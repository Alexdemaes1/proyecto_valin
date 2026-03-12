from app.extensions import db
from .base import BaseModel

class Vehiculo(BaseModel):
    __tablename__ = 'vehiculos'
    codigo_interno = db.Column(db.String(20), unique=True, index=True, nullable=False)
    matricula_tractora = db.Column(db.String(20))
    matricula_semirremolque = db.Column(db.String(20))
    activo = db.Column(db.Boolean, default=True)
    observaciones = db.Column(db.Text)

class Conductor(BaseModel):
    __tablename__ = 'conductores'
    alias = db.Column(db.String(100), unique=True, index=True, nullable=False)
    codigo_alfabetico = db.Column(db.String(10))
    nombre_legal = db.Column(db.String(200))
    dni = db.Column(db.String(20))
    telefono = db.Column(db.String(20))
    empresa = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True)
    notas = db.Column(db.Text)

class Granja(BaseModel):
    __tablename__ = 'granjas'
    codigo = db.Column(db.String(20), unique=True, index=True, nullable=False)
    nombre_cliente = db.Column(db.String(200), nullable=False)
    localidad = db.Column(db.String(150))
    plantas = db.Column(db.Integer, default=1)
    tiempo_trayecto_min = db.Column(db.Integer, default=120)  # default 2h
    tiempo_carga_min = db.Column(db.Integer, default=60)      # default 1h
    anotaciones = db.Column(db.Text)
    telefono_1 = db.Column(db.String(20))
    telefono_2 = db.Column(db.String(20))
    ubicacion_url = db.Column(db.String(500))
    activo = db.Column(db.Boolean, default=True)

class RutaFrigo(BaseModel):
    __tablename__ = 'rutas_frigo'
    codigo_ruta = db.Column(db.String(50), unique=True, index=True, nullable=False)
    poblacion = db.Column(db.String(150))
    hora_salida_texto = db.Column(db.String(20))
    origen = db.Column(db.String(150))
    destino = db.Column(db.String(150))
    trayecto_descripcion = db.Column(db.String(300))
    precio_fijo = db.Column(db.Numeric(10, 2))
    cliente = db.Column(db.String(150))
    activo = db.Column(db.Boolean, default=True)

class Tienda(BaseModel):
    __tablename__ = 'tiendas'
    codigo_tienda = db.Column(db.String(50), unique=True, index=True, nullable=False)
    poblacion = db.Column(db.String(150), nullable=False)
    activo = db.Column(db.Boolean, default=True)

class Simbologia(BaseModel):
    __tablename__ = 'simbologia'
    codigo = db.Column(db.String(20), unique=True, index=True, nullable=False)
    categoria = db.Column(db.String(50))   # e.g., 'Viaje', 'RRHH', 'Aldi'
    descripcion = db.Column(db.String(200))
    modulo = db.Column(db.String(50))      # D, DS, 1, 2, C2, M, T...
    activo = db.Column(db.Boolean, default=True)
