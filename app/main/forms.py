from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, RadioField, FormField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from app.models import User, Turma



class FormModel (FlaskForm):
	pass
	
	
	