from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, SelectMultipleField, BooleanField, FormField, TextAreaField, FileField
from wtforms.validators import ValidationError, DataRequired
from app import db
	
class ApiCreationForm(FlaskForm):
	key = StringField('Api Key', validators=[DataRequired()])
	description = StringField('Description', validators=[DataRequired()])
	submit = SubmitField('Create API key')
