from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(message="Debe escribir el nombre corto de usuario")])
    password = PasswordField('Contraseña', validators=[DataRequired(message="Debe proveer una contraseña")])
    submit = SubmitField('Acceder a Logística')
