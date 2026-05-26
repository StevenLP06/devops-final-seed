# CALMS — Marco Cultural de DevOps

CALMS es el framework que describe los pilares culturales de DevOps.
Este documento explica cómo cada pilar se aplicó en este proyecto.

---

## C — Culture (Cultura)

DevOps comienza con un cambio cultural: romper los silos entre
desarrollo y operaciones. En este proyecto esto se refleja en:

- El código, los tests, la infraestructura y los pipelines viven
  en el **mismo repositorio** — no hay equipo separado de "ops".
- Cada cambio pasa por revisión automática antes de llegar a producción.
- Los errores del pipeline son visibles para todo el equipo en tiempo real.

---

## A — Automation (Automatización)

Automatizar todo lo repetible para eliminar errores humanos:

| Tarea | Herramienta | Cuándo |
|-------|-------------|--------|
| Correr tests | GitHub Actions | Cada push |
| Análisis de seguridad | Bandit + pip-audit | Cada push |
| Build de imagen Docker | Docker Buildx | Tras tests verdes |
| Test de integración | docker compose + curl | Tras build |
| Lint de código | Flake8 | Cada push |

---

## L — Lean

Eliminar desperdicio y entregar valor en ciclos cortos:

- **Pipeline en cascada**: si los tests fallan, el build no corre.
  No se desperdician recursos construyendo código roto.
- **Imagen Docker multi-stage**: el builder es separado del runtime,
  reduciendo el tamaño final de la imagen.
- **SQLite**: base de datos sin servidor, sin configuración adicional.
  Simple para el alcance del proyecto.
- **Health check cada 30s**: detección temprana de fallos sin
  intervención manual.

---

## M — Measurement (Medición)

No se puede mejorar lo que no se mide:

| Métrica | Herramienta | Dónde se ve |
|---------|-------------|-------------|
| Cobertura de tests | pytest-cov | Terminal / CI report |
| Requests por segundo | Prometheus | `/metrics` |
| Latencia p50/p95/p99 | Prometheus | Grafana dashboard |
| Tasa de errores 4xx/5xx | Prometheus | Grafana dashboard |
| Tareas creadas | Counter custom | Grafana dashboard |
| Estado de salud | `/health` | Docker healthcheck |

---

## S — Sharing (Compartir)

El conocimiento compartido acelera a todo el equipo:

- Este repositorio contiene **toda la documentación** necesaria
  para entender, correr y mantener el sistema.
- Los logs son **JSON estructurado** — cualquier herramienta puede
  consumirlos sin conocimiento previo del sistema.
- El `Makefile` unifica los comandos: `make test`, `make lint`,
  `make all` — sin necesidad de conocer los flags internos.
- El `docker compose up` levanta el stack completo en un comando.
