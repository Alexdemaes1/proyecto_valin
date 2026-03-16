# Valin v2 — Documentación Técnica

## Arquitectura

```
valin.py                  → Entry point Flask (create_app + run)
db/                       → Capa de datos (sqlite3 directo)
  connection.py           → get_db(), close_db(), init_db()
  queries_auth.py         → Login, roles, admin
  queries_maestros.py     → CRUD vehículos, conductores, granjas
  queries_operaciones.py  → Planificaciones, viajes, frigos, aldi
  queries_rrhh.py         → Jornadas, horarios
routes/                   → Blueprints Flask
  __init__.py             → login_required decorator
  auth.py                 → Login / logout
  dashboard.py            → Config + import + sync + backups
  maestros.py             → CRUD datos maestros
  viajes.py               → Planificación pollo vivo (completo)
  frigos.py               → Listado frigoríficos (solo lectura)
  aldi.py                 → Listado Aldi (solo lectura)
  rrhh.py                 → Generación de jornadas + horarios
engines/                  → Lógica de negocio (sin Flask)
  viajes_engine.py        → Cálculo cronológico inverso
  rrhh_engine.py          → Nocturnidad, dietas
  frigos_engine.py        → Descripción trayectos (utilidad futura)
  aldi_engine.py          → Descripción trayectos Aldi (utilidad futura)
services/                 → Servicios del sistema
  config_manager.py       → Lee/escribe config.json + validación
  backup_manager.py       → Crear/listar/restaurar backups (sqlite3.backup)
  import_excel.py         → Importar maestros desde Excel
  sync_drive.py           → Push/pull con Google Drive + lock
templates/                → HTML con Jinja2
static/css/style.css      → Estilos CSS
schema.sql                → Esquema SQLite (13 tablas)
```

## Principios

1. **sqlite3 directo** — Sin ORM. Queries en `db/queries_*.py`.
2. **Engines desacoplados** — `engines/` no importa Flask ni DB.
3. **Config local** — `config.json` ignorada en Git. Cada PC tiene la suya.
4. **Rutas relativas** — `BASE_DIR = os.path.dirname(os.path.abspath(__file__))`.
5. **DB siempre local** — Nunca abre SQLite en Drive. Sync = copia de archivo.

## Estado de módulos

| Módulo | Estado | Detalle |
|---|---|---|
| Auth | ✅ Completo | Login/logout, sesiones, admin auto-creado |
| Dashboard | ✅ Completo | Config con validación, import, sync, backups |
| Maestros | ✅ Completo | CRUD vehículos, conductores, granjas |
| Viajes | ✅ Completo | Planificación + viajes + cálculo inverso |
| RRHH | ✅ Completo | Jornadas, nocturnidad, dietas |
| Frigos | ⚠️ Solo listado | Ruta, queries y engine existen. Falta formulario de edición |
| Aldi | ⚠️ Solo listado | Ruta, queries y engine existen. Falta formulario de edición |

## Añadir un módulo

1. Tabla en `schema.sql` (`CREATE TABLE IF NOT EXISTS`)
2. `db/queries_modulo.py` con funciones SQL
3. `routes/modulo.py` con Blueprint
4. Registrar en `valin.py` (`app.register_blueprint(...)`)
5. Templates en `templates/modulo/`
6. Enlace en `templates/base.html` (navbar)

## Completar Frigos/Aldi

Para hacerlos 100% funcionales:
1. Crear `templates/frigos/plan.html` (formulario como `viajes/plan.html`)
2. Añadir rutas de crear/editar/eliminar en `routes/frigos.py`
3. Los queries ya existen: `crear_frigo()`, `listar_frigos_plan()` en `queries_operaciones.py`
4. Lo mismo para Aldi con `crear_aldi()`, `listar_aldis_plan()`

## Tests

```bash
python -m pytest tests/ -v
```

## Dependencias

| Paquete | Uso |
|---|---|
| Flask 3.0 | Servidor web + Jinja2 |
| Werkzeug | Hash de contraseñas (viene con Flask) |
| openpyxl | Lectura de Excel |
