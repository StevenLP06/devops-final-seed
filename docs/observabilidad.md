# Observabilidad

## Los tres pilares implementados

### 1. Logs estructurados (JSON)

Implementados con `python-json-logger`. Cada log incluye:

```json
{
  "asctime": "2026-05-25T10:31:02",
  "levelname": "INFO",
  "name": "todo_api",
  "message": "Tarea creada",
  "task_id": 47,
  "title": "Aprender DevOps"
}
```

| Nivel | Cuándo se emite |
|-------|----------------|
| INFO | Operaciones exitosas |
| WARNING | Recursos no encontrados (404) |
| ERROR | Fallos de sistema (DB caída) |

---

### 2. Métricas (Prometheus)

Expuestas en `/metrics`. Prometheus scraping cada 15 segundos.

#### Métricas automáticas (flask-exporter)
| Métrica | Tipo | Descripción |
|---------|------|-------------|
| `flask_http_request_duration_seconds` | Histogram | Latencia por endpoint |
| `flask_http_request_total` | Counter | Total de requests |
| `flask_exporter_info` | Gauge | Versión del exporter |

#### Métricas custom
| Métrica | Tipo | Descripción |
|---------|------|-------------|
| `tasks_created_total` | Counter | Total de tareas creadas |

---

### 3. Health Check

Endpoint `/health` verifica:
- Que la aplicación está corriendo
- Que la base de datos responde (`SELECT 1`)

**Respuesta exitosa (200):**
```json
{
  "status": "healthy",
  "db": "connected",
  "version": "1.0.0"
}
```

**Respuesta fallida (503):**
```json
{
  "status": "unhealthy",
  "db": "disconnected",
  "error": "mensaje del error"
}
```

---

## Stack de observabilidad
To-Do API → /metrics → Prometheus → Grafana
↓
Dashboards:
- Requests por endpoint
- Latencia p50/p95/p99
- Tasa de errores
- Tareas creadas
- Health check status

## Acceso

| Servicio | URL | Credenciales |
|----------|-----|-------------|
| API | http://localhost:5000 | — |
| Prometheus | http://localhost:9090 | — |
| Grafana | http://localhost:3000 | admin / devops2024 |
