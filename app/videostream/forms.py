from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError,PasswordField, HiddenField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms.ext.sqlalchemy.fields import QuerySelectField

class FuncionForm(FlaskForm):
    inicio = StringField("Hora de Inicio",validators=[DataRequired()])
    fin = StringField("Hora de Fin", validators=[DataRequired()])
    submit= SubmitField('Agregar')