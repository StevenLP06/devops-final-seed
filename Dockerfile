# ── Etapa 1: builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Copiar e instalar dependencias en una capa separada (cache eficiente)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Etapa 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

# Metadatos de la imagen
LABEL maintainer="stlopezp@unal.edu.co"
LABEL version="1.0.0"
LABEL description="To-Do API — Proyecto Final DevOps"

# Usuario no-root por seguridad (buena práctica DevOps)
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copiar dependencias instaladas desde el builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copiar código fuente
COPY src/ ./src/

# Crear directorio para la base de datos con permisos correctos
RUN mkdir -p /app/data && chown -R appuser:appuser /app

# Cambiar al usuario no-root
USER appuser

# Variables de entorno por defecto
ENV PORT=5000
ENV DB_PATH=/app/data/tasks.db
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Puerto expuesto
EXPOSE 5000

# Health check nativo de Docker
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

# Comando de inicio
CMD ["python", "src/app.py"]