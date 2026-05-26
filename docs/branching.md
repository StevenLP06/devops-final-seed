# Estrategia de Branching

## Modelo adoptado: GitHub Flow simplificado

Se eligió GitHub Flow por su simplicidad y compatibilidad con
pipelines de CI/CD continuos.

---

## Ramas principales

| Rama | Propósito | Pipeline |
|------|-----------|----------|
| `main` | Código en producción. Siempre estable. | CI completo + deploy |
| `dev` | Integración de features en desarrollo. | CI completo |

## Ramas de trabajo

| Tipo | Nomenclatura | Ejemplo |
|------|-------------|---------|
| Nueva funcionalidad | `feature/descripcion` | `feature/add-auth` |
| Corrección de bug | `fix/descripcion` | `fix/health-endpoint` |
| Hotfix urgente | `hotfix/descripcion` | `hotfix/db-connection` |
| Documentación | `docs/descripcion` | `docs/update-readme` |

---

## Flujo de trabajo
1. Crear rama desde dev: git checkout dev, git checkout -b feature/nueva-funcionalidad
2. Desarrollar y commitear: git add . , git commit -m "feat: descripción del cambio"
3. Push y abrir Pull Request hacia dev: git push origin feature/nueva-funcionalidad
4. El pipeline corre automáticamente en el PR.
5. Si el pipeline pasa → merge a dev.
6. Cuando dev está estable → PR de dev a main.
7. El pipeline corre en main → deploy automático.

---

## Convención de commits

Seguimos **Conventional Commits**:

| Prefijo | Cuándo usarlo |
|---------|---------------|
| `feat:` | Nueva funcionalidad |
| `fix:` | Corrección de bug |
| `ci:` | Cambios en pipeline |
| `docs:` | Solo documentación |
| `test:` | Agregar o corregir tests |
| `refactor:` | Refactorización sin cambio funcional |
| `chore:` | Mantenimiento general |

### Ejemplos
feat: agregar endpoint DELETE /tasks
fix: corregir validación de title vacío
ci: agregar job de integración al pipeline
docs: documentar estrategia de branching
test: agregar test para health check fallido
