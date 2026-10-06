# Dockerfile — esqueleto genérico. Elige la imagen base de TU lenguaje y ajusta.
# Buenas prácticas: fijar versiones (no :latest), usuario no-root, .dockerignore.

# --- Imagen base (CAMBIAR por tu runtime; ejemplos comentados) ---
FROM IMAGEN_BASE:VERSION
# FROM python:3.12-slim
# FROM node:22-slim
# FROM golang:1.23 AS build   # (multi-stage para binarios)

# Zona horaria / entorno (opcional)
ENV TZ=America/Guayaquil \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1) Dependencias primero (mejor cache): copia solo el manifiesto y resuélvelo.
COPY MANIFIESTO_DE_DEPS ./
RUN COMANDO_INSTALAR_DEPS
# ej. Python:  COPY pyproject.toml ./ && RUN pip install --no-cache-dir .
# ej. Node:    COPY package*.json ./ && RUN npm ci

# 2) Código
COPY . .

# 3) Usuario no-root (recomendado)
RUN useradd --create-home appuser
USER appuser

# 4) Puerto que expone el servicio (si aplica)
# EXPOSE 8080

# 5) Comando de arranque
CMD ["COMANDO", "DE", "ARRANQUE"]
# ej. ["python", "-m", "mi_paquete"]
