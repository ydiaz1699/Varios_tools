#!/usr/bin/env python3
"""Scan a project and build a reviewable reusable-material plan.

This tool deliberately extracts metadata, patterns and evidence locations instead
of copying source contents. It is a planning aid; it does not promote artifacts,
modify the source project or replace semantic human/LLM review.
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
}
CODE_EXTENSIONS = {".c", ".cc", ".cpp", ".h", ".hpp", ".ino", ".py", ".sh", ".bash", ".js", ".ts", ".tsx", ".jsx"}
CONFIG_EXTENSIONS = {".ini", ".cfg", ".conf", ".cmake", ".json", ".toml", ".xml", ".yml", ".yaml", ".properties", ".mk"}
DECISIONS = {
    "NUEVO",
    "MEJORA",
    "DUPLICADO",
    "CONTRADICTORIO",
    "VARIANTE",
    "NO_DECIDIBLE",
    "FUERA_DE_ALCANCE",
}
SCOPE_VALUES = {"REUSABLE", "PARAMETRIZABLE", "PRODUCT_SPECIFIC", "SENSITIVE"}

TAG_RE = re.compile(r"\b(TODO|FIXME|HACK|BUG|NOTE|WARN)\b", re.IGNORECASE)
HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$")
INCLUDE_RE = re.compile(r"#\s*include\s*[<\"]([^>\"]+)[>\"]")
IMPORT_RE = re.compile(r"\b(?:from|import)\s+([A-Za-z_][A-Za-z0-9_./-]*)")
FILE_REF_RE = re.compile(
    r"(?:file|include|ref(?:erence)?|see)\s*[:=]?\s*([^\s,;()<>`]+)",
    re.IGNORECASE,
)
SECRET_RE = re.compile(
    r"\b(password|passwd|secret|token|api[_-]?key|private[_-]?key|credential|ssid)\b\s*[:=]",
    re.IGNORECASE,
)
PLACEHOLDER_RE = re.compile(r"(?:\[REDACTADO\]|\[.*?\]|__[^\n]+__|CHANGE_ME|TODO|YOUR_|example|placeholder)", re.IGNORECASE)
TECHNICAL_MARKERS = {
    "platformio",
    "arduino",
    "embedded",
    "firmware",
    "board",
    "peripheral",
    "wiring",
    "gpio",
    "interrupt",
    "digitalpintointerrupt",
    "schema",
    "provenance",
    "evidence",
    "catalog",
    "shared",
    "project_context",
    "decisions",
    "roadmap",
    "changelog",
    "skill",
    "copilot",
    "watchdog",
    "timeout",
    "retry",
    "rccswitch",
    "rf433",
}


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


def safe_relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def tokens(value: Iterable[str] | str) -> set[str]:
    text = " ".join(value) if not isinstance(value, str) else value
    return {
        token
        for token in re.findall(r"[a-z0-9][a-z0-9_-]{2,}", text.lower())
        if token not in {"the", "and", "for", "from", "with", "this", "that"}
    }


def jaccard(left: Iterable[str], right: Iterable[str]) -> float:
    first, second = set(left), set(right)
    if not first and not second:
        return 1.0
    if not first or not second:
        return 0.0
    return len(first & second) / len(first | second)


def title_from(path: Path, headings: list[dict[str, Any]]) -> str:
    if headings:
        return str(headings[0]["title"])
    return path.stem.replace("_", " ").replace("-", " ").strip() or path.name


def classify_artifact(path: Path, relative: str, text: str) -> str:
    lower_path = relative.lower()
    name = path.name.lower()
    lower_text = text.lower()
    if "copilot-instructions" in name or "agent instructions" in lower_text:
        return "agent_instructions"
    if name == "skill.md" or name.startswith("skill-") or ("## propósito" in lower_text and "criterios de salida" in lower_text):
        return "skill"
    if "schema" in name or (path.suffix.lower() == ".json" and '"$schema"' in lower_text):
        return "schema"
    if "audit" in name or "auditor" in lower_text:
        return "audit"
    if "prompt" in name or lower_path.startswith("prompts/") or "/prompts/" in lower_path:
        return "prompt"
    if "template" in name or lower_path.startswith("templates/") or "/templates/" in lower_path:
        return "template"
    if path.suffix.lower() == ".py" and (lower_path.startswith("tools/") or "/tools/" in lower_path or "argparse" in lower_text or "__main__" in lower_text):
        return "tool"
    if "/boards/" in lower_path or lower_path.startswith("boards/"):
        return "hardware_board"
    if "/peripherals/" in lower_path or lower_path.startswith("peripherals/"):
        return "hardware_peripheral"
    if "wiring" in name or "conexiones" in name or "project-wiring" in name:
        return "project_wiring"
    if name in {"readme.md", "readme", "changelog.md", "decisions.md", "roadmap.md"}:
        return "reference"
    if path.suffix.lower() in CODE_EXTENSIONS:
        return "source_code"
    if path.suffix.lower() in CONFIG_EXTENSIONS or name in {"platformio.ini", "package.json"}:
        return "configuration"
    if "/references/" in lower_path or "/shared/" in lower_path:
        return "reference"
    if path.suffix.lower() in {".md", ".markdown", ".rst", ".txt"}:
        return "documentation"
    return "unknown"


def read_text_metadata(path: Path) -> dict[str, Any]:
    headings: list[dict[str, Any]] = []
    tags: list[dict[str, Any]] = []
    references: set[str] = set()
    markers: set[str] = set()
    secret_fields: set[str] = set()
    line_count = 0
    replacement_count = 0
    max_line_length = 0
    try:
        with path.open("r", encoding="utf-8", errors="replace") as stream:
            for line_number, line in enumerate(stream, 1):
                line_count = line_number
                max_line_length = max(max_line_length, len(line.rstrip("\n")))
                replacement_count += line.count("\ufffd")
                heading = HEADING_RE.match(line)
                if heading:
                    headings.append({"level": len(heading.group(1)), "title": heading.group(2), "line": line_number})
                for match in TAG_RE.finditer(line):
                    tags.append({"tag": match.group(1).upper(), "line": line_number})
                for match in INCLUDE_RE.finditer(line):
                    references.add(match.group(1))
                for match in IMPORT_RE.finditer(line):
                    references.add(match.group(1))
                for match in FILE_REF_RE.finditer(line):
                    reference = match.group(1).strip("`[]<>")
                    if "/" in reference or "." in reference:
                        references.add(reference)
                lower = line.lower()
                for marker in TECHNICAL_MARKERS:
                    if marker in lower:
                        markers.add(marker)
                secret_match = SECRET_RE.search(line)
                if secret_match:
                    field = secret_match.group(1).lower().replace("-", "_")
                    secret_fields.add(field)
    except (OSError, UnicodeError) as exc:
        return {
            "read_status": "READ_ERROR",
            "read_error": str(exc),
            "line_count": 0,
            "headings": [],
            "tags": [],
            "references": [],
            "markers": [],
            "secret_fields": [],
            "replacement_characters": 0,
            "max_line_length": 0,
        }
    return {
        "read_status": "COMPLETE",
        "line_count": line_count,
        "headings": headings,
        "tags": tags,
        "references": sorted(references),
        "markers": sorted(markers),
        "secret_fields": sorted(secret_fields),
        "replacement_characters": replacement_count,
        "max_line_length": max_line_length,
    }


def collect_files(root: Path) -> tuple[list[Path], list[dict[str, Any]]]:
    files: list[Path] = []
    excluded: list[dict[str, Any]] = []
    for current, directories, names in os.walk(root):
        current_path = Path(current)
        kept: list[str] = []
        for directory in sorted(directories):
            if directory in SKIP_DIRS:
                excluded.append({"path": safe_relative(current_path / directory, root), "reason": "excluded_directory"})
            else:
                kept.append(directory)
        directories[:] = kept
        for name in sorted(names):
            files.append(current_path / name)
    return sorted(files), excluded


def evidence_reference(relative: str, metadata: dict[str, Any]) -> str:
    if metadata.get("headings"):
        first = metadata["headings"][0]
        return f"line {first['line']} heading: {first['title']}"
    if metadata.get("tags"):
        return f"line {metadata['tags'][0]['line']} tag: {metadata['tags'][0]['tag']}"
    return "file metadata and full text scan"


def target_scope(relative: str, artifact_type: str) -> str:
    lower = relative.lower()
    if artifact_type in {"source_code", "configuration", "project_wiring"}:
        return "PRODUCT_SPECIFIC"
    if any(part in lower for part in (".ai/", "/shared/", "shared/", "/templates/", "templates/")):
        return "PARAMETRIZABLE"
    if artifact_type in {"prompt", "template", "reference", "schema", "audit", "tool", "agent_instructions"}:
        return "REUSABLE"
    if artifact_type in {"hardware_board", "hardware_peripheral"}:
        return "PARAMETRIZABLE"
    return "PARAMETRIZABLE"


def detect_patterns(relative: str, artifact_type: str, metadata: dict[str, Any]) -> list[dict[str, Any]]:
    lower = relative.lower()
    markers = set(metadata.get("markers", []))
    patterns: list[dict[str, Any]] = []
    reference = evidence_reference(relative, metadata)

    def add(pattern_id: str, label: str, destination: str, transformation: str) -> None:
        patterns.append(
            {
                "pattern_id": pattern_id,
                "label": label,
                "destination": destination,
                "transformation": transformation,
                "evidence": {"file": relative, "reference": reference},
            }
        )

    if ".ai/" in lower or lower.startswith(".ai/"):
        add(
            "project-context-bundle",
            "bundle coordinado de contexto por proyecto",
            "templates/project-context-bundle/",
            "convertir nombres y valores de target en placeholders; conservar la estructura y la matriz de consistencia",
        )
    if "/shared/" in lower or lower.startswith("shared/"):
        add(
            "shared-project-layer",
            "capa de reglas y entorno compartido",
            "references/project-context-layers.md",
            "separar reglas generales de datos de cada proyecto y declarar el alcance (por ejemplo PlatformIO/embedded)",
        )
    if "board" in lower and artifact_type in {"hardware_board", "template", "reference"}:
        add(
            "board-catalog-entry",
            "ficha o checklist de catálogo de placa física",
            "catalog/boards/ y prompts/generar-ficha-board.md",
            "mantener la ficha concreta como procedencia; extraer solo schema, checklist y reglas de separación",
        )
    if "peripheral" in lower and artifact_type in {"hardware_peripheral", "template", "reference"}:
        add(
            "peripheral-catalog-entry",
            "ficha o checklist de catálogo de periférico",
            "catalog/peripherals/ y prompts/generar-ficha-periferico.md",
            "separar requisitos genéricos de variante, alimentación, lógica y wiring del proyecto",
        )
    if "wiring" in lower or "wiring" in markers or "gpio" in markers:
        add(
            "hardware-vs-project-wiring",
            "separación entre especificación de hardware y wiring concreto",
            "prompts/generar-project-wiring.md y referencias de hardware",
            "referenciar board/peripheral; no copiar pinout ni afirmar cableado físico desde un GPIO lógico",
        )
    if "platformio" in markers or "platformio.ini" in lower:
        add(
            "platformio-environment",
            "entorno PlatformIO parametrizable",
            "templates/shared-platformio/ o references/project-context-layers.md",
            "convertir board, framework, librerías, puerto y baudrate en parámetros",
        )
    if metadata.get("tags"):
        add(
            "code-tag-governance",
            "convención de tags TODO/FIXME/HACK/BUG/NOTE/WARN",
            "references/coding-style-tags.md y prompts de análisis",
            "extraer reglas de interpretación sin copiar valores del producto; relacionar BUG/TODO con tareas y decisiones",
        )
    if artifact_type in {"prompt", "template", "schema", "audit", "tool", "agent_instructions"}:
        add(
            "reusable-artifact-candidate",
            f"artefacto potencial de tipo {artifact_type}",
            f"codigo_tools/{artifact_type}/ o destino equivalente",
            "normalizar propósito, entradas, salidas, claims y compatibilidad antes de comparar o promover",
        )
    return patterns


def classify_file(path: Path, relative: str, artifact_type: str, metadata: dict[str, Any]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    if metadata.get("secret_fields"):
        reasons.append("contains secret-like field names; values are never emitted")
        if artifact_type in {"source_code", "configuration"}:
            return "SENSITIVE", reasons
    if artifact_type in {"source_code", "configuration", "project_wiring"}:
        reasons.append("source code, build configuration or project wiring is product-specific")
        return "PRODUCT_SPECIFIC", reasons
    lower = relative.lower()
    if ".ai/" in lower or lower.startswith(".ai/"):
        reasons.append("project context structure can be parameterized")
        return "PARAMETRIZABLE", reasons
    if artifact_type in {"hardware_board", "hardware_peripheral"}:
        reasons.append("hardware facts may be reusable only through a typed, sourced catalog entry")
        return "PARAMETRIZABLE", reasons
    if artifact_type in {"prompt", "template", "reference", "schema", "audit", "tool", "agent_instructions"}:
        reasons.append("path and artifact type indicate a repeatable procedure or contract")
        return "REUSABLE", reasons
    if any(marker in metadata.get("markers", []) for marker in ("firmware", "gpio", "arduino", "platformio")):
        reasons.append("technical content requires target scoping before reuse")
        return "PARAMETRIZABLE", reasons
    reasons.append("semantic purpose requires review")
    return "PARAMETRIZABLE", reasons


def candidate_tokens(relative: str, artifact_type: str, metadata: dict[str, Any], patterns: list[dict[str, Any]]) -> set[str]:
    values: list[str] = [relative, artifact_type]
    values.extend(str(item.get("title", "")) for item in metadata.get("headings", []))
    values.extend(metadata.get("markers", []))
    values.extend(str(item.get("tag", "")) for item in metadata.get("tags", []))
    values.extend(pattern["pattern_id"] for pattern in patterns)
    return tokens(values)


def destination_for(artifact_type: str, scope: str) -> str:
    if scope in {"PRODUCT_SPECIFIC", "SENSITIVE"}:
        return "SOURCE_ONLY_EVIDENCE"
    return {
        "prompt": "codigo_tools/prompts/",
        "template": "codigo_tools/templates/",
        "reference": "codigo_tools/references/",
        "schema": "codigo_tools/catalog/schemas/ or templates/",
        "audit": "codigo_tools/prompts/ or tools/",
        "tool": "codigo_tools/tools/",
        "skill": "codigo_tools/templates/ or prompts/",
        "agent_instructions": "codigo_tools/templates/",
        "hardware_board": "codigo_tools/catalog/boards/ or catalog policy",
        "hardware_peripheral": "codigo_tools/catalog/peripherals/ or catalog policy",
        "project_wiring": "SOURCE_ONLY_EVIDENCE; reference via project-wiring",
        "documentation": "codigo_tools/references/ after extracting the pattern",
    }.get(artifact_type, "REVIEW_REQUIRED")


def baseline_records(root: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    paths, _ = collect_files(root)
    for path in paths:
        if not is_text_file(path):
            continue
        metadata = read_text_metadata(path)
        if metadata.get("read_status") != "COMPLETE":
            continue
        relative = safe_relative(path, root)
        artifact_type = classify_artifact(path, relative, "")
        patterns = detect_patterns(relative, artifact_type, metadata)
        records.append(
            {
                "path": relative,
                "artifact_type": artifact_type,
                "tokens": sorted(candidate_tokens(relative, artifact_type, metadata, patterns)),
                "pattern_ids": sorted(pattern["pattern_id"] for pattern in patterns),
                "markers": metadata.get("markers", []),
                "headings": [item["title"] for item in metadata.get("headings", [])],
            }
        )
    return records


def compare_to_baseline(candidate: dict[str, Any], baseline: list[dict[str, Any]]) -> dict[str, Any]:
    if candidate["scope"] in {"PRODUCT_SPECIFIC", "SENSITIVE"}:
        return {
            "decision": "FUERA_DE_ALCANCE",
            "confidence": "ALTA",
            "canonical_path": None,
            "similarity": 0.0,
            "reason": "product-specific or sensitive content is evidence only and is not promoted",
        }
    if candidate.get("read_status") != "COMPLETE":
        return {
            "decision": "NO_DECIDIBLE",
            "confidence": "BAJA",
            "canonical_path": None,
            "similarity": 0.0,
            "reason": "text was not read completely",
        }
    ranked: list[tuple[float, dict[str, Any]]] = []
    candidate_tokens_set = set(candidate["tokens"])
    for item in baseline:
        type_score = 0.25 if item["artifact_type"] == candidate["artifact_type"] else 0.0
        token_score = 0.55 * jaccard(candidate_tokens_set, item["tokens"])
        candidate_patterns = set(candidate.get("pattern_ids", []))
        baseline_patterns = set(item.get("pattern_ids", []))
        pattern_score = 0.20 * jaccard(candidate_patterns, baseline_patterns) if candidate_patterns and baseline_patterns else 0.0
        ranked.append((round(type_score + token_score + pattern_score, 4), item))
    if not ranked:
        return {
            "decision": "NUEVO",
            "confidence": "MEDIA",
            "canonical_path": None,
            "similarity": 0.0,
            "reason": "no baseline files were available",
        }
    score, best = max(ranked, key=lambda pair: pair[0])
    if score >= 0.78:
        decision, confidence, reason = "DUPLICADO", "MEDIA", "high heuristic similarity; review content before rejecting"
    elif score >= 0.42:
        decision, confidence, reason = "MEJORA", "BAJA", "related baseline capability; identify exact new sections or claims"
    elif candidate["artifact_type"] == best["artifact_type"] and candidate.get("markers") and set(candidate["markers"]) != set(best.get("markers", [])):
        decision, confidence, reason = "VARIANTE", "BAJA", "same broad artifact type with different technical scope"
    else:
        decision, confidence, reason = "NUEVO", "BAJA", "no strong equivalent found heuristically"
    return {
        "decision": decision,
        "confidence": confidence,
        "canonical_path": best["path"],
        "similarity": score,
        "reason": reason,
    }


def build_candidate(
    path: Path,
    root: Path,
    baseline: list[dict[str, Any]],
    known_artifact_type: str | None = None,
) -> dict[str, Any]:
    relative = safe_relative(path, root)
    metadata = read_text_metadata(path)
    artifact_type = known_artifact_type or classify_artifact(path, relative, "")
    patterns = detect_patterns(relative, artifact_type, metadata)
    scope, scope_reasons = classify_file(path, relative, artifact_type, metadata)
    candidate = {
        "material_id": f"material-{hashlib.sha256(relative.encode('utf-8')).hexdigest()[:12]}",
        "source_file": relative,
        "artifact_type": artifact_type,
        "read_status": metadata.get("read_status"),
        "line_count": metadata.get("line_count", 0),
        "headings": metadata.get("headings", []),
        "tags": metadata.get("tags", []),
        "references": metadata.get("references", []),
        "markers": metadata.get("markers", []),
        "secret_fields": metadata.get("secret_fields", []),
        "scope": scope,
        "scope_reasons": scope_reasons,
        "patterns": patterns,
        "pattern_ids": sorted(pattern["pattern_id"] for pattern in patterns),
        "tokens": sorted(candidate_tokens(relative, artifact_type, metadata, patterns)),
        "proposed_destination": destination_for(artifact_type, scope),
        "transformation": (
            "no promotion; keep as source evidence and redact sensitive values"
            if scope in {"PRODUCT_SPECIFIC", "SENSITIVE"}
            else "extract structure, rules and contracts; replace project values with placeholders and preserve provenance"
        ),
        "risk": (
            "copying this file would import product-specific behavior or secrets"
            if scope in {"PRODUCT_SPECIFIC", "SENSITIVE"}
            else "heuristic extraction may confuse a project-specific document with a reusable procedure"
        ),
    }
    candidate["evidence_reference"] = evidence_reference(relative, metadata)
    comparison = compare_to_baseline(candidate, baseline)
    candidate["comparison"] = comparison
    return candidate


def build_ai_bundle_candidate(
    files: list[dict[str, Any]],
    baseline: list[dict[str, Any]],
) -> dict[str, Any] | None:
    """Create one candidate for a coordinated .ai context directory."""
    ai_files = [
        item
        for item in files
        if item.get("file_kind") == "text"
        and (item.get("path", "").startswith(".ai/") or "/.ai/" in item.get("path", ""))
    ]
    if len(ai_files) < 2:
        return None
    source_files = [item["path"] for item in ai_files]
    source_label = ".ai/ (context bundle)"
    headings = [heading for item in ai_files for heading in item.get("headings", [])]
    tags = [tag for item in ai_files for tag in item.get("tags", [])]
    markers = sorted({marker for item in ai_files for marker in item.get("markers", [])})
    secret_fields = sorted({field for item in ai_files for field in item.get("secret_fields", [])})
    metadata = {
        "read_status": "COMPLETE" if all(item.get("read_status") == "COMPLETE" for item in ai_files) else "READ_ERROR",
        "line_count": sum(item.get("line_count", 0) for item in ai_files),
        "headings": headings,
        "tags": tags,
        "markers": markers,
        "secret_fields": secret_fields,
    }
    patterns = [
        {
            "pattern_id": "project-context-bundle",
            "label": "bundle coordinado de contexto por proyecto",
            "destination": "templates/project-context-bundle/",
            "transformation": "convertir nombres y valores de target en placeholders; preservar la coordinación entre contexto, hardware, software, skill, tareas, decisiones, roadmap y changelog",
            "evidence": {"files": source_files, "reference": "all .ai files read"},
        }
    ]
    values = [source_label, "template", "project-context-bundle", "PROJECT_CONTEXT", "HARDWARE", "SOFTWARE", "SKILL", "TASKS", "DECISIONS", "ROADMAP", "CHANGELOG"]
    values.extend(source_files)
    values.extend(markers)
    candidate = {
        "material_id": f"material-{hashlib.sha256('|'.join(source_files).encode('utf-8')).hexdigest()[:12]}",
        "source_file": source_label,
        "source_files": source_files,
        "artifact_type": "template",
        "read_status": metadata["read_status"],
        "line_count": metadata["line_count"],
        "headings": headings,
        "tags": tags,
        "references": [],
        "markers": markers,
        "secret_fields": secret_fields,
        "scope": "PARAMETRIZABLE",
        "scope_reasons": ["multiple coordinated .ai files form a reusable project-context structure"],
        "patterns": patterns,
        "pattern_ids": ["project-context-bundle"],
        "tokens": sorted(tokens(values)),
        "proposed_destination": "codigo_tools/templates/project-context-bundle/",
        "transformation": "create a complete parameterized bundle; keep project values and firmware rules in the source project",
        "risk": "individual files may look reusable while their cross-file consistency depends on the source project",
        "evidence_reference": f"{len(source_files)} coordinated .ai files; all files read",
    }
    candidate["comparison"] = compare_to_baseline(candidate, baseline)
    return candidate


def inventory(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    paths, excluded = collect_files(root)
    records: list[dict[str, Any]] = []
    for path in paths:
        relative = safe_relative(path, root)
        try:
            size = path.stat().st_size
            digest = sha256_file(path)
        except OSError as exc:
            records.append({"path": relative, "read_status": "STAT_ERROR", "error": str(exc)})
            continue
        if not is_text_file(path):
            records.append(
                {
                    "path": relative,
                    "bytes": size,
                    "sha256": digest,
                    "file_kind": "binary_or_unknown",
                    "read_status": "BINARY_METADATA_ONLY",
                }
            )
            continue
        metadata = read_text_metadata(path)
        records.append(
            {
                "path": relative,
                "bytes": size,
                "sha256": digest,
                "file_kind": "text",
                "artifact_type": classify_artifact(path, relative, ""),
                **metadata,
            }
        )
    return records, excluded


def make_scan(root: Path, baseline_root: Path | None, target_id: str, snapshot: str, purpose: str) -> dict[str, Any]:
    files, excluded = inventory(root)
    baseline = baseline_records(baseline_root) if baseline_root else []
    candidates: list[dict[str, Any]] = []
    for record in files:
        if record.get("file_kind") != "text":
            continue
        candidates.append(build_candidate(root / record["path"], root, baseline, record.get("artifact_type")))
    ai_bundle = build_ai_bundle_candidate(files, baseline)
    if ai_bundle:
        candidates.append(ai_bundle)
    read_errors = [item for item in files if item.get("read_status") not in {"COMPLETE", "BINARY_METADATA_ONLY"}]
    binary_files = [item for item in files if item.get("read_status") == "BINARY_METADATA_ONLY"]
    incomplete = bool(read_errors)
    decisions: dict[str, int] = {}
    for candidate in candidates:
        decision = candidate["comparison"]["decision"]
        decisions[decision] = decisions.get(decision, 0) + 1
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "reusable-material-scan",
        "source": {
            "root": str(root),
            "target_id": target_id,
            "snapshot": snapshot,
            "purpose": purpose,
        },
        "coverage": {
            "files_discovered": len(files),
            "text_files_read": sum(1 for item in files if item.get("read_status") == "COMPLETE"),
            "binary_metadata_only": len(binary_files),
            "read_errors": len(read_errors),
            "excluded_directories": excluded,
            "read_status": "LECTURA_INCOMPLETA" if incomplete else "COMPLETA_CON_BINARIOS_EN_METADATA",
        },
        "baseline": {
            "root": str(baseline_root) if baseline_root else None,
            "files_compared": len(baseline),
            "status": "AVAILABLE" if baseline_root else "NOT_PROVIDED",
        },
        "files": files,
        "candidates": candidates,
        "matrix": [
            {
                "material_id": candidate["material_id"],
                "source_file": candidate["source_file"],
                "artifact_type": candidate["artifact_type"],
                "scope": candidate["scope"],
                "decision": candidate["comparison"]["decision"],
                "confidence": candidate["comparison"]["confidence"],
                "canonical_path": candidate["comparison"]["canonical_path"],
                "similarity": candidate["comparison"]["similarity"],
                "evidence": candidate["evidence_reference"],
                "destination": candidate["proposed_destination"],
                "transformation": candidate["transformation"],
                "risk": candidate["risk"],
                "review_required": True,
            }
            for candidate in candidates
        ],
        "summary": {
            "decisions": decisions,
            "promotion_allowed": False,
            "note": "This is a heuristic extraction plan. Human/LLM review is required before creating or improving codigo_tools artifacts.",
        },
        "guardrails": [
            "Do not copy firmware, product logic, project wiring, secrets or target values into codigo_tools.",
            "Treat source code and build configuration as product-specific evidence unless explicitly parameterized.",
            "Treat all heuristic decisions as reviewable proposals, never as canonical acceptance.",
            "Preserve source path, snapshot and evidence reference for every candidate.",
            "Do not modify the scanned source project.",
        ],
    }


def md_cell(value: Any) -> str:
    text = str(value if value is not None else "—")
    return text.replace("|", "\\|").replace("\n", " ")


def render_plan(scan: dict[str, Any]) -> str:
    source = scan["source"]
    coverage = scan["coverage"]
    baseline = scan["baseline"]
    decisions = scan["summary"]["decisions"]
    lines = [
        f"# Plan de material reutilizable — `{source['target_id']}`",
        "",
        "## Estado",
        f"- Raíz: `{source['root']}`",
        f"- Snapshot: `{source['snapshot']}`",
        f"- Lectura: **{coverage['read_status']}**",
        f"- Archivos descubiertos: `{coverage['files_discovered']}`",
        f"- Archivos de texto leídos: `{coverage['text_files_read']}`",
        f"- Binarios registrados solo por metadata: `{coverage['binary_metadata_only']}`",
        f"- Errores de lectura: `{coverage['read_errors']}`",
        f"- Baseline comparado: `{baseline['root'] or 'no proporcionado'}`",
        "- Promoción automática: **BLOQUEADA**",
        "",
        "## Resumen de decisiones heurísticas",
    ]
    lines.extend([f"- `{key}`: {value}" for key, value in sorted(decisions.items())] or ["- Sin candidatos de texto"])
    lines.extend(
        [
            "",
            "## Matriz de extracción",
            "",
            "| Material | Fuente | Tipo | Alcance | Decisión | Canónico | Evidencia | Destino | Acción |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in scan["matrix"]:
        action = "revisar; no promover automáticamente"
        lines.append(
            "| "
            + " | ".join(
                md_cell(row[key])
                for key in (
                    "material_id",
                    "source_file",
                    "artifact_type",
                    "scope",
                    "decision",
                    "canonical_path",
                    "evidence",
                    "destination",
                    "transformation",
                )
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Patrones candidatos detectados",
        ]
    )
    pattern_count = 0
    for candidate in scan["candidates"]:
        for pattern in candidate.get("patterns", []):
            pattern_count += 1
            evidence = pattern["evidence"]
            evidence_source = evidence.get("file") or ", ".join(evidence.get("files", []))
            lines.append(
                f"- `{pattern['pattern_id']}` — {pattern['label']} — fuente `{evidence_source}` ({evidence.get('reference', 'evidence')}); destino sugerido: `{pattern['destination']}`. Transformación: {pattern['transformation']}."
            )
    if pattern_count == 0:
        lines.append("- No se detectaron patrones por heurística; revisar los archivos manualmente.")
    lines.extend(
        [
            "",
            "## Archivos no textuales y exclusiones",
        ]
    )
    for item in scan["files"]:
        if item.get("read_status") == "BINARY_METADATA_ONLY":
            lines.append(f"- `{item['path']}` — binario/unknown; bytes `{item['bytes']}`, SHA-256 `{item['sha256']}`; no se copió contenido.")
    for item in coverage.get("excluded_directories", []):
        lines.append(f"- `{item['path']}` — {item['reason']}.")
    if not any(item.get("read_status") == "BINARY_METADATA_ONLY" for item in scan["files"]) and not coverage.get("excluded_directories"):
        lines.append("- Ninguno.")
    lines.extend(
        [
            "",
            "## Reglas anti-desviación",
            "",
            "- El firmware, la lógica de producto y el wiring concreto son evidencia del proyecto, no artefactos globales.",
            "- Los valores específicos deben convertirse en placeholders o permanecer en la fuente.",
            "- Una decisión heurística `NUEVO` o `MEJORA` requiere leer el canónico completo y revisar claims/procedencia.",
            "- Las fichas de hardware deben mantener separadas board, peripheral y project-wiring.",
            "- Este informe propone; no crea, modifica ni publica artefactos automáticamente.",
            "",
            "## Próximos pasos del plan",
            "",
            "1. Revisar candidatos `REUSABLE` y `PARAMETRIZABLE` individualmente.",
            "2. Leer el artefacto canónico indicado en cada posible `MEJORA` o `DUPLICADO`.",
            "3. Separar reglas generales, placeholders, datos específicos y sensibles.",
            "4. Redactar propuestas completas con procedencia y diff previsto.",
            "5. Validar las propuestas antes de crear un PR.",
            "",
            "**Resultado:** extracción heurística completada; revisión y aprobación aún requeridas.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_json(value: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def command_scan(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: project root is not a directory: {root}", file=sys.stderr)
        return 1
    baseline = Path(args.baseline_root).resolve() if args.baseline_root else None
    if baseline and not baseline.is_dir():
        print(f"ERROR: baseline root is not a directory: {baseline}", file=sys.stderr)
        return 1
    output_dir = Path(args.output_dir).resolve()
    scan = make_scan(root, baseline, args.target_id or root.name, args.snapshot, args.project_purpose)
    write_json(scan, output_dir / "scan.json")
    (output_dir / "plan.md").write_text(render_plan(scan), encoding="utf-8")
    print(json.dumps({"output_dir": str(output_dir), "scan": str(output_dir / "scan.json"), "plan": str(output_dir / "plan.md"), "read_status": scan["coverage"]["read_status"], "candidates": len(scan["candidates"])}, ensure_ascii=False, indent=2))
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Escanea un proyecto y genera un plan trazable de material reutilizable.")
    sub = root.add_subparsers(dest="command", required=True)
    scan = sub.add_parser("scan", help="leer archivos, extraer patrones y generar scan.json/plan.md")
    scan.add_argument("root", help="raíz del proyecto fuente")
    scan.add_argument("--baseline-root", help="raíz actual de codigo_tools para comparación heurística")
    scan.add_argument("--output-dir", required=True, help="directorio fuera de la fuente donde se escriben los reportes")
    scan.add_argument("--target-id", default="", help="target o ensamblaje exacto")
    scan.add_argument("--snapshot", default="PENDIENTE_DE_VERIFICAR", help="commit, rama, tag o fecha")
    scan.add_argument("--project-purpose", default="PENDIENTE_DE_CONFIRMAR", help="propósito confirmado del proyecto")
    scan.set_defaults(func=command_scan)
    return root


if __name__ == "__main__":
    arguments = parser().parse_args()
    raise SystemExit(arguments.func(arguments))
