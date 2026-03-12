from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class LocalConfigForm(FlaskForm):
    pc_name = StringField('Nombre Identificativo del PC', validators=[DataRequired()])
    drive_path = StringField('Ruta Raíz de Google Drive (Carpeta de Red)', validators=[DataRequired()])
    master_db_filename = StringField('Nombre del Archivo DB Maestro', default='valin_master.db')
    legacy_excel_path = StringField('Ruta al Excel de Importación (Opcional)')
    submit = SubmitField('Guardar y Vincular')
