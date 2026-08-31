#!/usr/bin/env python3
"""Validate a project context bundle without modifying or promoting artifacts.

The validator checks the canonical minimum (`.ai/PROJECT_CONTEXT.md`), resolves
Markdown links, detects likely unredacted secret assignments, and reports basic
catalog gaps from an optional `project-wiring.json`. It is intentionally static:
it does not build firmware, edit the project, create catalog entries, or infer
physical wiring from source code.
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    from hardware_catalog import load, resolve_ref, check_project
except ImportError:  # pragma: no cover - supports importing the file directly
    load = None  # type: ignore[assignment]
    resolve_ref = None  # type: ignore[assignment]
    check_project = None  # type: ignore[assignment]

MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SECRET_ASSIGNMENT_RE = re.compile(
    r"\b(?:password|passwd|secret|token|api[_-]?key|private[_-]?key|ssid)\b"
    r"\s*[:=]\s*(?!\[REDACTADO\]|\[[^\]]+\]|<[^>]+>|__[^\n]+__|"
    r"PENDIENTE(?:_DE_CONFIRMAR|_DE_VERIFICAR)?\b|N/A\b|CHANGE_ME\b)",
    re.IGNORECASE,
)
REQUIRED_CONTEXT_HEADINGS = (
    "Propósito y alcance",
    "Entradas y puntos de entrada",
    "Referencias de hardware y documentos",
    "Archivos clave",
    "Verificación",
    "Pendientes y contradicciones",
)
BUILD_MARKERS = (
    "platformio.ini",
    "CMakeLists.txt",
    "package.json",
    "pyproject.toml",
    "Makefile",
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def add_issue(report: dict[str, Any], severity: str, code: str, message: str, path: str | None = None) -> None:
    report["issues"].append({"severity": severity, "code": code, "message": message, "path": path})


def validate_links(root: Path, report: dict[str, Any]) -> None:
    for path in sorted((root / ".ai").rglob("*.md")):
        try:
            text = read_text(path)
        except OSError as exc:
            add_issue(report, "error", "READ_ERROR", f"no se pudo leer el archivo: {exc}", str(path.relative_to(root)))
            continue
        for raw_target in MARKDOWN_LINK_RE.findall(text):
            target = raw_target.strip().split("#", 1)[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "<")):
                continue
            target_path = (path.parent / target).resolve()
            try:
                target_path.relative_to(root.resolve())
            except ValueError:
                add_issue(report, "error", "LINK_OUTSIDE_ROOT", "enlace fuera de la raíz del proyecto", str(path.relative_to(root)))
                continue
            report["checks"]["links_checked"] += 1
            if not target_path.exists():
                add_issue(report, "error", "BROKEN_LINK", f"referencia no resoluble: {target}", str(path.relative_to(root)))


def validate_secrets(root: Path, report: dict[str, Any]) -> None:
    for path in sorted((root / ".ai").rglob("*.md")):
        try:
            lines = read_text(path).splitlines()
        except OSError:
            continue
        for line_number, line in enumerate(lines, 1):
            if SECRET_ASSIGNMENT_RE.search(line):
                add_issue(
                    report,
                    "error",
                    "SECRET_LIKE_ASSIGNMENT",
                    "asignación con nombre de secreto no parece redactada; revisar sin imprimir su valor",
                    f"{path.relative_to(root)}:{line_number}",
                )


def validate_context_file(root: Path, report: dict[str, Any]) -> None:
    context_path = root / ".ai" / "PROJECT_CONTEXT.md"
    report["checks"]["project_context_exists"] = context_path.exists()
    if not context_path.exists():
        add_issue(report, "error", "MISSING_PROJECT_CONTEXT", "falta .ai/PROJECT_CONTEXT.md")
        return
    try:
        text = read_text(context_path)
    except OSError as exc:
        add_issue(report, "error", "READ_ERROR", f"no se pudo leer PROJECT_CONTEXT.md: {exc}", ".ai/PROJECT_CONTEXT.md")
        return
    for heading in REQUIRED_CONTEXT_HEADINGS:
        if f"## {heading}" not in text:
            add_issue(report, "error", "MISSING_CONTEXT_SECTION", f"falta la sección requerida: {heading}", ".ai/PROJECT_CONTEXT.md")
    report["checks"]["context_sections_checked"] = len(REQUIRED_CONTEXT_HEADINGS)


def validate_conditions(root: Path, report: dict[str, Any], strict: bool) -> None:
    ai = root / ".ai"
    if not ai.exists():
        return
    conditions: list[tuple[bool, str, str]] = []
    has_wiring = (root / "project-wiring.json").exists()
    has_build = any((root / marker).exists() for marker in BUILD_MARKERS)
    has_tests = (root / "test").exists() or (root / "tests").exists()
    conditions.extend([
        (has_wiring, "HARDWARE.md", "project-wiring.json existe"),
        (has_build, "SOFTWARE.md", "se detectó configuración de build"),
        (has_tests, "TESTING.md", "se detectó directorio de tests"),
    ])
    for applies, filename, reason in conditions:
        if applies and not (ai / filename).exists():
            severity = "error" if strict else "warning"
            add_issue(report, severity, "CONDITIONAL_FILE_MISSING", f"falta .ai/{filename}; condición: {reason}", ".ai")


def catalog_files(catalog_root: Path, collection: str) -> list[Path]:
    return sorted((catalog_root / collection).rglob("*.json")) if (catalog_root / collection).exists() else []


def suggest_refs(ref: str, catalog_root: Path, collection: str) -> list[str]:
    candidates: list[str] = []
    query = ref.rsplit("/", 1)[-1].removesuffix(".json").lower()
    for path in catalog_files(catalog_root, collection):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        values = [str(data.get("id", "")), str(data.get("name", "")), *[str(item) for item in data.get("aliases", [])]]
        score = max((difflib.SequenceMatcher(None, query, value.lower()).ratio() for value in values if value), default=0.0)
        if score >= 0.45:
            candidates.append(str(path.relative_to(catalog_root)))
    return candidates[:5]


def catalog_gap_report(wiring_path: Path, catalog_root: Path) -> dict[str, Any]:
    if load is None or resolve_ref is None:
        return {"decision": "NO_DECIDIBLE", "error": "no se pudo cargar hardware_catalog.py"}
    wiring = load(wiring_path)
    missing: list[dict[str, Any]] = []
    board_ref = str(wiring.get("board_ref", ""))
    if resolve_ref(board_ref, catalog_root, "boards")[1] is None:
        missing.append({"kind": "board", "ref": board_ref, "suggestions": suggest_refs(board_ref, catalog_root, "boards")})
    for item in wiring.get("peripherals", []):
        if not isinstance(item, dict):
            continue
        ref = str(item.get("ref", ""))
        if resolve_ref(ref, catalog_root, "peripherals")[1] is None:
            missing.append({"kind": "peripheral", "instance": item.get("instance"), "ref": ref, "suggestions": suggest_refs(ref, catalog_root, "peripherals")})
    return {
        "schema_version": 1,
        "kind": "catalog-gap-report",
        "wiring": str(wiring_path),
        "catalog_root": str(catalog_root),
        "decision": "GAPS_FOUND" if missing else "NO_GAPS",
        "missing": missing,
        "promotion_allowed": False,
        "note": "Este informe detecta referencias faltantes; no crea ni publica fichas.",
    }


def validate_bundle(root: Path, catalog_root: Path, strict: bool) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema_version": 1,
        "kind": "project-context-bundle-validation",
        "project_root": str(root),
        "decision": "PASS",
        "promotion_allowed": False,
        "checks": {"project_context_exists": False, "context_sections_checked": 0, "links_checked": 0},
        "issues": [],
        "catalog_gap": None,
        "note": "Validación estática; no demuestra build, tests ni cableado físico.",
    }
    if not (root / ".ai").is_dir():
        add_issue(report, "error", "MISSING_AI_DIRECTORY", "falta el directorio .ai")
    else:
        validate_context_file(root, report)
        validate_links(root, report)
        validate_secrets(root, report)
        validate_conditions(root, report, strict)
    wiring_path = root / "project-wiring.json"
    if wiring_path.exists():
        report["catalog_gap"] = catalog_gap_report(wiring_path, catalog_root)
        if check_project is not None:
            try:
                project_report = check_project(wiring_path, catalog_root)
                report["wiring_validation"] = {
                    "decision": project_report.get("decision"),
                    "errors": project_report.get("errors", []),
                    "warnings": project_report.get("warnings", []),
                }
                for message in project_report.get("errors", []):
                    add_issue(report, "error", "WIRING_INVALID", message, "project-wiring.json")
                for message in project_report.get("warnings", []):
                    add_issue(report, "warning", "WIRING_WARNING", message, "project-wiring.json")
            except (OSError, ValueError, KeyError, TypeError) as exc:
                add_issue(report, "error", "WIRING_CHECK_ERROR", f"no se pudo validar wiring: {exc}", "project-wiring.json")
    if any(item["severity"] == "error" for item in report["issues"]):
        report["decision"] = "FAIL"
    elif any(item["severity"] == "warning" for item in report["issues"]):
        report["decision"] = "PASS_CON_ADVERTENCIAS"
    return report


def emit(report: dict[str, Any], output: str | None) -> None:
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if output:
        Path(output).write_text(text, encoding="utf-8")
    print(text, end="")


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida bundles .ai y reporta gaps de catálogo sin promocionar artefactos.")
    sub = parser.add_subparsers(dest="command", required=True)
    validate_parser = sub.add_parser("validate", help="validar el bundle de un proyecto")
    validate_parser.add_argument("project_root")
    validate_parser.add_argument("--catalog-root", default="catalog")
    validate_parser.add_argument("--strict-conditions", action="store_true")
    validate_parser.add_argument("--output")
    gap_parser = sub.add_parser("catalog-gap", help="reportar referencias de wiring ausentes del catálogo")
    gap_parser.add_argument("wiring")
    gap_parser.add_argument("--catalog-root", default="catalog")
    gap_parser.add_argument("--output")
    args = parser.parse_args()
    try:
        if args.command == "validate":
            report = validate_bundle(Path(args.project_root).resolve(), Path(args.catalog_root).resolve(), args.strict_conditions)
        else:
            report = catalog_gap_report(Path(args.wiring).resolve(), Path(args.catalog_root).resolve())
        emit(report, args.output)
        return 0 if report.get("decision") not in {"FAIL", "GAPS_FOUND", "NO_DECIDIBLE"} else 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
