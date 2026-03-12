from app.extensions import db
from .base import BaseModel
from datetime import date

class PlanificacionDia(BaseModel):
    __tablename__ = 'planificaciones_dia'
    fecha_operativa = db.Column(db.Date, unique=True, index=True, nullable=False)
    dia_semana = db.Column(db.String(20)) # LUNES, MARTES...
    semana_excel = db.Column(db.Integer)
    tipo_dia = db.Column(db.String(50)) # MATANZA...
    estado = db.Column(db.String(20), default='abierta') # abierta, cerrada
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    viajes = db.relationship('ViajePollo', backref='planificacion', cascade="all, delete-orphan")
    frigos = db.relationship('ServicioFrigo', backref='planificacion', cascade="all, delete-orphan")
    aldis = db.relationship('ServicioAldi', backref='planificacion', cascade="all, delete-orphan")

class ViajePollo(BaseModel):
    __tablename__ = 'viajes_pollos'
    planificacion_id = db.Column(db.Integer, db.ForeignKey('planificaciones_dia.id'), nullable=False)
    orden_visual = db.Column(db.Integer, default=1)
    granja_id = db.Column(db.Integer, db.ForeignKey('granjas.id'), nullable=False)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculos.id'), nullable=False)
    conductor_id = db.Column(db.Integer, db.ForeignKey('conductores.id'), nullable=False)
    
    hora_llegada_matadero = db.Column(db.String(5), nullable=False) # '22:00'
    hora_carga_granja_calc = db.Column(db.String(5))
    hora_salida_sueca_calc = db.Column(db.String(5))
    hora_fin_jornada_aprox_calc = db.Column(db.String(5))
    
    # Marcadores estéticos y de operativas especiales
    flecha = db.Column(db.String(5)) # ↑ / ↓
    moffett = db.Column(db.String(10)) # M-4, M-6...
    codigo_visual_extra = db.Column(db.String(10)) # Columna L, letra o núm
    equipo_texto = db.Column(db.String(100))
    notas = db.Column(db.Text)
    
    alerta_duplicidad_conductor = db.Column(db.Boolean, default=False)
    
class ServicioFrigo(BaseModel):
    __tablename__ = 'servicios_frigos'
    planificacion_id = db.Column(db.Integer, db.ForeignKey('planificaciones_dia.id'), nullable=False)
    orden_visual = db.Column(db.Integer, default=1)
    ruta_frigo_id = db.Column(db.Integer, db.ForeignKey('rutas_frigo.id'), nullable=False)
    conductor_id = db.Column(db.Integer, db.ForeignKey('conductores.id'), nullable=False)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculos.id'), nullable=False)
    
    hora_salida_sueca = db.Column(db.String(5))
    hora_inicio_real = db.Column(db.String(5))
    hora_fin_real = db.Column(db.String(5))
    
    num_tiendas_aldi = db.Column(db.Integer, default=0)
    tienda_1_id = db.Column(db.Integer, db.ForeignKey('tiendas.id'))
    tienda_2_id = db.Column(db.Integer, db.ForeignKey('tiendas.id'))
    tienda_3_id = db.Column(db.Integer, db.ForeignKey('tiendas.id'))
    tienda_4_id = db.Column(db.Integer, db.ForeignKey('tiendas.id'))
    
    texto_trayecto_calc = db.Column(db.String(300))
    observaciones = db.Column(db.Text)

class ServicioAldi(BaseModel):
    __tablename__ = 'servicios_aldis'
    planificacion_id = db.Column(db.Integer, db.ForeignKey('planificaciones_dia.id'), nullable=False)
    conductor_id = db.Column(db.Integer, db.ForeignKey('conductores.id'), nullable=False)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculos.id'), nullable=False)
    
    base_origen = db.Column(db.String(100), default='SAGUNTO')
    tienda_1_id = db.Column(db.Integer, db.ForeignKey('tiendas.id'))
    tienda_2_id = db.Column(db.Integer, db.ForeignKey('tiendas.id'))
    tienda_3_id = db.Column(db.Integer, db.ForeignKey('tiendas.id'))
    tienda_4_id = db.Column(db.Integer, db.ForeignKey('tiendas.id'))
    
    texto_trayecto_calc = db.Column(db.String(300))
    hora_inicio_real = db.Column(db.String(5))
    hora_fin_real = db.Column(db.String(5))
    observaciones = db.Column(db.Text)
