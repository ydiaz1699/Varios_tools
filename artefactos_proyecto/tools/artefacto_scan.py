#!/usr/bin/env python3
"""artefacto_scan — descubre archivos-artefacto en repos de referencia y los compara
con el catálogo `artefactos_proyecto`.

Qué hace (enfoque a + b):
  (a) REPORTA: para cada repo de referencia, lista qué artefactos estándar tiene,
      y los clasifica frente a tu catálogo en NUEVO / YA_TIENES / (candidato a) MEJORA.
      Descarga los ejemplos reales a tools/_referencias/<repo>/ como material de consulta.
  (b) SEMBRAR: con --seed, crea una ficha BORRADOR en entries/ para cada artefacto NUEVO,
      lista para que tú/un LLM la completes y GENERALICES.

Regla (filosofía codigo_tools): esta herramienta trae los ejemplos como REFERENCIA;
NUNCA copia el archivo ajeno tal cual como tu plantilla. La generalización (quitar lo
específico del repo fuente, dejar placeholders) la hace una persona/LLM al revisar.

Requiere: `gh` autenticado (usa `gh api`). Sin dependencias de terceros.

Uso:
  python3 artefacto_scan.py                          # escanea los repos de sources.txt
  python3 artefacto_scan.py --repo prowler-cloud/prowler
  python3 artefacto_scan.py --seed                   # además crea fichas BORRADOR de los NUEVO
  python3 artefacto_scan.py --json                   # salida machine-readable
"""

from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # .../artefactos_proyecto
CATALOG = ROOT / "catalog.json"
ENTRIES = ROOT / "entries"
REFERENCIAS = Path(__file__).resolve().parent / "_referencias"
SOURCES = Path(__file__).resolve().parent / "sources.txt"

# Nombres de artefactos estándar a buscar. Ruta relativa dentro del repo -> slug del catálogo.
# Los slugs deben coincidir con los del catalog.json cuando ya existen.
KNOWN_ARTIFACTS: dict[str, str] = {
    "README.md": "readme",
    "LICENSE": "license",
    "LICENSE.md": "license",
    ".gitignore": "gitignore",
    ".editorconfig": "editorconfig",
    "CONTRIBUTING.md": "contributing",
    "CHANGELOG.md": "changelog",
    "SECURITY.md": "security",
    "AGENTS.md": "agents-md",
    "Makefile": "makefile",
    "UPSTREAM.md": "upstream",
    ".env.example": "env-example",
    # Artefactos que Prowler tiene y que aún pueden no estar en el catálogo:
    "CODE_OF_CONDUCT.md": "code-of-conduct",
    ".pre-commit-config.yaml": "pre-commit",
    "Dockerfile": "dockerfile",
    ".github/CODEOWNERS": "codeowners",
    ".github/pull_request_template.md": "pull-request-template",
    ".dockerignore": "dockerignore",
}


def sh(cmd: list[str]) -> tuple[int, str]:
    """Ejecuta un comando y devuelve (returncode, stdout)."""
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.returncode, p.stdout


