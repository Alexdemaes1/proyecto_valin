from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, BooleanField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Optional, Length

class VehiculoForm(FlaskForm):
    codigo_interno = StringField('Código Interno', validators=[DataRequired()])
    matricula_tractora = StringField('Matrícula Tractora')
    matricula_semirremolque = StringField('Matrícula Remolque')
    activo = BooleanField('Activo', default=True)
    observaciones = TextAreaField('Observaciones')
    submit = SubmitField('Guardar Vehículo')

class ConductorForm(FlaskForm):
    alias = StringField('Alias (Operativo)', validators=[DataRequired()])
    codigo_alfabetico = StringField('Código Letras', validators=[Length(max=10)])
    nombre_legal = StringField('Nombre Completo')
    dni = StringField('DNI')
    telefono = StringField('Teléfono')
    empresa = StringField('Empresa / Nómina')
    activo = BooleanField('Activo', default=True)
    notas = TextAreaField('Notas')
    submit = SubmitField('Guardar Conductor')

class GranjaForm(FlaskForm):
    codigo = StringField('Código Granja', validators=[DataRequired()])
    nombre_cliente = StringField('Nombre Cliente', validators=[DataRequired()])
    localidad = StringField('Localidad')
    plantas = IntegerField('Plantas', default=1)
    tiempo_trayecto_min = IntegerField('Tiempo Trayecto (min)', default=120)
    tiempo_carga_min = IntegerField('Tiempo Carga (min)', default=60)
    telefono_1 = StringField('Teléfono 1')
    telefono_2 = StringField('Teléfono 2')
    ubicacion_url = StringField('URL Ubicación')
    anotaciones = TextAreaField('Anotaciones')
    activo = BooleanField('Activo', default=True)
    submit = SubmitField('Guardar Granja')

class RutaFrigoForm(FlaskForm):
    codigo_ruta = StringField('Código Ruta', validators=[DataRequired()])
    poblacion = StringField('Población / Destino')
    hora_salida_texto = StringField('Hora Salida Programada')
    precio_fijo = DecimalField('Tarifa (€)', places=2)
    cliente = StringField('Cliente')
    activo = BooleanField('Activo', default=True)
    submit = SubmitField('Guardar Ruta')
