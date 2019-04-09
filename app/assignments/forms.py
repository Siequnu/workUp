from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, RadioField, FormField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from app.models import User, Turma
	
	
class AssignmentCreationForm(FlaskForm):
	title = StringField('Assignment title', validators=[DataRequired()])
	description = StringField('Assignment description', validators=[DataRequired()])
	due_date = DateField('Due date:', validators=[DataRequired()])
	target_course = SelectField('Class ID', choices=Turma.getTurmaChoiceListForForm (), validators=[DataRequired()])
	peer_review_necessary = RadioField ('Peer review necessary?', choices=[('True', 'Yes'),('False', 'No')], default='No', validators=[DataRequired()])
	peer_review_form = StringField('Peer review form Class name', validators=[DataRequired()])
	submit = SubmitField('Create')
	