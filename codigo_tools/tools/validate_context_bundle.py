#!/usr/bin/env python3
"""Validate a project-context bundle without modifying its inputs.

The validator is intentionally deterministic and conservative. It checks the
minimum PROJECT_CONTEXT entry point, local Markdown links, obvious unredacted
secret assignments, and optional project-wiring references. It does not infer
hardware facts, run builds, install dependencies, or promote catalog entries.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SECRET_ASSIGNMENT_RE = re.compile(
    r"(?i)\b(password|passwd|token|secret|api[_-]?key|ssid|private[_-]?key)\b"
    r"\s*[:=]\s*([^\s|,;]+)"
)
PLACEHOLDER_RE = re.compile(
    r"^(?:\[[^\]]+\]|\$\{[^}]+\}|<[^>]+>|(?:REDACTED|REDACTADO|PRESENTE_NO_EXHIBIDO|"
    r"PENDIENTE(?:_DE_[A-Z_]+)?|UNKNOWN|NONE|N/A|TODO)(?:$|\b))",
    re.IGNORECASE,
)

REQUIRED_PROJECT_FILES = (".ai/PROJECT_CONTEXT.md",)
DEFAULT_SHARED_FILES = ("shared/CODING_STYLE.md", "shared/SOFTWARE.md")


def _json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


def write_report(report: dict[str, Any], output: Path | None) -> None:
    payload = json.dumps(_json_safe(report), indent=2, ensure_ascii=False) + "\n"
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


def resolve_project_root(value: str | Path) -> Path:
    path = Path(value).expanduser().resolve()
    if path.name == ".ai":
        return path.parent
    if path.is_file() and path.name == "PROJECT_CONTEXT.md":
        return path.parent.parent
    return path


def discover_shared_root(project_root: Path, explicit: str | None) -> Path | None:
    if explicit:
        return Path(explicit).expanduser().resolve()
    candidates = (
        project_root / "shared",
        project_root.parent / "shared",
        project_root.parent.parent / "shared",
    )
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    return None


def load_manifest(project_root: Path) -> tuple[dict[str, Any] | None, Path | None]:
    candidates = (
        project_root / "project-context-bundle-manifest.json",
        project_root.parent / "project-context-bundle-manifest.json",
        project_root.parent.parent / "project-context-bundle-manifest.json",
    )
    for path in candidates:
        if path.is_file():
            try:
                return json.loads(path.read_text(encoding="utf-8")), path
            except (OSError, json.JSONDecodeError):
                return None, path
    return None, None


def markdown_files(project_root: Path, shared_root: Path | None) -> list[Path]:
    files: list[Path] = []
    ai_root = project_root / ".ai"
    if ai_root.is_dir():
        files.extend(sorted(ai_root.glob("*.md")))
    if shared_root and shared_root.is_dir():
        files.extend(sorted(shared_root.glob("*.md")))
    return files


def relative_display(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def validate_links(files: Iterable[Path]) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    for source in files:
        try:
            text = source.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append({"source": str(source), "error": f"cannot_read: {exc}"})
            continue
        for target in MARKDOWN_LINK_RE.findall(text):
            target = target.strip().split("#", 1)[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            target_path = (source.parent / target).resolve()
            if not target_path.exists():
                errors.append(
                    {
                        "source": str(source),
                        "target": target,
                        "error": "local_link_not_found",
                    }
                )
    return errors


def is_safe_secret_value(value: str) -> bool:
    value = value.strip().strip("'\"")
    if not value:
        return True
    if PLACEHOLDER_RE.match(value):
        return True
    if value.upper() in {"TRUE", "FALSE", "NULL", "NONE"}:
        return True
    return False


def find_secret_findings(files: Iterable[Path]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for source in files:
        try:
            lines = source.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for number, line in enumerate(lines, 1):
            if "[REDACTADO]" in line or "[REDACTED]" in line:
                continue
            for match in SECRET_ASSIGNMENT_RE.finditer(line):
                value = match.group(2).rstrip("`)")
                if not is_safe_secret_value(value):
                    findings.append(
                        {
                            "source": str(source),
                            "line": number,
                            "field": match.group(1),
                            "value": "[REDACTADO]",
                            "error": "possible_unredacted_secret_assignment",
                        }
                    )
    return findings


def read_text(path: Path) -> tuple[str | None, str | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except (OSError, UnicodeDecodeError) as exc:
        return None, str(exc)


def validate_bundle(
    project_root: Path, shared_root: Path | None, output: Path | None
) -> int:
    errors: list[dict[str, Any]] = []
    warnings: list[dict[str, Any]] = []
    project_root = project_root.resolve()
    shared_root = shared_root.resolve() if shared_root else None

    if not project_root.is_dir():
        errors.append({"path": str(project_root), "error": "project_root_not_found"})

    manifest, manifest_path = load_manifest(project_root)
    required = list(REQUIRED_PROJECT_FILES)
    shared_files = list(DEFAULT_SHARED_FILES)
    if manifest:
        required = list(manifest.get("required_project_files", required))
        shared_files = list(manifest.get("shared_files", shared_files))
    elif manifest_path:
        errors.append({"path": str(manifest_path), "error": "invalid_manifest"})

    project_files: list[Path] = []
    for relative in required:
        path = project_root / relative
        if not path.is_file():
            errors.append({"path": str(path), "error": "required_file_not_found"})
        else:
            project_files.append(path)

    if shared_root:
        for relative in shared_files:
            filename = Path(relative).name
            path = shared_root / filename
            if not path.is_file():
                warnings.append({"path": str(path), "error": "shared_file_not_found"})
            else:
                project_files.append(path)
    else:
        warnings.append({"error": "shared_root_not_found"})

    ai_root = project_root / ".ai"
    if ai_root.is_dir():
        optional_count = len(list(ai_root.glob("*.md")))
        if optional_count == 0:
            warnings.append({"path": str(ai_root), "error": "no_context_documents_found"})
    else:
        errors.append({"path": str(ai_root), "error": "project_ai_directory_not_found"})

    files = markdown_files(project_root, shared_root)
    errors.extend(validate_links(files))
    secret_findings = find_secret_findings(files)
    if secret_findings:
        errors.extend(secret_findings)

    placeholders = 0
    for path in files:
        text, error = read_text(path)
        if error:
            continue
        placeholders += len(re.findall(r"\[[A-Z][A-Z0-9_ /|-]{2,}\]", text or ""))
    if placeholders:
        warnings.append(
            {
                "error": "template_placeholders_present",
                "count": placeholders,
                "note": "expected for an unfilled scaffold; review before promotion",
            }
        )

    if errors:
        decision = "FAIL"
    elif warnings:
        decision = "PASS_WITH_WARNINGS"
    else:
        decision = "PASS"

    report = {
        "tool": "validate_context_bundle.py",
        "command": "validate",
        "project_root": project_root,
        "shared_root": shared_root,
        "manifest": manifest_path,
        "decision": decision,
        "errors": errors,
        "warnings": warnings,
        "files_checked": [str(path) for path in files],
        "secret_findings": len(secret_findings),
        "promotion_allowed": False,
        "auto_apply": False,
        "review_required": True,
    }
    write_report(report, output)
    return 1 if errors else 0


def iter_reference_values(value: Any, path: str = "") -> Iterable[tuple[str, str]]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield from iter_reference_values(child, f"{path}.{key}" if path else str(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from iter_reference_values(child, f"{path}[{index}]")
    elif isinstance(value, str) and ("boards/" in value or "peripherals/" in value):
        yield path, value


def catalog_gap(project_root: Path, catalog_root: Path, output: Path | None) -> int:
    wiring = project_root / "project-wiring.json"
    gaps: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []
    references: list[dict[str, str]] = []

    if not wiring.is_file():
        warnings.append(
            {
                "path": str(wiring),
                "error": "project_wiring_not_found",
                "note": "no gap can be resolved without a wiring manifest",
            }
        )
    else:
        try:
            data = json.loads(wiring.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            gaps.append({"path": str(wiring), "error": f"invalid_project_wiring: {exc}"})
        else:
            for field, reference in iter_reference_values(data):
                reference_path = (catalog_root / reference).resolve()
                item = {"field": field, "reference": reference, "resolved": str(reference_path)}
                if reference_path.is_file():
                    references.append({**item, "status": "FOUND"})
                else:
                    gaps.append({**item, "status": "MISSING"})

    decision = "GAPS_FOUND" if gaps else ("NO_WIRING" if not wiring.is_file() else "NO_GAPS")
    report = {
        "tool": "validate_context_bundle.py",
        "command": "catalog-gap",
        "project_root": project_root.resolve(),
        "catalog_root": catalog_root.resolve(),
        "wiring": wiring,
        "decision": decision,
        "references": references,
        "gaps": gaps,
        "warnings": warnings,
        "promotion_allowed": False,
        "auto_apply": False,
        "review_required": True,
    }
    write_report(report, output)
    return 1 if gaps else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="validate a context bundle")
    validate.add_argument("project_root", help="project root, .ai directory, or PROJECT_CONTEXT.md")
    validate.add_argument("--shared-root", help="optional shared directory")
    validate.add_argument("--output", type=Path, help="write JSON report outside the input")

    gap = subparsers.add_parser("catalog-gap", help="report missing catalog references")
    gap.add_argument("project_root", help="project root containing project-wiring.json")
    gap.add_argument("--catalog-root", required=True, help="catalog root containing boards/ and peripherals/")
    gap.add_argument("--output", type=Path, help="write JSON report outside the input")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "validate":
        return validate_bundle(
            resolve_project_root(args.project_root),
            discover_shared_root(resolve_project_root(args.project_root), args.shared_root),
            args.output,
        )
    if args.command == "catalog-gap":
        return catalog_gap(
            resolve_project_root(args.project_root),
            Path(args.catalog_root).expanduser().resolve(),
            args.output,
        )
    raise AssertionError(f"unknown command: {args.command}")


if __name__ == "__main__":
    sys.exit(main())
