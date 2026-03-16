"""
Queries para RRHH: jornadas de empleados y fichas snapshot.
"""

from db.connection import get_db


def listar_jornadas_plan(plan_id):
    """Jornadas generadas para una planificación, con datos de conductor."""
    db = get_db()
    return db.execute("""
        SELECT j.*, c.alias AS conductor_alias
        FROM jornadas_empleados j
        LEFT JOIN conductores c ON j.conductor_id = c.id
        WHERE j.planificacion_origen_id = ?
        ORDER BY c.alias
    """, (plan_id,)).fetchall()


def borrar_jornadas_plan(plan_id):
    """Borra las jornadas existentes de un plan antes de regenerarlas."""
    db = get_db()
    db.execute("DELETE FROM jornadas_empleados WHERE planificacion_origen_id = ?", (plan_id,))
    db.commit()


def crear_jornada(plan_id, fecha, conductor_id, tipo_jornada, hora_inicio, hora_fin,
                  horas_trabajadas_min=0, horas_nocturnas_min=0, horas_nocturnas_decimal=0.0,
                  dieta_bool=0, viajes_count=1, semana_excel=None):
    db = get_db()
    db.execute(
        "INSERT INTO jornadas_empleados "
        "(planificacion_origen_id, fecha, conductor_id, tipo_jornada, hora_inicio_real, "
        "hora_fin_real, horas_trabajadas_min, horas_nocturnas_min, horas_nocturnas_decimal, "
        "dieta_bool, viajes_count, semana_excel) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (plan_id, fecha, conductor_id, tipo_jornada, hora_inicio, hora_fin,
         horas_trabajadas_min, horas_nocturnas_min, horas_nocturnas_decimal,
         dieta_bool, viajes_count, semana_excel)
    )
    db.commit()


def obtener_conductores_en_plan(plan_id):
    """Obtiene todos los conductor_id únicos que trabajan en un plan."""
    db = get_db()
    rows = db.execute("""
        SELECT DISTINCT conductor_id FROM (
            SELECT conductor_id FROM viajes_pollos WHERE planificacion_id = ?
            UNION ALL
            SELECT conductor_id FROM servicios_frigos WHERE planificacion_id = ?
            UNION ALL
            SELECT conductor_id FROM servicios_aldis WHERE planificacion_id = ?
        ) WHERE conductor_id IS NOT NULL
    """, (plan_id, plan_id, plan_id)).fetchall()
    return [r['conductor_id'] for r in rows]


def obtener_horarios_conductor_en_plan(plan_id, conductor_id):
    """Devuelve lista de tuplas (hora_inicio, hora_fin) de todos los servicios del conductor."""
    db = get_db()
    tiempos = []

    # Viajes Pollo: usamos hora_salida_sueca_calc y hora_fin_jornada_aprox_calc
    viajes = db.execute(
        "SELECT hora_salida_sueca_calc, hora_fin_jornada_aprox_calc "
        "FROM viajes_pollos WHERE planificacion_id = ? AND conductor_id = ?",
        (plan_id, conductor_id)
    ).fetchall()
    for v in viajes:
        if v['hora_salida_sueca_calc'] and v['hora_fin_jornada_aprox_calc']:
            tiempos.append((v['hora_salida_sueca_calc'], v['hora_fin_jornada_aprox_calc']))

    # Servicios Frigo
    frigos = db.execute(
        "SELECT hora_salida_sueca, hora_fin_real "
        "FROM servicios_frigos WHERE planificacion_id = ? AND conductor_id = ?",
        (plan_id, conductor_id)
    ).fetchall()
    for f in frigos:
        if f['hora_salida_sueca']:
            fin = f['hora_fin_real'] or f['hora_salida_sueca']
            tiempos.append((f['hora_salida_sueca'], fin))

    return tiempos
