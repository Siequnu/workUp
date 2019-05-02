from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField, DateField, BooleanField, FormField, TextAreaField
from wtforms.validators import ValidationError, DataRequired
from flask_wtf.file import FileField, FileRequired
from app import db


	
class AssignmentCreationForm(FlaskForm):
	title = StringField('Assignment title', validators=[DataRequired()])
	description = StringField('Assignment description', validators=[DataRequired()])
	due_date = DateField('Due date:', validators=[DataRequired()])
	target_turmas = SelectMultipleField('For classes', coerce=int, validators=[DataRequired()])
	peer_review_necessary = BooleanField('Peer review necessary', default=True)
	peer_review_form_id = SelectField('Peer review form', coerce=int, validators=[DataRequired()])
	assignment_task_file = FileField(label='Assignment Task File')
	submit = SubmitField('Create')
	
class TurmaCreationForm(FlaskForm):
	turma_number = StringField('Class number', validators=[DataRequired()])
	turma_label = StringField('Class label', validators=[DataRequired()])
	turma_term = StringField('Class term', validators=[DataRequired()])
	turma_year = StringField('Class year', validators=[DataRequired()])
	submit = SubmitField('Create')

		
