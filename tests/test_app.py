"""
Tests unitarios para la Tasks API (seed original).
Ejecutar: pytest tests/ -v --cov=src

Estrategia de aislamiento:
  - Cada test recibe su propia base de datos SQLite en un archivo temporal.
  - Se parchea DB_PATH del módulo app antes de cargarlo para que
    init_db() y get_db() apunten al archivo temporal.
  - Al finalizar cada test se elimina el archivo temporal.
"""
import os
import sys
import tempfile
import importlib
import pytest

SRC = os.path.join(os.path.dirname(__file__), "..", "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)


@pytest.fixture
def client():
    """
    Fixture principal: crea una DB temporal, recarga el módulo app
    apuntando a esa DB y devuelve un cliente de test Flask.
    """
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.environ["DB_PATH"] = db_path

    import app as app_module
    importlib.reload(app_module)

    with app_module.app.test_client() as c:
        yield c

    os.environ.pop("DB_PATH", None)
    os.close(db_fd)
    os.unlink(db_path)


# ── Test 1 — GET / devuelve información de la API ────────────────────────────
def test_index_devuelve_info_api(client):
    resp = client.get("/")
    data = resp.get_json()

    assert resp.status_code == 200
    assert data["name"] == "To-Do API"
    assert "version" in data
    assert "endpoints" in data


# ── Test 2 — GET /tasks devuelve lista vacía al inicio ───────────────────────
def test_list_tasks_vacia_al_inicio(client):
    resp = client.get("/tasks")
    data = resp.get_json()

    assert resp.status_code == 200
    assert isinstance(data, list)
    assert len(data) == 0


# ── Test 3 — POST /tasks crea una tarea correctamente ────────────────────────
def test_crear_tarea_exitoso(client):
    payload = {"title": "Estudiar Docker", "description": "Dockerfile y compose"}
    resp = client.post("/tasks", json=payload)
    data = resp.get_json()

    assert resp.status_code == 201
    assert data["title"] == "Estudiar Docker"
    assert data["description"] == "Dockerfile y compose"
    assert data["completed"] in (0, False)   # el seed usa 'completed', no 'done'
    assert "id" in data
    assert "created_at" in data


# ── Test 4 — POST /tasks sin 'title' devuelve 400 ────────────────────────────
def test_crear_tarea_sin_titulo_retorna_400(client):
    resp = client.post("/tasks", json={"description": "sin título"})
    data = resp.get_json()

    assert resp.status_code == 400
    assert "error" in data


# ── Test 5 — GET /tasks/<id> devuelve la tarea correcta ─────────────────────
def test_obtener_tarea_por_id(client):
    created = client.post("/tasks", json={"title": "Mi tarea"}).get_json()
    task_id = created["id"]

    resp = client.get(f"/tasks/{task_id}")
    data = resp.get_json()

    assert resp.status_code == 200
    assert data["id"] == task_id
    assert data["title"] == "Mi tarea"


# ── Test 6 — GET /tasks/<id> inexistente devuelve 404 ────────────────────────
def test_obtener_tarea_inexistente_retorna_404(client):
    resp = client.get("/tasks/99999")
    data = resp.get_json()

    assert resp.status_code == 404
    assert "error" in data


# ── Test 7 — PUT /tasks/<id> actualiza título y campo completed ──────────────
def test_actualizar_tarea(client):
    created = client.post("/tasks", json={"title": "Original"}).get_json()
    task_id = created["id"]

    resp = client.put(f"/tasks/{task_id}", json={"title": "Actualizada", "completed": 1})
    data = resp.get_json()

    assert resp.status_code == 200
    assert data["title"] == "Actualizada"
    assert data["completed"] in (1, True)

# ── Test 8 — PUT /tasks/<id> con body vacío devuelve 400 ─────────────────────
def test_actualizar_sin_datos_retorna_400(client):
    created = client.post("/tasks", json={"title": "Para actualizar"}).get_json()
    task_id = created["id"]

    # El seed valida que el body no sea None ni vacío -> 400
    resp = client.put(f"/tasks/{task_id}", json={})
    assert resp.status_code == 400
    assert "error" in resp.get_json()


# ── Test 9 — DELETE /tasks/<id> elimina la tarea ─────────────────────────────
def test_eliminar_tarea(client):
    created = client.post("/tasks", json={"title": "Para borrar"}).get_json()
    task_id = created["id"]

    resp = client.delete(f"/tasks/{task_id}")
    assert resp.status_code == 200
    assert "message" in resp.get_json()

    # Confirmar que ya no existe
    assert client.get(f"/tasks/{task_id}").status_code == 404


# ── Test 10 — DELETE /tasks/<id> inexistente devuelve 404 ────────────────────
def test_eliminar_tarea_inexistente_retorna_404(client):
    resp = client.delete("/tasks/99999")
    assert resp.status_code == 404


# ── Test 11 — Flujo CRUD completo end-to-end ─────────────────────────────────
def test_flujo_crud_completo(client):
    # Crear
    task = client.post("/tasks", json={
        "title": "Tarea CRUD",
        "description": "Prueba completa",
    }).get_json()
    task_id = task["id"]

    # Listar — debe aparecer
    lista = client.get("/tasks").get_json()
    assert any(t["id"] == task_id for t in lista)

    # Leer individualmente
    assert client.get(f"/tasks/{task_id}").status_code == 200

    # Actualizar
    updated = client.put(f"/tasks/{task_id}", json={"completed": 1}).get_json()
    assert updated["completed"] in (1, True)

    # Eliminar y confirmar
    client.delete(f"/tasks/{task_id}")
    assert client.get(f"/tasks/{task_id}").status_code == 404

# ── Test 12 — PUT /tasks/<id> inexistente devuelve 404 ───────────────────────
def test_actualizar_tarea_inexistente_retorna_404(client):
    resp = client.put("/tasks/99999", json={"title": "No existe"})
    data = resp.get_json()

    assert resp.status_code == 404
    assert "error" in data