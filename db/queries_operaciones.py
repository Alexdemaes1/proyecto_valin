"""
Queries para operaciones: planificaciones, viajes, frigos, aldi.
"""

from db.connection import get_db


# ─── PLANIFICACIONES ────────────────────────────────────────────
def listar_planificaciones():
    db = get_db()
    return db.execute(
        "SELECT * FROM planificaciones_dia ORDER BY fecha_operativa DESC"
    ).fetchall()


def obtener_planificacion(id):
    return get_db().execute(
        "SELECT * FROM planificaciones_dia WHERE id = ?", (id,)
    ).fetchone()


def obtener_planificacion_por_fecha(fecha_str):
    return get_db().execute(
        "SELECT * FROM planificaciones_dia WHERE fecha_operativa = ?", (fecha_str,)
    ).fetchone()


def crear_planificacion(fecha_operativa, dia_semana='', semana_excel=None,
                        tipo_dia='', created_by=None):
    db = get_db()
    db.execute(
        "INSERT INTO planificaciones_dia (fecha_operativa, dia_semana, semana_excel, tipo_dia, created_by) "
        "VALUES (?, ?, ?, ?, ?)",
        (fecha_operativa, dia_semana, semana_excel, tipo_dia, created_by)
    )
    db.commit()
    return db.execute("SELECT last_insert_rowid()").fetchone()[0]


def eliminar_planificacion(id):
    db = get_db()
    db.execute("DELETE FROM planificaciones_dia WHERE id = ?", (id,))
    db.commit()


# ─── VIAJES POLLO ───────────────────────────────────────────────
def listar_viajes_plan(plan_id):
    """Lista viajes de un plan con datos de granja, vehículo y conductor unidos."""
    db = get_db()
    return db.execute("""
        SELECT v.*,
               g.codigo AS granja_codigo,
               g.nombre_cliente AS granja_nombre,
               g.tiempo_trayecto_min AS granja_trayecto,
               g.tiempo_carga_min AS granja_carga,
               ve.codigo_interno AS vehiculo_codigo,
               c.alias AS conductor_alias
        FROM viajes_pollos v
        LEFT JOIN granjas g ON v.granja_id = g.id
        LEFT JOIN vehiculos ve ON v.vehiculo_id = ve.id
        LEFT JOIN conductores c ON v.conductor_id = c.id
        WHERE v.planificacion_id = ?
        ORDER BY v.orden_visual
    """, (plan_id,)).fetchall()


def crear_viaje(plan_id, granja_id=None, vehiculo_id=None, conductor_id=None,
                hora_llegada='00:00'):
    db = get_db()
    # Calcular orden visual
    ultimo = db.execute(
        "SELECT COUNT(*) FROM viajes_pollos WHERE planificacion_id = ?", (plan_id,)
    ).fetchone()[0]

    db.execute(
        "INSERT INTO viajes_pollos (planificacion_id, orden_visual, granja_id, vehiculo_id, "
        "conductor_id, hora_llegada_matadero) VALUES (?, ?, ?, ?, ?, ?)",
        (plan_id, ultimo + 1, granja_id, vehiculo_id, conductor_id, hora_llegada)
    )
    db.commit()
    return db.execute("SELECT last_insert_rowid()").fetchone()[0]


def actualizar_viaje(viaje_id, **campos):
    db = get_db()
    partes = []
    valores = []
    for campo, valor in campos.items():
        partes.append(f"{campo} = ?")
        valores.append(valor)
    partes.append("updated_at = datetime('now')")
    valores.append(viaje_id)
    db.execute(f"UPDATE viajes_pollos SET {', '.join(partes)} WHERE id = ?", valores)
    db.commit()


def eliminar_viaje(viaje_id):
    db = get_db()
    db.execute("DELETE FROM viajes_pollos WHERE id = ?", (viaje_id,))
    db.commit()


def contar_viajes_conductor_en_plan(plan_id, conductor_id):
    """Para detectar duplicidad de conductor en un mismo plan."""
    db = get_db()
    return db.execute(
        "SELECT COUNT(*) FROM viajes_pollos WHERE planificacion_id = ? AND conductor_id = ?",
        (plan_id, conductor_id)
    ).fetchone()[0]


# ─── SERVICIOS FRIGOS ──────────────────────────────────────────
def listar_frigos_plan(plan_id):
    db = get_db()
    return db.execute("""
        SELECT sf.*,
               rf.codigo_ruta, rf.origen, rf.destino, rf.trayecto_descripcion,
               ve.codigo_interno AS vehiculo_codigo,
               c.alias AS conductor_alias
        FROM servicios_frigos sf
        LEFT JOIN rutas_frigo rf ON sf.ruta_frigo_id = rf.id
        LEFT JOIN vehiculos ve ON sf.vehiculo_id = ve.id
        LEFT JOIN conductores c ON sf.conductor_id = c.id
        WHERE sf.planificacion_id = ?
        ORDER BY sf.orden_visual
    """, (plan_id,)).fetchall()


def crear_frigo(plan_id, ruta_frigo_id=None, conductor_id=None, vehiculo_id=None,
                hora_salida=''):
    db = get_db()
    ultimo = db.execute(
        "SELECT COUNT(*) FROM servicios_frigos WHERE planificacion_id = ?", (plan_id,)
    ).fetchone()[0]
    db.execute(
        "INSERT INTO servicios_frigos (planificacion_id, orden_visual, ruta_frigo_id, "
        "conductor_id, vehiculo_id, hora_salida_sueca) VALUES (?, ?, ?, ?, ?, ?)",
        (plan_id, ultimo + 1, ruta_frigo_id, conductor_id, vehiculo_id, hora_salida)
    )
    db.commit()


# ─── SERVICIOS ALDI ────────────────────────────────────────────
def listar_aldis_plan(plan_id):
    db = get_db()
    return db.execute("""
        SELECT sa.*,
               ve.codigo_interno AS vehiculo_codigo,
               c.alias AS conductor_alias
        FROM servicios_aldis sa
        LEFT JOIN vehiculos ve ON sa.vehiculo_id = ve.id
        LEFT JOIN conductores c ON sa.conductor_id = c.id
        WHERE sa.planificacion_id = ?
    """, (plan_id,)).fetchall()


def crear_aldi(plan_id, conductor_id=None, vehiculo_id=None, base_origen='SAGUNTO'):
    db = get_db()
    db.execute(
        "INSERT INTO servicios_aldis (planificacion_id, conductor_id, vehiculo_id, base_origen) "
        "VALUES (?, ?, ?, ?)",
        (plan_id, conductor_id, vehiculo_id, base_origen)
    )
    db.commit()
