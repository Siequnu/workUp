from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField, DateField, BooleanField, FormField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_wtf.file import FileField, FileRequired
from app.models import Turma
	
	
class LibraryUploadForm(FlaskForm):
	library_upload_file = FileField(label='File:')
	title = StringField('Library upload title:', validators=[DataRequired()])
	description = StringField('Description:', validators=[DataRequired()])
	target_turmas = SelectMultipleField('For classes', coerce=int, validators=[DataRequired()])
	submit = SubmitField('Upload new file')
	

		
