#!/usr/bin/env python3
"""Discover and compare reusable artifact candidates.

This tool deliberately stops at a reviewable proposal. It does not merge or
overwrite canonical artifacts; semantic generation and approval remain an
explicit step driven by detectar-evolucionar-artefactos.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


DECISIONS = {
    "NUEVO",
    "MEJORA",
    "DUPLICADO",
    "CONTRADICTORIO",
    "VARIANTE",
    "NO_DECIDIBLE",
}
ARTIFACT_TYPES = {
    "prompt",
    "template",
    "reference",
    "schema",
    "audit",
    "tool",
    "skill",
    "agent_instructions",
    "readme",
    "repo_map",
    "hardware_docs",
    "unknown",
}
SKIP_DIRS = {".git", ".pio", "node_modules", "__pycache__", ".venv", "venv"}
TEXT_EXTENSIONS = {
    ".md",
    ".markdown",
    ".txt",
    ".yml",
    ".yaml",
    ".json",
    ".py",
    ".sh",
    ".js",
    ".ts",
    ".xml",
    ".svg",
}


def tokens(value: Any) -> set[str]:
    text = json.dumps(value, ensure_ascii=False) if not isinstance(value, str) else value
    return {token for token in re.findall(r"[a-z0-9][a-z0-9_-]{2,}", text.lower())}


def jaccard(left: Iterable[str], right: Iterable[str]) -> float:
    a, b = set(left), set(right)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def normalized(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip().lower())


def classify(path: Path, content: str) -> str:
    name = path.name.lower()
    lower = content.lower()
    if "copilot-instructions" in name or "agent instructions" in lower:
        return "agent_instructions"
    if name == "skill.md" or name.startswith("skill-") or "## propósito" in lower and "criterios de salida" in lower:
        return "skill"
    if "repo-map" in name or "archivo-mapa" in name:
        return "repo_map"
    if "audit" in name or "auditoría" in lower:
        return "audit"
    if "prompt" in name or path.parent.name == "prompts":
        return "prompt"
    if "template" in name or path.parent.name == "templates":
        return "template"
    if "notas" in name or "conexiones" in name:
        return "hardware_docs"
    if path.suffix.lower() in {".yml", ".yaml", ".json"} and "schema" in name:
        return "schema"
    if name == "readme.md":
        return "readme"
    if path.suffix.lower() == ".py" and ("argparse" in lower or "__main__" in lower):
        return "tool"
    return "unknown"


def candidate_id(path: Path, content: str) -> str:
    digest = hashlib.sha256(content.encode("utf-8", errors="replace")).hexdigest()[:12]
    stem = re.sub(r"[^a-z0-9]+", "-", path.stem.lower()).strip("-") or "artifact"
    return f"candidate-{stem}-{digest}"


def discover(root: Path) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    files_seen = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        files_seen += 1
        artifact_type = classify(path, content)
        if artifact_type == "unknown":
            continue
        relative = path.relative_to(root).as_posix()
        candidates.append(
            {
                "candidate_id": candidate_id(path, content),
                "path": relative,
                "artifact_type": artifact_type,
                "bytes": len(content.encode("utf-8")),
                "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                "title": next((line.lstrip("# ").strip() for line in content.splitlines() if line.startswith("#")), path.stem),
                "signals": sorted(tokens(path.name) | tokens(content[:4000])),
            }
        )
    return {
        "schema_version": 1,
        "root": str(root),
        "files_seen": files_seen,
        "candidates": candidates,
        "note": "Discovery is an inventory signal; semantic classification requires a normalized manifest and review.",
    }


def build_catalog(root: Path) -> dict[str, Any]:
    inventory = discover(root)
    artifacts = []
    for item in inventory["candidates"]:
        artifacts.append(
            {
                "artifact_id": f"discovered-{item['path'].replace('/', '-').replace(' ', '-')}",
                "artifact_type": item["artifact_type"],
                "status": "discovered",
                "purpose": item["title"],
                "target_scope": ["general"],
                "capabilities": item["signals"],
                "inputs": [],
                "outputs": [],
                "sections": [],
                "claims": [],
                "source_files": [{"path": item["path"], "reference": "file", "state": "DISCOVERED"}],
                "snapshot": None,
                "heuristic": True,
            }
        )
    return {
        "schema_version": 1,
        "root": str(root),
        "status": "discovered-not-semantic",
        "artifacts": artifacts,
        "note": "Normalize and review entries with detectar-evolucionar-artefactos.md before accepting them as canonical.",
    }


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = ["artifact_id", "artifact_type", "purpose", "capabilities", "claims", "source_files"]
    for key in required:
        if key not in manifest:
            errors.append(f"missing required field: {key}")
    if manifest.get("artifact_type") not in ARTIFACT_TYPES:
        errors.append(f"unsupported artifact_type: {manifest.get('artifact_type')}")
    if not isinstance(manifest.get("capabilities"), list):
        errors.append("capabilities must be a list")
    if not isinstance(manifest.get("claims"), list):
        errors.append("claims must be a list")
    if not isinstance(manifest.get("source_files"), list):
        errors.append("source_files must be a list")
    for index, claim in enumerate(manifest.get("claims", [])):
        if not isinstance(claim, dict):
            errors.append(f"claims[{index}] must be an object")
            continue
        for key in ("key", "value", "evidence"):
            if key not in claim:
                errors.append(f"claims[{index}] missing: {key}")
        if not claim.get("evidence"):
            errors.append(f"claims[{index}] has no evidence")
    return errors


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON {path}: {exc}") from exc


def catalog_items(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if isinstance(value, dict) and isinstance(value.get("artifacts"), list):
        return [item for item in value["artifacts"] if isinstance(item, dict)]
    if isinstance(value, dict):
        return [value]
    return []


def claim_map(manifest: dict[str, Any]) -> dict[str, str]:
    result: dict[str, str] = {}
    for claim in manifest.get("claims", []):
        if isinstance(claim, dict) and claim.get("key"):
            result[normalized(claim["key"])] = normalized(claim.get("value", ""))
    return result


def capability_score(candidate: dict[str, Any], existing: dict[str, Any]) -> float:
    score = 0.0
    if candidate.get("artifact_type") == existing.get("artifact_type"):
        score += 0.20
    score += 0.25 * jaccard(tokens(candidate.get("purpose", "")), tokens(existing.get("purpose", "")))
    score += 0.35 * jaccard(tokens(candidate.get("capabilities", [])), tokens(existing.get("capabilities", [])))
    score += 0.10 * jaccard(tokens(candidate.get("sections", [])), tokens(existing.get("sections", [])))
    candidate_scope = set(candidate.get("target_scope", []))
    existing_scope = set(existing.get("target_scope", []))
    if candidate_scope & existing_scope or "general" in candidate_scope or "general" in existing_scope:
        score += 0.10
    return round(min(score, 1.0), 4)


def compare(candidate: dict[str, Any], catalog: list[dict[str, Any]]) -> dict[str, Any]:
    errors = validate_manifest(candidate)
    if errors:
        return {
            "schema_version": 1,
            "candidate_id": candidate.get("artifact_id"),
            "decision": "NO_DECIDIBLE",
            "confidence": "BAJA",
            "errors": errors,
            "review": {"status": "PENDING_APPROVAL"},
        }

    ranked = sorted(
        ((capability_score(candidate, item), item) for item in catalog),
        key=lambda pair: pair[0],
        reverse=True,
    )
    best_score, best = ranked[0] if ranked else (0.0, None)
    if best is None or best_score < 0.45:
        return result(candidate, "NUEVO", "ALTA", None, best_score, [], [], [], [], [])

    candidate_claims = claim_map(candidate)
    existing_claims = claim_map(best)
    same_claims = sorted(key for key in candidate_claims.keys() & existing_claims.keys() if candidate_claims[key] == existing_claims[key])
    conflicts = sorted(
        [
            {
                "key": key,
                "candidate": candidate_claims[key],
                "canonical": existing_claims[key],
            }
            for key in candidate_claims.keys() & existing_claims.keys()
            if candidate_claims[key] != existing_claims[key]
        ],
        key=lambda item: item["key"],
    )
    new_claims = sorted(key for key in candidate_claims.keys() - existing_claims.keys())
    common_caps = sorted(set(candidate.get("capabilities", [])) & set(best.get("capabilities", [])))
    new_caps = sorted(set(candidate.get("capabilities", [])) - set(best.get("capabilities", [])))
    candidate_scope = set(candidate.get("target_scope", []))
    canonical_scope = set(best.get("target_scope", []))
    incompatible_scope = bool(candidate_scope and canonical_scope and not (candidate_scope & canonical_scope or "general" in candidate_scope or "general" in canonical_scope))

    if conflicts:
        decision, confidence = "CONTRADICTORIO", "ALTA"
    elif incompatible_scope:
        decision, confidence = "VARIANTE", "ALTA"
    elif new_claims or new_caps or len(candidate.get("sections", [])) > len(best.get("sections", [])):
        decision, confidence = "MEJORA", "MEDIA" if best_score < 0.70 else "ALTA"
    else:
        decision, confidence = "DUPLICADO", "ALTA" if best_score >= 0.75 else "MEDIA"
    return result(candidate, decision, confidence, best, best_score, common_caps, new_caps, same_claims, new_claims, conflicts)


def result(candidate: dict[str, Any], decision: str, confidence: str, best: dict[str, Any] | None, score: float, common_caps: list[str], new_caps: list[str], same_claims: list[str], new_claims: list[str], conflicts: list[dict[str, str]]) -> dict[str, Any]:
    proposal_suffix = {
        "NUEVO": "new",
        "MEJORA": "improvement",
        "CONTRADICTORIO": "conflict",
        "VARIANTE": "variant",
    }.get(decision)
    candidate_id = candidate.get("artifact_id", "candidate")
    return {
        "schema_version": 1,
        "candidate_id": candidate_id,
        "candidate_snapshot": candidate.get("snapshot"),
        "decision": decision,
        "confidence": confidence,
        "similarity_score": round(score, 4),
        "canonical_artifact_id": best.get("artifact_id") if best else None,
        "matching_capabilities": common_caps,
        "new_capabilities": new_caps,
        "same_claims": same_claims,
        "new_claims": new_claims,
        "conflicts": conflicts,
        "evidence_gaps": [] if candidate.get("verification", {}).get("read_complete") is True else ["read_complete=false"],
        "proposal_path": f"proposals/{candidate_id}-{proposal_suffix}.md" if proposal_suffix else None,
        "review": {"status": "PENDING_APPROVAL", "approved_by": None, "approved_at": None, "decision_notes": None},
    }


def render_markdown(report: dict[str, Any]) -> str:
    common_caps = report.get("matching_capabilities", [])
    new_caps = report.get("new_capabilities", [])
    new_claims = report.get("new_claims", [])
    lines = [
        f"# Evolución de artefacto — `{report.get('candidate_id', 'candidate')}`",
        "",
        f"- Decisión: **{report.get('decision', 'NO_DECIDIBLE')}**",
        f"- Confianza: **{report.get('confidence', 'BAJA')}**",
        f"- Similitud: `{report.get('similarity_score', 0)}`",
        f"- Canónico comparado: `{report.get('canonical_artifact_id') or 'ninguno'}`",
        "- Revisión: **PENDING_APPROVAL**",
        "",
        "## Capacidades coincidentes",
    ]
    lines.extend([f"- {item}" for item in common_caps] or ["- Ninguna"])
    lines.extend(["", "## Capacidades nuevas"])
    lines.extend([f"- {item}" for item in new_caps] or ["- Ninguna"])
    lines.extend(["", "## Claims nuevos"])
    lines.extend([f"- `{item}`" for item in new_claims] or ["- Ninguno"])
    lines.extend(["", "## Conflictos"])
    conflicts = report.get("conflicts", [])
    lines.extend(
        [f"- `{item['key']}`: candidato=`{item['candidate']}`; canónico=`{item['canonical']}`" for item in conflicts]
        or ["- Ninguno"]
    )
    lines.extend(
        [
            "",
            "## Próxima acción",
            "No modificar ni publicar el artefacto hasta revisar la propuesta, la procedencia y los gaps de evidencia.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_output(value: Any, path: Path | None) -> None:
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def command_discover(args: argparse.Namespace) -> int:
    write_output(discover(Path(args.root).resolve()), Path(args.output) if args.output else None)
    return 0


def command_catalog(args: argparse.Namespace) -> int:
    write_output(build_catalog(Path(args.root).resolve()), Path(args.output) if args.output else None)
    return 0


def command_validate(args: argparse.Namespace) -> int:
    manifest = load_json(Path(args.manifest))
    errors = validate_manifest(manifest)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Valid manifest: {manifest['artifact_id']}")
    return 0


def command_compare(args: argparse.Namespace) -> int:
    candidate = load_json(Path(args.candidate))
    catalog = catalog_items(load_json(Path(args.catalog)))
    report = compare(candidate, catalog)
    output = Path(args.output) if args.output else None
    write_output(report, output)
    if args.markdown:
        markdown_path = Path(args.markdown)
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return 0 if report.get("decision") != "NO_DECIDIBLE" else 2


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Discover and compare reusable artifact candidates.")
    sub = root.add_subparsers(dest="command", required=True)

    discover_parser = sub.add_parser("discover", help="inventory likely artifact files in a project")
    discover_parser.add_argument("root")
    discover_parser.add_argument("--output")
    discover_parser.set_defaults(func=command_discover)

    catalog_parser = sub.add_parser("catalog", help="build a reviewable heuristic catalog from a project")
    catalog_parser.add_argument("root")
    catalog_parser.add_argument("--output")
    catalog_parser.set_defaults(func=command_catalog)

    validate_parser = sub.add_parser("validate", help="validate a normalized artifact manifest")
    validate_parser.add_argument("manifest")
    validate_parser.set_defaults(func=command_validate)

    compare_parser = sub.add_parser("compare", help="compare one manifest against an artifact catalog")
    compare_parser.add_argument("--candidate", required=True)
    compare_parser.add_argument("--catalog", required=True)
    compare_parser.add_argument("--output")
    compare_parser.add_argument("--markdown")
    compare_parser.set_defaults(func=command_compare)
    return root


if __name__ == "__main__":
    arguments = parser().parse_args()
    raise SystemExit(arguments.func(arguments))
