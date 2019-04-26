from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField, DateField, BooleanField, FormField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_wtf.file import FileField, FileRequired
from app.models import Turma
	
	
class LibraryUploadForm(FlaskForm):
	library_upload_file = FileField(label='File:')
	title = StringField('Library upload title:', validators=[DataRequired()])
	description = StringField('Description:', validators=[DataRequired()])
	target_turma_id = SelectMultipleField('Target classes:', choices=Turma.get_class_list_for_forms (), validators=[DataRequired()])	
	submit = SubmitField('Upload new file')
	

		
