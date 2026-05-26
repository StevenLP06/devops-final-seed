from flask import Flask, request, jsonify
import sqlite3
import os
import logging
from pythonjsonlogger import jsonlogger
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import REGISTRY, Counter


# ─── Logging estructurado JSON ────────────────────────────────────────────────
logger = logging.getLogger("todo_api")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


# ─── App Flask ────────────────────────────────────────────────────────────────
app = Flask(__name__)
metrics = PrometheusMetrics(app)


# Reutiliza el contador si ya fue registrado (evita error en tests)
if "tasks_created_total" not in REGISTRY._names_to_collectors:
    tasks_created_counter = Counter(
        "tasks_created_total",
        "Número total de tareas creadas"
    )
else:
    tasks_created_counter = REGISTRY._names_to_collectors["tasks_created_total"]

DB_PATH = os.environ.get("DB_PATH", "tasks.db")


# ─── Base de datos ────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            completed BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Base de datos inicializada", extra={"db_path": DB_PATH})


init_db()


# ─── Endpoints de observabilidad ──────────────────────────────────────────────
@app.route("/health", methods=["GET"])
def health():
    """Verifica que la app y la DB estén operativas."""
    try:
        conn = get_db()
        conn.execute("SELECT 1")
        conn.close()
        logger.info("Health check OK")
        return jsonify({
            "status": "healthy",
            "db": "connected",
            "version": "1.0.0"
        }), 200
    except Exception as e:
        logger.error("Health check FAILED", extra={"error": str(e)})
        return jsonify({
            "status": "unhealthy",
            "db": "disconnected",
            "error": str(e)
        }), 503


# ─── Endpoints de la API ──────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def index():
    logger.info("API info solicitada")
    return jsonify({
        "name": "To-Do API",
        "version": "1.0.0",
        "endpoints": ["/tasks", "/health", "/metrics"]
    })


@app.route("/tasks", methods=["GET"])
def list_tasks():
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    conn.close()
    result = [dict(t) for t in tasks]
    logger.info("Tareas listadas", extra={"count": len(result)})
    return jsonify(result)


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    if not data or "title" not in data:
        logger.warning("Intento de crear tarea sin título")
        return jsonify({"error": "El campo 'title' es obligatorio"}), 400

    title = data["title"]
    description = data.get("description", "")

    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO tasks (title, description) VALUES (?, ?)",
        (title, description),
    )
    task_id = cursor.lastrowid
    conn.commit()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()

    tasks_created_counter.inc()
    logger.info("Tarea creada", extra={"task_id": task_id, "title": title})
    return jsonify(dict(task)), 201


@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if task is None:
        logger.warning("Tarea no encontrada", extra={"task_id": task_id})
        return jsonify({"error": "Tarea no encontrada"}), 404
    logger.info("Tarea obtenida", extra={"task_id": task_id})
    return jsonify(dict(task))


@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.get_json()
    if not data:
        logger.warning("PUT sin datos", extra={"task_id": task_id})
        return jsonify({"error": "No se enviaron datos"}), 400

    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        conn.close()
        logger.warning("PUT tarea inexistente", extra={"task_id": task_id})
        return jsonify({"error": "Tarea no encontrada"}), 404

    title = data.get("title", task["title"])
    description = data.get("description", task["description"])
    completed = data.get("completed", task["completed"])

    conn.execute(
        "UPDATE tasks SET title=?, description=?, completed=? WHERE id=?",
        (title, description, completed, task_id),
    )
    conn.commit()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    logger.info("Tarea actualizada", extra={"task_id": task_id})
    return jsonify(dict(task))


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        conn.close()
        logger.warning("DELETE tarea inexistente", extra={"task_id": task_id})
        return jsonify({"error": "Tarea no encontrada"}), 404

    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    logger.info("Tarea eliminada", extra={"task_id": task_id})
    return jsonify({"message": "Tarea eliminada"}), 200


if __name__ == "__main__":  # pragma: no cover
    port = int(os.environ.get("PORT", 5000))
    logger.info("Iniciando To-Do API", extra={"port": port})
    app.run(host="0.0.0.0", port=port) # nosec B104
