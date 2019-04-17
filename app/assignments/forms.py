from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, SelectMultipleField, DateField, BooleanField, FormField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_wtf.file import FileField, FileRequired
from app.models import User, Turma
	
	
class AssignmentCreationForm(FlaskForm):
	title = StringField('Assignment title', validators=[DataRequired()])
	description = StringField('Assignment description', validators=[DataRequired()])
	due_date = DateField('Due date:', validators=[DataRequired()])
	target_turma_id = SelectMultipleField('Class ID', choices=Turma.get_class_list_for_forms (), validators=[DataRequired()])
	peer_review_necessary = BooleanField('Peer review necessary', default=True)
	# Should be a SelectField, with default to BlankPeerReview
	peer_review_form = StringField('Peer review form Class name', validators=[DataRequired()])
	assignment_task_file = FileField(label='Assignment Task File')
	submit = SubmitField('Create')
	
class TurmaCreationForm(FlaskForm):
	turmaNumber = StringField('Class number', validators=[DataRequired()])
	turmaLabel = StringField('Class label', validators=[DataRequired()])
	turmaTerm = StringField('Class term', validators=[DataRequired()])
	turmaYear = StringField('Class year', validators=[DataRequired()])
	submit = SubmitField('Create')

		
