from app.extensions import db
from .base import BaseModel

class JornadaEmpleado(BaseModel):
    __tablename__ = 'jornadas_empleados'
    fecha = db.Column(db.Date, index=True, nullable=False)
    semana_excel = db.Column(db.Integer)
    conductor_id = db.Column(db.Integer, db.ForeignKey('conductores.id'), nullable=False)
    poblacion_servicio = db.Column(db.String(250)) # O lista separada de pueblos
    tipo_jornada = db.Column(db.String(10), nullable=False) # 1, 2, 3, 4, M, T, DS...
    
    hora_inicio_real = db.Column(db.String(5))
    hora_fin_real = db.Column(db.String(5))
    
    # Cálculos puros de RRHH
    horas_trabajadas_min = db.Column(db.Integer, default=0)
    horas_nocturnas_min = db.Column(db.Integer, default=0)
    horas_nocturnas_decimal = db.Column(db.Numeric(6, 2), default=0.0)
    
    # Banderas extraídas de lógica de la APP
    dieta_bool = db.Column(db.Boolean, default=False)
    desayuno_bool = db.Column(db.Boolean, default=False)
    pernocta_bool = db.Column(db.Boolean, default=False)
    
    # Banderas manuales
    festivo_bool_manual = db.Column(db.Boolean, default=False)
    sexto_dia_bool_manual = db.Column(db.Boolean, default=False)
    
    # Control origen de datos para auditoría
    viajes_count = db.Column(db.Integer, default=1)
    planificacion_origen_id = db.Column(db.Integer, db.ForeignKey('planificaciones_dia.id'))

class FichaEmpleadoSnapshot(BaseModel):
    # Snapshot / Cached statistics for the monthly view of drivers
    __tablename__ = 'fichas_empleado_snapshot'
    conductor_id = db.Column(db.Integer, db.ForeignKey('conductores.id'), nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    fecha_impresion = db.Column(db.Date)
    
    horas_totales_min = db.Column(db.Integer, default=0)
    horas_nocturnas_min = db.Column(db.Integer, default=0)
    horas_media_salida = db.Column(db.String(5))
    horas_media_llegada = db.Column(db.String(5))
    
    dobles_viajes_count = db.Column(db.Integer, default=0)
    combinados_count = db.Column(db.Integer, default=0)
    # the rest will be dynamically fetched matching the existing Excel 'FICHA' view
