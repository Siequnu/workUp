from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, RadioField, FormField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from app.models import User, Turma
	
	
class AssignmentCreationForm(FlaskForm):
	title = StringField('Assignment title', validators=[DataRequired()])
	description = StringField('Assignment description', validators=[DataRequired()])
	due_date = DateField('Due date:', validators=[DataRequired()])
	target_course = SelectField('Class ID', choices=Turma.getTurmaChoiceListForForm (), validators=[DataRequired()])
	peer_review_form = StringField('Peer review form Class name', validators=[DataRequired()])
	submit = SubmitField('Create')
	
	
class TurmaCreationForm(FlaskForm):
	turmaNumber = StringField('Class number', validators=[DataRequired()])
	turmaLabel = StringField('Class label', validators=[DataRequired()])
	turmaTerm = StringField('Class term', validators=[DataRequired()])
	turmaYear = StringField('Class year', validators=[DataRequired()])
	submit = SubmitField('Create')
	
class AdminRegistrationForm(FlaskForm):
	username = StringField('Admin Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Please use a different username.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Please use a different email address.')
		
