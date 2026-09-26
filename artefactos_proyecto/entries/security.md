---
slug: security
title: SECURITY.md — política de seguridad y reporte de vulnerabilidades
artifact: SECURITY.md
problem: >
  Indica cómo reportar una vulnerabilidad de forma privada y qué versiones se soportan,
  para que los fallos de seguridad no se publiquen en issues abiertos.
applies_to:
  - proyecto público que otros pueden usar
  - servicios expuestos, MCP servers, apps con auth/secretos
  - repos donde recibir reportes de seguridad tiene sentido
not_for:
  - scripts personales privados sin usuarios externos
tags: [security, vulnerabilidades, reporte, disclosure, seguridad]
template: templates/SECURITY.md
owner_source: null
status: ESTABLE
---

# SECURITY.md

## Qué es

Documento (raíz o `.github/`) que explica **cómo reportar una vulnerabilidad en privado**
(no en issues públicos) y **qué versiones reciben parches**. GitHub lo reconoce y muestra
un enlace "Report a vulnerability".

## Cuándo SÍ aplica

- Proyecto público con usuarios.
- Servicios/MCP expuestos, apps con autenticación o secretos.

## Cuándo NO aplica

- Scripts personales privados sin terceros.

## Cómo usarlo

Copiar `templates/SECURITY.md`, poner un canal de contacto privado (email o GitHub
Security Advisories) y las versiones soportadas. No usar issues públicos para 0-days.

## Fuente / plantilla

- Plantilla: `templates/SECURITY.md`
- Nota del ecosistema: relevante para MCP servers expuestos (recordar el aviso de la
  vuln RCE de Flowise self-hosted registrado en tus learnings).
