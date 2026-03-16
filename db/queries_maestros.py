"""
Queries CRUD para datos maestros: vehículos, conductores, granjas, rutas frigo, tiendas.
"""

from db.connection import get_db


# ─── VEHÍCULOS ──────────────────────────────────────────────────
def listar_vehiculos(solo_activos=True):
    db = get_db()
    sql = "SELECT * FROM vehiculos"
    if solo_activos:
        sql += " WHERE activo = 1"
    sql += " ORDER BY codigo_interno"
    return db.execute(sql).fetchall()


def obtener_vehiculo(id):
    return get_db().execute("SELECT * FROM vehiculos WHERE id = ?", (id,)).fetchone()


def crear_vehiculo(codigo_interno, matricula_tractora='', matricula_semirremolque='', observaciones=''):
    db = get_db()
    db.execute(
        "INSERT INTO vehiculos (codigo_interno, matricula_tractora, matricula_semirremolque, observaciones) "
        "VALUES (?, ?, ?, ?)",
        (codigo_interno, matricula_tractora, matricula_semirremolque, observaciones)
    )
    db.commit()


def actualizar_vehiculo(id, **campos):
    db = get_db()
    partes = []
    valores = []
    for campo, valor in campos.items():
        partes.append(f"{campo} = ?")
        valores.append(valor)
    partes.append("updated_at = datetime('now')")
    valores.append(id)
    db.execute(f"UPDATE vehiculos SET {', '.join(partes)} WHERE id = ?", valores)
    db.commit()


def eliminar_vehiculo(id):
    db = get_db()
    db.execute("DELETE FROM vehiculos WHERE id = ?", (id,))
    db.commit()


# ─── CONDUCTORES ────────────────────────────────────────────────
def listar_conductores(solo_activos=True):
    db = get_db()
    sql = "SELECT * FROM conductores"
    if solo_activos:
        sql += " WHERE activo = 1"
    sql += " ORDER BY alias"
    return db.execute(sql).fetchall()


def obtener_conductor(id):
    return get_db().execute("SELECT * FROM conductores WHERE id = ?", (id,)).fetchone()


def crear_conductor(alias, codigo_alfabetico='', nombre_legal='', dni='',
                    telefono='', empresa='', notas=''):
    db = get_db()
    db.execute(
        "INSERT INTO conductores (alias, codigo_alfabetico, nombre_legal, dni, telefono, empresa, notas) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (alias, codigo_alfabetico, nombre_legal, dni, telefono, empresa, notas)
    )
    db.commit()


def actualizar_conductor(id, **campos):
    db = get_db()
    partes = []
    valores = []
    for campo, valor in campos.items():
        partes.append(f"{campo} = ?")
        valores.append(valor)
    partes.append("updated_at = datetime('now')")
    valores.append(id)
    db.execute(f"UPDATE conductores SET {', '.join(partes)} WHERE id = ?", valores)
    db.commit()


# ─── GRANJAS ────────────────────────────────────────────────────
def listar_granjas(solo_activos=True):
    db = get_db()
    sql = "SELECT * FROM granjas"
    if solo_activos:
        sql += " WHERE activo = 1"
    sql += " ORDER BY codigo"
    return db.execute(sql).fetchall()


def obtener_granja(id):
    return get_db().execute("SELECT * FROM granjas WHERE id = ?", (id,)).fetchone()


def crear_granja(codigo, nombre_cliente='DESCONOCIDO', localidad='',
                 plantas=1, tiempo_trayecto_min=120, tiempo_carga_min=60,
                 telefono_1='', telefono_2='', ubicacion_url='', anotaciones=''):
    db = get_db()
    db.execute(
        "INSERT INTO granjas (codigo, nombre_cliente, localidad, plantas, "
        "tiempo_trayecto_min, tiempo_carga_min, telefono_1, telefono_2, ubicacion_url, anotaciones) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (codigo, nombre_cliente, localidad, plantas,
         tiempo_trayecto_min, tiempo_carga_min,
         telefono_1, telefono_2, ubicacion_url, anotaciones)
    )
    db.commit()


def actualizar_granja(id, **campos):
    db = get_db()
    partes = []
    valores = []
    for campo, valor in campos.items():
        partes.append(f"{campo} = ?")
        valores.append(valor)
    partes.append("updated_at = datetime('now')")
    valores.append(id)
    db.execute(f"UPDATE granjas SET {', '.join(partes)} WHERE id = ?", valores)
    db.commit()


# ─── RUTAS FRIGO ────────────────────────────────────────────────
def listar_rutas_frigo(solo_activos=True):
    db = get_db()
    sql = "SELECT * FROM rutas_frigo"
    if solo_activos:
        sql += " WHERE activo = 1"
    sql += " ORDER BY codigo_ruta"
    return db.execute(sql).fetchall()


def obtener_ruta_frigo(id):
    return get_db().execute("SELECT * FROM rutas_frigo WHERE id = ?", (id,)).fetchone()


# ─── TIENDAS ────────────────────────────────────────────────────
def listar_tiendas(solo_activos=True):
    db = get_db()
    sql = "SELECT * FROM tiendas"
    if solo_activos:
        sql += " WHERE activo = 1"
    sql += " ORDER BY codigo_tienda"
    return db.execute(sql).fetchall()


def obtener_tienda(id):
    return get_db().execute("SELECT * FROM tiendas WHERE id = ?", (id,)).fetchone()


# ─── CONTADORES PARA DASHBOARD ─────────────────────────────────
def contar_maestros():
    """Devuelve el conteo de registros maestros activos para el dashboard."""
    db = get_db()
    return {
        'vehiculos': db.execute("SELECT COUNT(*) FROM vehiculos WHERE activo = 1").fetchone()[0],
        'conductores': db.execute("SELECT COUNT(*) FROM conductores WHERE activo = 1").fetchone()[0],
        'granjas': db.execute("SELECT COUNT(*) FROM granjas WHERE activo = 1").fetchone()[0],
        'rutas_frigo': db.execute("SELECT COUNT(*) FROM rutas_frigo WHERE activo = 1").fetchone()[0],
        'tiendas': db.execute("SELECT COUNT(*) FROM tiendas WHERE activo = 1").fetchone()[0],
    }
