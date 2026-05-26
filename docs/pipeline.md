# Pipeline CI/CD

## Descripción general

El pipeline automatiza el ciclo completo desde un `git push`
hasta la verificación en producción. Está definido en
`.github/workflows/ci-cd.yml` y corre en GitHub Actions.

---

## Jobs y orden de ejecución
git push
│
├──► [test]   pytest + coverage (mínimo 90%)
│
└──► [lint]   flake8 + bandit + pip-audit
│
└──► [build]  Docker image → artefacto
│
└──► [integration]  docker compose + curl
│
└──► [deploy]  solo en main

## Detalle de cada job

### 1. test
- Instala dependencias con cache de pip
- Corre `pytest` con cobertura mínima del 90%
- Genera `coverage.xml` como artefacto descargable
- **Si falla**: el job `build` no se ejecuta

### 2. lint
- `flake8` — estilo y errores de sintaxis (max 100 chars)
- `bandit` — vulnerabilidades en el código fuente
- `pip-audit` — CVEs en dependencias
- Genera `bandit-report.json` como artefacto
- **Si falla**: el job `build` no se ejecuta

### 3. build
- Requiere que `test` y `lint` hayan pasado (`needs: [test, lint]`)
- Construye imagen Docker con BuildKit y caché de GitHub Actions
- Etiqueta la imagen con el SHA corto del commit
- Exporta la imagen como artefacto `.tar` con retención de 7 días

### 4. integration
- Descarga la imagen construida en el job anterior
- Levanta el stack completo con `docker compose up`
- Espera hasta 60 segundos a que la API esté lista
- Verifica los endpoints: `/`, `/tasks`, `/health`
- Baja el stack al finalizar

### 5. deploy
- Solo se ejecuta en la rama `main` con evento `push`
- Genera un resumen en GitHub con commit, rama, actor y timestamp

---

## Artefactos generados

| Artefacto | Contenido | Retención |
|-----------|-----------|-----------|
| `coverage-report` | `coverage.xml` con cobertura de tests | 90 días |
| `security-report` | `bandit-report.json` con análisis | 90 días |
| `docker-image-{sha}` | Imagen Docker exportada como `.tar` | 7 días |

---

## Variables de entorno requeridas

No se requieren secrets para el pipeline base. Si se añade
publicación a Docker Hub, agregar en Settings → Secrets:

| Secret | Descripción |
|--------|-------------|
| `DOCKERHUB_USERNAME` | Usuario de Docker Hub |
| `DOCKERHUB_TOKEN` | Access token (no contraseña) |
