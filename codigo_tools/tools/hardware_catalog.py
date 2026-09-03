#!/usr/bin/env python3
"""Validate and inspect the hybrid board/peripheral/wiring catalog.

The tool is intentionally dependency-free and conservative: it checks
structure, references, duplicate pins and declared signal mismatches. It does
not claim electrical safety or hardware verification.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

KINDS = {"board", "peripheral", "wiring", "rules"}
EVIDENCE_STATES = {
    "OBSERVADO_EN_CODIGO", "OBSERVADO_EN_BUILD", "DOCUMENTADO", "ESTIMADO",
    "CONTRADICTORIO", "PENDIENTE_DE_VERIFICAR", "VERIFICADO_EN_HARDWARE",
}


def load(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"no se pudo leer JSON {path}: {exc}") from exc


def required(data: dict[str, Any], fields: list[str]) -> list[str]:
    return [field for field in fields if field not in data]


def validate_evidence(items: Any, label: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(items, list):
        return [f"{label} debe ser una lista"]
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            errors.append(f"{label}[{index}] debe ser un objeto")
            continue
        if "source" not in item or "state" not in item:
            errors.append(f"{label}[{index}] requiere source y state")
        elif item["state"] not in EVIDENCE_STATES:
            errors.append(f"{label}[{index}] estado desconocido: {item['state']}")
    return errors


def validate_board(data: dict[str, Any]) -> list[str]:
    errors = required(data, ["schema_version", "kind", "id", "name", "aliases", "variants", "platformio", "identity", "power", "logic", "pins", "restrictions", "provenance", "evidence_status"])
    if data.get("kind") != "board":
        errors.append("kind debe ser board")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(data.get("id", ""))):
        errors.append("id debe usar kebab-case ASCII")
    if not isinstance(data.get("pins"), list):
        errors.append("pins debe ser una lista")
    errors.extend(validate_evidence(data.get("provenance"), "provenance"))
    return errors


def validate_peripheral(data: dict[str, Any]) -> list[str]:
    errors = required(data, ["schema_version", "kind", "id", "name", "aliases", "variants", "category", "power", "signals", "interfaces", "requirements", "provenance", "evidence_status"])
    if data.get("kind") != "peripheral":
        errors.append("kind debe ser peripheral")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", str(data.get("id", ""))):
        errors.append("id debe usar kebab-case ASCII")
    if not isinstance(data.get("interfaces"), list):
        errors.append("interfaces debe ser una lista")
    errors.extend(validate_evidence(data.get("provenance"), "provenance"))
    return errors


def validate_wiring(data: dict[str, Any]) -> list[str]:
    errors = required(data, ["schema_version", "kind", "project_id", "target_id", "board_ref", "peripherals", "connections", "evidence_status"])
    if data.get("kind") != "project-wiring":
        errors.append("kind debe ser project-wiring")
    if not isinstance(data.get("peripherals"), list):
        errors.append("peripherals debe ser una lista")
    if not isinstance(data.get("connections"), list):
        errors.append("connections debe ser una lista")
    for index, connection in enumerate(data.get("connections", [])):
        if not isinstance(connection, dict):
            errors.append(f"connections[{index}] debe ser un objeto")
            continue
        errors.extend(f"connections[{index}] requiere {field}" for field in required(connection, ["from", "to", "signal"]))
        errors.extend(validate_evidence(connection.get("evidence", []), f"connections[{index}].evidence"))
    return errors


def validate_rules(data: dict[str, Any]) -> list[str]:
    errors = required(data, ["schema_version", "kind", "rules"])
    if data.get("kind") != "compatibility-rules":
        errors.append("kind debe ser compatibility-rules")
    if not isinstance(data.get("rules"), list):
        errors.append("rules debe ser una lista")
    return errors


def validate(kind: str, data: dict[str, Any]) -> list[str]:
    if kind == "board":
        return validate_board(data)
    if kind == "peripheral":
        return validate_peripheral(data)
    if kind == "wiring":
        return validate_wiring(data)
    if kind == "rules":
        return validate_rules(data)
    return [f"tipo no soportado: {kind}"]


def resolve_ref(ref: str, root: Path, collection: str) -> tuple[Path | None, dict[str, Any] | None]:
    candidate = root / ref
    if candidate.exists():
        return candidate, load(candidate)
    for path in sorted((root / collection).rglob("*.json")):
        try:
            data = load(path)
        except ValueError:
            continue
        if data.get("id") == ref or ref in data.get("aliases", []):
            return path, data
    return None, None


def check_project(wiring_path: Path, catalog_root: Path) -> dict[str, Any]:
    wiring = load(wiring_path)
    errors = validate_wiring(wiring)
    warnings: list[str] = []
    board_path, board = resolve_ref(str(wiring.get("board_ref", "")), catalog_root, "boards")
    if board is None:
        errors.append(f"board_ref no resuelto: {wiring.get('board_ref')}")
    elif validate_board(board):
        errors.append(f"ficha board inválida: {board_path}")

    peripheral_data: dict[str, dict[str, Any]] = {}
    for item in wiring.get("peripherals", []):
        if not isinstance(item, dict):
            errors.append("cada peripheral debe ser un objeto")
            continue
        path, data = resolve_ref(str(item.get("ref", "")), catalog_root, "peripherals")
        instance = str(item.get("instance", ""))
        if data is None:
            errors.append(f"peripheral ref no resuelto: {item.get('ref')}")
        else:
            peripheral_data[instance] = data
            item_errors = validate_peripheral(data)
            errors.extend(f"{path}: {error}" for error in item_errors)

    used_board_pins: dict[str, str] = {}
    used_peripheral_pins: dict[str, str] = {}
    for index, connection in enumerate(wiring.get("connections", [])):
        source = str(connection.get("from", ""))
        target = str(connection.get("to", ""))
        if source.startswith("board:"):
            if source in used_board_pins:
                warnings.append(f"pin de placa repetido: {source} en conexiones {used_board_pins[source]} y {index}")
            used_board_pins[source] = str(index)
        if ":" in target and not target.startswith("board:"):
            instance, pin = target.split(":", 1)
            key = f"{instance}:{pin}"
            if key in used_peripheral_pins:
                warnings.append(f"pin de peripheral repetido: {key} en conexiones {used_peripheral_pins[key]} y {index}")
            used_peripheral_pins[key] = str(index)
        if source.startswith("board:") and board:
            pin_id = source.split(":", 1)[1]
            pin = next((p for p in board.get("pins", []) if p.get("id") == pin_id or pin_id in p.get("aliases", [])), None)
            if pin and (pin.get("reserved") or pin.get("boot_sensitive")):
                warnings.append(f"conexión {index} usa pin reservado/sensible de boot: {source}")

        target_instance = target.split(":", 1)[0] if ":" in target else ""
        peripheral = peripheral_data.get(target_instance)
        if peripheral and board:
            board_logic = board.get("logic", {}).get("nominal_voltage")
            peripheral_logic = peripheral.get("signals", {}).get("logic_voltage")
            if board_logic and peripheral_logic and board_logic != peripheral_logic and not connection.get("level_shifter"):
                warnings.append(f"posible mismatch lógico en conexión {index}: board={board_logic}, peripheral={peripheral_logic}; falta level_shifter")

    return {
        "schema_version": 1,
        "project_id": wiring.get("project_id"),
        "decision": "FAIL" if errors else ("PASS_CON_ADVERTENCIAS" if warnings else "PASS"),
        "errors": errors,
        "warnings": warnings,
        "resolved": {"board": str(board_path) if board_path else None, "peripherals": sorted(peripheral_data)},
        "note": "La validación estructural no sustituye datasheet, medición ni prueba física.",
    }


def search(args: argparse.Namespace) -> int:
    root = Path(args.catalog_root)
    query = args.query.lower()
    collection = {"board": "boards", "peripheral": "peripherals"}.get(args.type)
    paths = sorted((root / collection).rglob("*.json")) if collection else sorted(root.rglob("*.json"))
    hits = []
    for path in paths:
        try:
            data = load(path)
        except ValueError:
            continue
        haystack = json.dumps(data, ensure_ascii=False).lower()
        if query in haystack:
            hits.append({"path": str(path), "id": data.get("id"), "name": data.get("name"), "kind": data.get("kind")})
    print(json.dumps({"query": args.query, "results": hits}, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validador del catálogo híbrido de hardware.")
    sub = parser.add_subparsers(dest="command", required=True)
    validate_parser = sub.add_parser("validate")
    validate_parser.add_argument("--type", choices=sorted(KINDS), required=True)
    validate_parser.add_argument("path")
    search_parser = sub.add_parser("search")
    search_parser.add_argument("--type", choices=["board", "peripheral"])
    search_parser.add_argument("--catalog-root", default="catalog")
    search_parser.add_argument("query")
    check_parser = sub.add_parser("check-project")
    check_parser.add_argument("--catalog-root", default="catalog")
    check_parser.add_argument("wiring")
    args = parser.parse_args()

    try:
        if args.command == "validate":
            errors = validate(args.type, load(Path(args.path)))
            if errors:
                for error in errors:
                    print(f"ERROR: {error}", file=sys.stderr)
                return 1
            print(f"Valid {args.type}: {args.path}")
            return 0
        if args.command == "search":
            return search(args)
        report = check_project(Path(args.wiring), Path(args.catalog_root))
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["decision"] != "FAIL" else 1
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
