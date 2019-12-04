from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, SelectMultipleField, BooleanField, FormField, TextAreaField
from wtforms.validators import ValidationError, DataRequired
from flask_wtf.file import FileField, FileRequired
from app import db


	
class GrammarSubmissionForm(FlaskForm):
	title = TextAreaField('Your assignment', validators=[DataRequired()])
	submit = SubmitField('Check')