def gh_file(repo: str, path: str) -> str | None:
    """Devuelve el contenido de un archivo del repo vía gh api, o None si no existe."""
    code, out = sh(["gh", "api", f"repos/{repo}/contents/{path}", "--jq", ".content"])
    if code != 0 or not out.strip():
        return None
    try:
        return base64.b64decode(out).decode("utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        return None


def gh_exists(repo: str, path: str) -> bool:
    code, out = sh(["gh", "api", f"repos/{repo}/contents/{path}", "--jq", ".name"])
    return code == 0 and bool(out.strip())


def load_catalog_slugs() -> set[str]:
    if not CATALOG.exists():
        return set()
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    return {e["slug"] for e in data.get("entries", [])}


def load_sources(cli_repos: list[str]) -> list[str]:
    if cli_repos:
        return cli_repos
    if SOURCES.exists():
        return [ln.strip() for ln in SOURCES.read_text(encoding="utf-8").splitlines()
                if ln.strip() and not ln.strip().startswith("#")]
    return []


def scan_repo(repo: str, catalog_slugs: set[str]) -> list[dict]:
    """Descubre artefactos en un repo y los clasifica frente al catálogo."""
    findings = []
    seen_slugs = set()
    for path, slug in KNOWN_ARTIFACTS.items():
        if slug in seen_slugs:
            # Ya encontramos este slug por otra ruta (ej. LICENSE vs LICENSE.md)
            if not gh_exists(repo, path):
                continue
        if not gh_exists(repo, path):
            continue
        seen_slugs.add(slug)
        status = "YA_TIENES" if slug in catalog_slugs else "NUEVO"
        # Los YA_TIENES son candidatos a MEJORA (hay una referencia externa que comparar)
        classification = "MEJORA?" if status == "YA_TIENES" else "NUEVO"
        findings.append({
            "repo": repo,
            "path": path,
            "slug": slug,
            "status": status,
            "classification": classification,
        })
    return findings


def download_references(repo: str, findings: list[dict]) -> None:
    """Descarga los archivos encontrados a _referencias/<repo>/ como material de consulta."""
    dest = REFERENCIAS / repo.replace("/", "__")
    dest.mkdir(parents=True, exist_ok=True)
    for f in findings:
        content = gh_file(repo, f["path"])
        if content is None:
            continue
        # Aplanar la ruta para el nombre de archivo de referencia.
        fname = f["path"].replace("/", "__")
        (dest / fname).write_text(content, encoding="utf-8")
    # Nota de procedencia (para no confundir referencia con plantilla propia).
    (dest / "_PROCEDENCIA.txt").write_text(
        f"Ejemplos descargados de https://github.com/{repo}\n"
        "SON REFERENCIA, no plantillas propias. Generalizar antes de usar (quitar lo\n"
        "específico del repo fuente, dejar placeholders). Respetar su licencia.\n",
        encoding="utf-8",
    )


_FICHA_BORRADOR = """---
slug: {slug}
title: {artifact} — (completar)
artifact: {artifact}
problem: >
  TODO: en una frase, qué aporta este archivo al proyecto.
applies_to:
  - TODO: situación donde SÍ conviene
not_for:
  - TODO: situación donde NO hace falta
tags: [TODO]
template: null
owner_source: null
status: BORRADOR
---

# {artifact}

> Ficha SEMBRADA por artefacto_scan desde: {repo} (`{path}`).
> Ejemplo de referencia en `tools/_referencias/{repo_flat}/{path_flat}`.
> GENERALIZAR antes de dar por buena: quitar lo específico del repo fuente.

## Qué es

TODO.

## Cuándo SÍ aplica

- TODO.

## Cuándo NO aplica

- TODO.

## Cómo usarlo

TODO: crear `templates/<archivo>` genérico y apuntar aquí.

## Fuente / plantilla

- Referencia descargada: `tools/_referencias/{repo_flat}/{path_flat}`
- Fuente original: https://github.com/{repo}
"""


def seed_drafts(findings: list[dict]) -> list[str]:
    """Crea fichas BORRADOR para los artefactos NUEVO que no tengan ficha aún."""
    created = []
    for f in findings:
        if f["status"] != "NUEVO":
            continue
        ficha = ENTRIES / f"{f['slug']}.md"
        if ficha.exists():
            continue
        ficha.write_text(
            _FICHA_BORRADOR.format(
                slug=f["slug"],
                artifact=Path(f["path"]).name,
                repo=f["repo"],
                path=f["path"],
                repo_flat=f["repo"].replace("/", "__"),
                path_flat=f["path"].replace("/", "__"),
            ),
            encoding="utf-8",
        )
        created.append(str(ficha.relative_to(ROOT)))
    return created


def main() -> None:
    ap = argparse.ArgumentParser(description="Descubre artefactos en repos de referencia.")
    ap.add_argument("--repo", action="append", default=[],
                    help="Repo owner/name (repetible). Si se omite, usa sources.txt.")
    ap.add_argument("--seed", action="store_true",
                    help="Crea fichas BORRADOR de los artefactos NUEVO.")
    ap.add_argument("--no-download", action="store_true",
                    help="No descargar los ejemplos de referencia.")
    ap.add_argument("--json", action="store_true", help="Salida en JSON.")
    args = ap.parse_args()

    repos = load_sources(args.repo)
    if not repos:
        print("No hay repos. Usa --repo owner/name o crea sources.txt.", file=sys.stderr)
        sys.exit(1)

    catalog_slugs = load_catalog_slugs()
    all_findings: list[dict] = []
    seeded: list[str] = []

    for repo in repos:
        findings = scan_repo(repo, catalog_slugs)
        all_findings.extend(findings)
        if not args.no_download:
            download_references(repo, findings)
        if args.seed:
            seeded.extend(seed_drafts(findings))

    if args.json:
        print(json.dumps({"findings": all_findings, "seeded": seeded}, indent=2))
        return

    # Reporte legible
    nuevos = [f for f in all_findings if f["status"] == "NUEVO"]
    tienes = [f for f in all_findings if f["status"] == "YA_TIENES"]
    print(f"\n=== artefacto_scan — {len(repos)} repo(s), {len(all_findings)} hallazgos ===\n")
    print(f"NUEVO (no está en tu catálogo): {len(nuevos)}")
    for f in nuevos:
        print(f"  + {f['slug']:22} ({f['path']})  ← {f['repo']}")
    print(f"\nYA_TIENES (candidato a MEJORA, compara con la referencia): {len(tienes)}")
    for f in tienes:
        print(f"  ~ {f['slug']:22} ({f['path']})  ← {f['repo']}")
    if not args.no_download:
        print(f"\nEjemplos de referencia en: {REFERENCIAS.relative_to(ROOT.parent)}/")
    if args.seed:
        print(f"\nFichas BORRADOR creadas: {len(seeded)}")
        for s in seeded:
            print(f"  · {s}")
    elif nuevos:
        print("\n(usa --seed para crear fichas BORRADOR de los NUEVO)")
    print("\nRecuerda: los ejemplos son REFERENCIA; generaliza antes de crear la plantilla.\n")


if __name__ == "__main__":
    main()
