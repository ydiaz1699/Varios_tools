#!/usr/bin/env python3
"""Prepare and validate inputs for reconstructing a documentary artifact.

The tool is intentionally deterministic.  It inventories the source project,
records evidence metadata without copying source bodies, and validates the
contract/guardrails of a spec produced by an LLM.  It does not infer the
semantic generation procedure, modify the source project, or promote output.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable

SCHEMA_VERSION = 1
SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".pio",
    "node_modules",
    "__pycache__",
    ".venv",
    "venv",
    "build",
    "dist",
    "coverage",
}
TEXT_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".h",
    ".hh",
    ".hpp",
    ".ino",
    ".ini",
    ".cfg",
    ".conf",
    ".cmake",
    ".json",
    ".md",
    ".markdown",
    ".py",
    ".rst",
    ".sh",
    ".bash",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".toml",
    ".txt",
    ".xml",
    ".svg",
    ".yml",
    ".yaml",
    ".properties",
    ".mk",
}
TEXT_FILENAMES = {
    "README",
    "README.md",
    "Dockerfile",
    "Makefile",
    "CMakeLists.txt",
    "platformio.ini",
    ".gitignore",
    ".env.example",
    "secrets.template",
}
SECRET_NAME_RE = re.compile(
    r"\b(password|passwd|secret|token|api[_-]?key|private[_-]?key|credential|ssid|access[_-]?key)\b",
    re.IGNORECASE,
)
SECRET_ASSIGNMENT_RE = re.compile(
    r"(?:[A-Za-z0-9]+[_-])*"
    r"(password|passwd|secret|token|api[_-]?key|private[_-]?key|credential|ssid|access[_-]?key)\b"
    r"\s*[:=]\s*(?!\s*(?:\[REDACTADO\]|\[redacted\]|\[[^\]]+\]|"
    r"<[^>]+>|__[^\n]+__|CHANGE_ME|TODO|PENDIENTE(?:_[A-Z]+)*|UNKNOWN|NONE|N/A|null|false|true)"
    r"(?=\s|[,}\"']|$))"
    r"[^\s,;}'\"]+",
    re.IGNORECASE,
)
HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$")
TAG_RE = re.compile(r"\b(TODO|FIXME|HACK|BUG|NOTE|WARN)\b", re.IGNORECASE)
INCLUDE_RE = re.compile(r"#\s*include\s*[<\"]([^>\"]+)[>\"]")
IMPORT_RE = re.compile(r"\b(?:from|import)\s+([A-Za-z_][A-Za-z0-9_./-]*)")
FILE_REF_RE = re.compile(
    r"(?:file|include|ref(?:erence)?|see)\s*[:=]?\s*([^\s,;()<>`]+)",
    re.IGNORECASE,
)
MARKER_NAMES = (
    "firmware",
    "platformio",
    "arduino",
    "embedded",
    "gpio",
    "wiring",
    "roadmap",
    "prompt",
    "template",
    "schema",
    "provenance",
    "evidence",
    "build",
    "test",
)
READ_STATES = {"COMPLETE", "PARTIAL", "MISSING", "UNREADABLE"}
CONTENT_CLASSES = {"REUSABLE", "PARAMETRIZABLE", "PRODUCT_SPECIFIC", "SENSITIVE", "MIXED"}
EVIDENCE_STATES = {"CONFIRMED", "INFERRED", "CONTRADICTED", "UNKNOWN", "LECTURA_INCOMPLETA"}
ARTIFACT_TYPES = {"roadmap", "file-map", "guide", "architecture", "changelog", "inventory", "other"}
REQUIRED_SPEC_FIELDS = {
    "schema_version",
    "recreator_id",
    "artifact_id",
    "artifact_type",
    "status",
    "purpose",
    "target_scope",
    "document_role",
    "snapshot",
    "source_project",
    "source_files",
    "document_inputs",
    "behavioral_contract",
    "reconstruction_steps",
    "generation_conditions",
    "omission_conditions",
    "conflicts_with_code",
    "output_artifacts",
    "verification",
    "promotion",
}


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def relative_or_absolute(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_text_file(path: Path) -> bool:
    if path.name in TEXT_FILENAMES or path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    try:
        with path.open("rb") as stream:
            sample = stream.read(8192)
    except OSError:
        return False
    return b"\x00" not in sample


def redact_label(value: str) -> str:
    """Keep structural labels while preventing secret-like assignments."""
    if SECRET_NAME_RE.search(value) or SECRET_ASSIGNMENT_RE.search(value):
        return "[REDACTED_METADATA]"
    return value.strip()


def classify_path(path: Path, relative: str) -> str:
    lower = relative.lower()
    name = path.name.lower()
    if "prompt" in name or "/prompts/" in lower or lower.startswith("prompts/"):
        return "prompt"
    if "template" in name or "/templates/" in lower or lower.startswith("templates/"):
        return "template"
    if name == "roadmap.md":
        return "roadmap"
    if name == "changelog.md":
        return "changelog"
    if name in {"decisions.md", "readme.md", "readme"}:
        return "reference"
    if "schema" in name:
        return "schema"
    if "audit" in name or "audit" in lower:
        return "audit"
    if path.suffix.lower() in {".c", ".cc", ".cpp", ".h", ".hh", ".hpp", ".ino", ".py", ".sh", ".bash", ".js", ".ts", ".tsx", ".jsx"}:
        return "source_code"
    if path.suffix.lower() in {".ini", ".cfg", ".conf", ".cmake", ".json", ".toml", ".xml", ".yml", ".yaml", ".properties", ".mk"}:
        return "configuration"
    if path.suffix.lower() in {".md", ".markdown", ".rst", ".txt"}:
        return "documentation"
    return "other"


def collect_files(root: Path) -> tuple[list[Path], list[dict[str, str]]]:
    files: list[Path] = []
    excluded: list[dict[str, str]] = []
    for current, directories, names in os.walk(root, followlinks=False):
        current_path = Path(current)
        kept: list[str] = []
        for directory in sorted(directories):
            if directory in SKIP_DIRS:
                excluded.append({"path": relative_or_absolute(current_path / directory, root), "reason": "excluded_directory"})
            else:
                kept.append(directory)
        directories[:] = kept
        files.extend(current_path / name for name in sorted(names))
    return sorted(files), excluded


def metadata_for_text(path: Path) -> dict[str, Any]:
    headings: list[dict[str, Any]] = []
    tags: list[dict[str, Any]] = []
    references: set[str] = set()
    markers: set[str] = set()
    secret_fields: set[str] = set()
    line_count = 0
    replacement_characters = 0
    max_line_length = 0
    try:
        with path.open("r", encoding="utf-8", errors="replace") as stream:
            for line_number, line in enumerate(stream, 1):
                line_count = line_number
                max_line_length = max(max_line_length, len(line.rstrip("\n")))
                replacement_characters += line.count("\ufffd")
                heading = HEADING_RE.match(line)
                if heading:
                    headings.append(
                        {
                            "level": len(heading.group(1)),
                            "title": redact_label(heading.group(2)),
                            "line": line_number,
                        }
                    )
                for match in TAG_RE.finditer(line):
                    tags.append({"tag": match.group(1).upper(), "line": line_number})
                for match in INCLUDE_RE.finditer(line):
                    references.add(redact_label(match.group(1)))
                for match in IMPORT_RE.finditer(line):
                    references.add(redact_label(match.group(1)))
                for match in FILE_REF_RE.finditer(line):
                    reference = match.group(1).strip("`[]<>")
                    if "/" in reference or "." in reference:
                        references.add(redact_label(reference))
                lower = line.lower()
                markers.update(marker for marker in MARKER_NAMES if marker in lower)
                for match in SECRET_NAME_RE.finditer(line):
                    secret_fields.add(match.group(1).lower().replace("-", "_"))
    except (OSError, UnicodeError) as exc:
        return {
            "read_state": "UNREADABLE",
            "read_error": type(exc).__name__,
            "line_count": 0,
            "headings": [],
            "tags": [],
            "references": [],
            "markers": [],
            "secret_fields": [],
            "replacement_characters": 0,
            "max_line_length": 0,
            "sensitive_content_present": False,
        }
    return {
        "read_state": "COMPLETE",
        "line_count": line_count,
        "headings": headings,
        "tags": tags,
        "references": sorted(references),
        "markers": sorted(markers),
        "secret_fields": sorted(secret_fields),
        "replacement_characters": replacement_characters,
        "max_line_length": max_line_length,
        "sensitive_content_present": bool(secret_fields) or bool(SECRET_ASSIGNMENT_RE.search(path.name)),
    }


def inventory_file(path: Path, root: Path) -> dict[str, Any]:
    relative = relative_or_absolute(path, root)
    try:
        size = path.stat().st_size
        digest = sha256_file(path)
    except OSError as exc:
        return {
            "path": relative,
            "file_kind": "unknown",
            "read_state": "UNREADABLE",
            "error_type": type(exc).__name__,
            "sensitive_content_present": False,
        }
    record: dict[str, Any] = {
        "path": relative,
        "bytes": size,
        "sha256": digest,
        "artifact_type": classify_path(path, relative),
        "sensitive_content_present": path.name.lower() in {".env", ".env.local", "secrets", "secrets.h", "credentials"},
    }
    if not is_text_file(path):
        record.update({"file_kind": "binary_or_unknown", "read_state": "BINARY_METADATA_ONLY"})
        return record
    record["file_kind"] = "text"
    record.update(metadata_for_text(path))
    return record


def resolve_source_path(raw: str, root: Path, label: str, must_exist: bool = True) -> Path:
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    if must_exist and not resolved.exists():
        raise ValueError(f"{label} does not exist: {raw}")
    return resolved


def validate_output_dir(output_dir: Path, source_root: Path) -> None:
    if is_within(output_dir, source_root):
        raise ValueError("output-dir must be outside PROJECT_ROOT")
    output_dir.mkdir(parents=True, exist_ok=True)


def source_record(path: Path, root: Path, role: str) -> dict[str, Any]:
    record = inventory_file(path, root)
    record["role"] = role
    return record


def artifact_summary(path: Path, root: Path, role: str) -> dict[str, Any]:
    record = source_record(path, root, role)
    if record.get("read_state") != "COMPLETE":
        raise ValueError(f"artifact must be read completely: {record.get('path')} ({record.get('read_state')})")
    return {
        "path": record["path"],
        "bytes": record.get("bytes", 0),
        "sha256": record.get("sha256", "UNAVAILABLE"),
        "line_count": record.get("line_count", 0),
        "headings": record.get("headings", []),
        "artifact_type": record.get("artifact_type", "documentation"),
        "read_state": record.get("read_state"),
        "sensitive_content_present": record.get("sensitive_content_present", False),
        "secret_fields": record.get("secret_fields", []),
        "role": role,
    }


def unique_paths(paths: Iterable[Path]) -> list[Path]:
    result: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = str(path.resolve())
        if key not in seen:
            seen.add(key)
            result.append(path.resolve())
    return result


def write_json(value: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def render_brief(manifest: dict[str, Any], prompt_path: Path, contract_path: Path) -> str:
    source = manifest["source"]
    coverage = manifest["coverage"]
    lines = [
        "# Brief de entrada para recreación documental",
        "",
        "Este brief contiene metadatos preparados determinísticamente. El LLM debe leer las fuentes directamente desde `project_root`; este archivo no contiene cuerpos de código ni documentos.",
        "",
        "## Parámetros",
        f"- Proyecto fuente: `{source['project_root']}`",
        f"- Target: `{source['target_id']}`",
        f"- Snapshot: `{source['snapshot']}`",
        f"- Artefacto: `{source['artifact_path']}`",
        f"- Directorio de salida: `{source['output_dir']}`",
        "",
        "## Cobertura",
        f"- Archivos descubiertos: `{coverage['files_discovered']}`",
        f"- Archivos de texto leídos completos: `{coverage['text_files_read']}`",
        f"- Binarios registrados solo como metadata: `{coverage['binary_metadata_only']}`",
        f"- Errores de lectura: `{coverage['read_errors']}`",
        f"- Estado: **{coverage['read_status']}**",
        "",
        "## Fuentes que el LLM debe leer",
        f"- Prompt de procedimiento: `{prompt_path}`",
        f"- Contrato JSON: `{contract_path}`",
        f"- Manifiesto de entrada: `{source['manifest_path']}`",
        "- Proyecto fuente completo, especialmente el artefacto, el código/configuración relacionado, prompts existentes y baselines indicados.",
        "",
        "## Guardrails",
        "- No copiar cuerpos de firmware, documentos, secretos ni valores de producto.",
        "- Redactar nombres y valores sensibles; conservar solo categorías y metadatos necesarios.",
        "- Marcar `LECTURA_INCOMPLETA` cuando una fuente necesaria no se haya leído completa.",
        "- Escribir las tres salidas (`recreator-spec.json`, `recreator-prompt.md`, `review.md`) fuera del proyecto fuente.",
        "- Mantener `promotion_allowed: false` y `review_required: true`.",
        "",
        "## Archivos registrados",
    ]
    for item in manifest["files"]:
        state = item.get("read_state", "UNKNOWN")
        kind = item.get("file_kind", "unknown")
        lines.append(f"- `{item['path']}` — {kind}, {state}, {item.get('bytes', 0)} bytes")
    lines.extend(
        [
            "",
            "El análisis semántico y la inferencia del contrato siguen siendo responsabilidad del LLM y requieren revisión humana.",
        ]
    )
    return "\n".join(lines) + "\n"


def command_prepare(args: argparse.Namespace) -> int:
    root = Path(args.project_root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"PROJECT_ROOT is not a directory: {root}")
    output_dir = Path(args.output_dir).expanduser().resolve()
    validate_output_dir(output_dir, root)

    artifact_path = resolve_source_path(args.artifact, root, "artifact")
    if not is_within(artifact_path, root):
        raise ValueError("artifact must be inside PROJECT_ROOT")
    if not artifact_path.is_file():
        raise ValueError("artifact must be a regular file")

    prompt_paths = []
    for raw in args.prompt or []:
        prompt_path = resolve_source_path(raw, root, "prompt")
        if not prompt_path.is_file():
            raise ValueError(f"prompt must be a regular file: {raw}")
        prompt_paths.append(prompt_path)
    baseline_paths = []
    for raw in args.baseline or []:
        baseline_path = resolve_source_path(raw, root, "baseline")
        baseline_paths.append(baseline_path)

    paths, excluded = collect_files(root)
    files = [inventory_file(path, root) for path in paths]
    read_errors = [item for item in files if item.get("read_state") == "UNREADABLE"]
    text_files = [item for item in files if item.get("read_state") == "COMPLETE"]
    binary_files = [item for item in files if item.get("read_state") == "BINARY_METADATA_ONLY"]
    artifact = artifact_summary(artifact_path, root, "reference_document")
    artifact_source_path = artifact["path"]
    if artifact_source_path not in {item.get("path") for item in files}:
        raise ValueError("artifact was not included in the project inventory")

    additional_sources = [source_record(path, root, "existing_prompt") for path in prompt_paths]
    external_baselines = [source_record(path, root, "baseline") for path in baseline_paths if path.is_file()]
    incomplete_paths = [
        item["path"]
        for item in files
        if item.get("read_state") == "UNREADABLE"
    ]
    artifact_complete = artifact.get("read_state") == "COMPLETE"
    read_status = "LECTURA_INCOMPLETA" if read_errors else "COMPLETA_CON_BINARIOS_EN_METADATA"

    manifest_path = output_dir / "recreator-input.json"
    manifest: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "kind": "recreator-input",
        "source": {
            "project_root": str(root),
            "target_id": args.target_id or artifact_path.stem,
            "snapshot": args.snapshot,
            "purpose": args.purpose,
            "artifact_path": artifact_source_path,
            "output_dir": str(output_dir),
            "manifest_path": str(manifest_path),
            "existing_prompt_paths": [item["path"] for item in additional_sources],
            "baseline_paths": [relative_or_absolute(path, root) for path in baseline_paths],
        },
        "artifact": artifact,
        "files": files,
        "additional_sources": additional_sources + external_baselines,
        "excluded_directories": excluded,
        "coverage": {
            "files_discovered": len(files),
            "text_files_read": len(text_files),
            "binary_metadata_only": len(binary_files),
            "read_errors": len(read_errors),
            "incomplete_paths": incomplete_paths,
            "artifact_read_complete": artifact_complete,
            "read_status": read_status,
        },
        "llm_contract": {
            "procedure_prompt": str((Path(__file__).resolve().parents[1] / "prompts" / "generar-especificacion-recreador.md")),
            "spec_contract": str((Path(__file__).resolve().parents[1] / "references" / "recreator-spec-contract.md")),
            "required_outputs": ["recreator-spec.json", "recreator-prompt.md", "review.md"],
            "semantic_inference": "LLM_AND_HUMAN_REVIEW",
            "promotion_allowed": False,
            "review_required": True,
        },
        "guardrails": {
            "source_modified": False,
            "source_bodies_embedded": False,
            "secret_values_embedded": False,
            "output_outside_source_project": not is_within(output_dir, root),
            "promotion_allowed": False,
            "review_required": True,
        },
        "note": "Metadata-only preparation. Read the source files directly; this manifest does not replace complete reading or semantic review.",
    }
    write_json(manifest, manifest_path)
    brief_path = output_dir / "recreator-brief.md"
    brief_path.write_text(
        render_brief(manifest, Path(manifest["llm_contract"]["procedure_prompt"]), Path(manifest["llm_contract"]["spec_contract"])),
        encoding="utf-8",
    )
    print(json.dumps({"manifest": str(manifest_path), "brief": str(brief_path), "coverage": manifest["coverage"]}, ensure_ascii=False, indent=2))
    return 0


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON {path}: {exc}") from exc


def add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_evidence_list(value: Any, location: str, errors: list[str]) -> None:
    if not isinstance(value, list):
        add_error(errors, f"{location} must be a list")
        return
    for index, evidence in enumerate(value):
        if not isinstance(evidence, (str, dict)):
            add_error(errors, f"{location}[{index}] must be a string or object")


def validate_spec(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["spec must be a JSON object"]
    missing = sorted(REQUIRED_SPEC_FIELDS - set(value))
    errors.extend(f"missing required field: {field}" for field in missing)
    if value.get("schema_version") != SCHEMA_VERSION:
        add_error(errors, f"schema_version must be {SCHEMA_VERSION}")
    if value.get("artifact_type") not in ARTIFACT_TYPES:
        add_error(errors, f"unsupported artifact_type: {value.get('artifact_type')}")
    if not isinstance(value.get("target_scope"), list):
        add_error(errors, "target_scope must be a list")
    for field in ("source_files", "document_inputs", "reconstruction_steps", "generation_conditions", "omission_conditions", "conflicts_with_code", "output_artifacts"):
        if not isinstance(value.get(field), list):
            add_error(errors, f"{field} must be a list")
    if not isinstance(value.get("behavioral_contract"), dict):
        add_error(errors, "behavioral_contract must be an object")
    if not isinstance(value.get("verification"), dict):
        add_error(errors, "verification must be an object")
    if not isinstance(value.get("promotion"), dict):
        add_error(errors, "promotion must be an object")

    promotion = value.get("promotion")
    if isinstance(promotion, dict):
        if promotion.get("promotion_allowed") is not False:
            add_error(errors, "promotion.promotion_allowed must be false")
        if promotion.get("review_required") is not True:
            add_error(errors, "promotion.review_required must be true")
        if promotion.get("approved_by") not in (None, "") or promotion.get("approved_at") not in (None, ""):
            add_error(errors, "promotion approval fields must remain null/empty")

    verification = value.get("verification")
    if isinstance(verification, dict):
        if verification.get("sensitive_values_redacted") is not True:
            add_error(errors, "verification.sensitive_values_redacted must be true")
        if verification.get("human_review") != "REQUIRED":
            add_error(errors, "verification.human_review must be REQUIRED")
        incomplete_files = verification.get("incomplete_files", [])
        if not isinstance(incomplete_files, list):
            add_error(errors, "verification.incomplete_files must be a list")
        if verification.get("read_complete") is True and incomplete_files:
            add_error(errors, "read_complete cannot be true when incomplete_files is non-empty")

    source_files = value.get("source_files")
    if isinstance(source_files, list):
        for index, item in enumerate(source_files):
            location = f"source_files[{index}]"
            if not isinstance(item, dict):
                add_error(errors, f"{location} must be an object")
                continue
            for field in ("path", "read_state", "content_class"):
                if field not in item:
                    add_error(errors, f"{location} missing: {field}")
            if item.get("read_state") not in READ_STATES:
                add_error(errors, f"{location}.read_state has unsupported value: {item.get('read_state')}")
            if item.get("content_class") not in CONTENT_CLASSES:
                add_error(errors, f"{location}.content_class has unsupported value: {item.get('content_class')}")
            if item.get("sensitive_content_present") is True and item.get("content_class") not in {"SENSITIVE", "MIXED", "PRODUCT_SPECIFIC"}:
                add_error(errors, f"{location} marks sensitive content but is not classified as sensitive/mixed/product-specific")

    for field in ("generation_conditions", "omission_conditions"):
        items = value.get(field)
        if not isinstance(items, list):
            continue
        for index, item in enumerate(items):
            location = f"{field}[{index}]"
            if not isinstance(item, dict):
                add_error(errors, f"{location} must be an object")
                continue
            if "evidence" not in item:
                add_error(errors, f"{location} missing evidence")
            else:
                validate_evidence_list(item["evidence"], f"{location}.evidence", errors)
            if item.get("state") not in EVIDENCE_STATES:
                add_error(errors, f"{location}.state has unsupported value: {item.get('state')}")

    claims = value.get("claims", [])
    if claims is not None:
        if not isinstance(claims, list):
            add_error(errors, "claims must be a list")
        else:
            for index, claim in enumerate(claims):
                location = f"claims[{index}]"
                if not isinstance(claim, dict):
                    add_error(errors, f"{location} must be an object")
                    continue
                if not claim.get("evidence"):
                    add_error(errors, f"{location} must have evidence")
                if claim.get("state") not in EVIDENCE_STATES:
                    add_error(errors, f"{location}.state has unsupported value: {claim.get('state')}")
                validate_evidence_list(claim.get("evidence", []), f"{location}.evidence", errors)

    outputs = value.get("output_artifacts")
    if isinstance(outputs, list):
        output_names = {str(item.get("path")) for item in outputs if isinstance(item, dict)}
        for required in {"recreator-spec.json", "recreator-prompt.md", "review.md"}:
            if required not in output_names:
                add_error(errors, f"output_artifacts missing required output: {required}")
        for index, item in enumerate(outputs):
            if not isinstance(item, dict):
                add_error(errors, f"output_artifacts[{index}] must be an object")
                continue
            output_path = str(item.get("path", ""))
            if Path(output_path).is_absolute() or "PROJECT_ROOT" in output_path or "project_root" in output_path.lower():
                add_error(errors, f"output_artifacts[{index}].path must be a generic relative path")
            if item.get("promotion_allowed") is not False:
                add_error(errors, f"output_artifacts[{index}].promotion_allowed must be false")

    serialized = json.dumps(value, ensure_ascii=False)
    if SECRET_ASSIGNMENT_RE.search(serialized):
        add_error(errors, "spec appears to contain an unredacted secret-like assignment")
    if re.search(r"(?i)(?:private[_-]?key|api[_-]?key)\s*[:=]\s*-----BEGIN", serialized):
        add_error(errors, "spec appears to contain a private key body")
    return errors


def command_validate_spec(args: argparse.Namespace) -> int:
    path = Path(args.spec).expanduser().resolve()
    value = load_json(path)
    errors = validate_spec(value)
    report = {
        "schema_version": SCHEMA_VERSION,
        "kind": "recreator-spec-validation",
        "spec": str(path),
        "decision": "PASS" if not errors else "FAIL",
        "errors": errors,
        "promotion_allowed": False,
        "note": "Static contract and guardrail validation; semantic approval remains pending human review.",
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepara y valida especificaciones de recreadores documentales sin copiar contenido ni promocionar artefactos.")
    sub = parser.add_subparsers(dest="command", required=True)

    prepare = sub.add_parser("prepare", help="inventariar un proyecto y preparar metadata/brief para el LLM")
    prepare.add_argument("project_root", metavar="PROJECT_ROOT")
    prepare.add_argument("--artifact", required=True, help="ruta relativa o absoluta del documento de referencia")
    prepare.add_argument("--output-dir", required=True, help="directorio de salida; debe estar fuera de PROJECT_ROOT")
    prepare.add_argument("--target-id", help="identificador estable del artefacto")
    prepare.add_argument("--snapshot", default="UNKNOWN")
    prepare.add_argument("--purpose", default="reconstruir un generador documental parametrizable")
    prepare.add_argument("--prompt", action="append", help="prompt existente relacionado; puede repetirse")
    prepare.add_argument("--baseline", action="append", help="baseline documental relacionado; puede repetirse")
    prepare.set_defaults(func=command_prepare)

    validate = sub.add_parser("validate-spec", help="validar un recreator-spec.json sin aprobarlo")
    validate.add_argument("spec", metavar="SPEC_PATH")
    validate.set_defaults(func=command_validate_spec)
    return parser


def main() -> int:
    try:
        args = build_parser().parse_args()
        return args.func(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
