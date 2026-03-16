-- ============================================================
-- ESQUEMA VALIN v2 — Base de datos SQLite
-- ============================================================
-- Este archivo define todas las tablas del sistema.
-- Se ejecuta automáticamente al arrancar la app si no existe la DB.
-- ============================================================

-- AUTENTICACIÓN
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    active INTEGER DEFAULT 1,
    role_id INTEGER REFERENCES roles(id),
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- DATOS MAESTROS
CREATE TABLE IF NOT EXISTS vehiculos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_interno TEXT UNIQUE NOT NULL,
    matricula_tractora TEXT DEFAULT '',
    matricula_semirremolque TEXT DEFAULT '',
    activo INTEGER DEFAULT 1,
    observaciones TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS conductores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alias TEXT UNIQUE NOT NULL,
    codigo_alfabetico TEXT DEFAULT '',
    nombre_legal TEXT DEFAULT '',
    dni TEXT DEFAULT '',
    telefono TEXT DEFAULT '',
    empresa TEXT DEFAULT '',
    activo INTEGER DEFAULT 1,
    notas TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS granjas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    nombre_cliente TEXT NOT NULL DEFAULT 'DESCONOCIDO',
    localidad TEXT DEFAULT '',
    plantas INTEGER DEFAULT 1,
    tiempo_trayecto_min INTEGER DEFAULT 120,
    tiempo_carga_min INTEGER DEFAULT 60,
    anotaciones TEXT DEFAULT '',
    telefono_1 TEXT DEFAULT '',
    telefono_2 TEXT DEFAULT '',
    ubicacion_url TEXT DEFAULT '',
    activo INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS rutas_frigo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_ruta TEXT UNIQUE NOT NULL,
    poblacion TEXT DEFAULT '',
    hora_salida_texto TEXT DEFAULT '',
    origen TEXT DEFAULT '',
    destino TEXT DEFAULT '',
    trayecto_descripcion TEXT DEFAULT '',
    precio_fijo REAL DEFAULT 0.0,
    cliente TEXT DEFAULT '',
    activo INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tiendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_tienda TEXT UNIQUE NOT NULL,
    poblacion TEXT NOT NULL,
    activo INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS simbologia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    categoria TEXT DEFAULT '',
    descripcion TEXT DEFAULT '',
    modulo TEXT DEFAULT '',
    activo INTEGER DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- OPERACIONES
CREATE TABLE IF NOT EXISTS planificaciones_dia (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha_operativa TEXT UNIQUE NOT NULL,
    dia_semana TEXT DEFAULT '',
    semana_excel INTEGER,
    tipo_dia TEXT DEFAULT '',
    estado TEXT DEFAULT 'abierta',
    created_by INTEGER REFERENCES users(id),
    updated_by INTEGER REFERENCES users(id),
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS viajes_pollos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    planificacion_id INTEGER NOT NULL REFERENCES planificaciones_dia(id) ON DELETE CASCADE,
    orden_visual INTEGER DEFAULT 1,
    granja_id INTEGER REFERENCES granjas(id),
    vehiculo_id INTEGER REFERENCES vehiculos(id),
    conductor_id INTEGER REFERENCES conductores(id),
    hora_llegada_matadero TEXT DEFAULT '00:00',
    hora_carga_granja_calc TEXT DEFAULT '',
    hora_salida_sueca_calc TEXT DEFAULT '',
    hora_fin_jornada_aprox_calc TEXT DEFAULT '',
    flecha TEXT DEFAULT '',
    moffett TEXT DEFAULT '',
    codigo_visual_extra TEXT DEFAULT '',
    equipo_texto TEXT DEFAULT '',
    notas TEXT DEFAULT '',
    alerta_duplicidad_conductor INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS servicios_frigos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    planificacion_id INTEGER NOT NULL REFERENCES planificaciones_dia(id) ON DELETE CASCADE,
    orden_visual INTEGER DEFAULT 1,
    ruta_frigo_id INTEGER REFERENCES rutas_frigo(id),
    conductor_id INTEGER REFERENCES conductores(id),
    vehiculo_id INTEGER REFERENCES vehiculos(id),
    hora_salida_sueca TEXT DEFAULT '',
    hora_inicio_real TEXT DEFAULT '',
    hora_fin_real TEXT DEFAULT '',
    num_tiendas_aldi INTEGER DEFAULT 0,
    tienda_1_id INTEGER REFERENCES tiendas(id),
    tienda_2_id INTEGER REFERENCES tiendas(id),
    tienda_3_id INTEGER REFERENCES tiendas(id),
    tienda_4_id INTEGER REFERENCES tiendas(id),
    texto_trayecto_calc TEXT DEFAULT '',
    observaciones TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS servicios_aldis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    planificacion_id INTEGER NOT NULL REFERENCES planificaciones_dia(id) ON DELETE CASCADE,
    conductor_id INTEGER REFERENCES conductores(id),
    vehiculo_id INTEGER REFERENCES vehiculos(id),
    base_origen TEXT DEFAULT 'SAGUNTO',
    tienda_1_id INTEGER REFERENCES tiendas(id),
    tienda_2_id INTEGER REFERENCES tiendas(id),
    tienda_3_id INTEGER REFERENCES tiendas(id),
    tienda_4_id INTEGER REFERENCES tiendas(id),
    texto_trayecto_calc TEXT DEFAULT '',
    hora_inicio_real TEXT DEFAULT '',
    hora_fin_real TEXT DEFAULT '',
    observaciones TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- RRHH
CREATE TABLE IF NOT EXISTS jornadas_empleados (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha TEXT NOT NULL,
    semana_excel INTEGER,
    conductor_id INTEGER NOT NULL REFERENCES conductores(id),
    poblacion_servicio TEXT DEFAULT '',
    tipo_jornada TEXT DEFAULT '1',
    hora_inicio_real TEXT DEFAULT '',
    hora_fin_real TEXT DEFAULT '',
    horas_trabajadas_min INTEGER DEFAULT 0,
    horas_nocturnas_min INTEGER DEFAULT 0,
    horas_nocturnas_decimal REAL DEFAULT 0.0,
    dieta_bool INTEGER DEFAULT 0,
    desayuno_bool INTEGER DEFAULT 0,
    pernocta_bool INTEGER DEFAULT 0,
    festivo_bool_manual INTEGER DEFAULT 0,
    sexto_dia_bool_manual INTEGER DEFAULT 0,
    viajes_count INTEGER DEFAULT 1,
    planificacion_origen_id INTEGER REFERENCES planificaciones_dia(id),
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS fichas_empleado_snapshot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conductor_id INTEGER NOT NULL REFERENCES conductores(id),
    anio INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    fecha_impresion TEXT,
    horas_totales_min INTEGER DEFAULT 0,
    horas_nocturnas_min INTEGER DEFAULT 0,
    horas_media_salida TEXT DEFAULT '',
    horas_media_llegada TEXT DEFAULT '',
    dobles_viajes_count INTEGER DEFAULT 0,
    combinados_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
