from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, RadioField, FormField, TextAreaField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_wtf.file import FileField, FileRequired

from app.models import User, Turma
	
	
class TurmaCreationForm(FlaskForm):
	turmaNumber = StringField('Class number', validators=[DataRequired()])
	turmaLabel = StringField('Class label', validators=[DataRequired()])
	turmaTerm = StringField('Class term', validators=[DataRequired()])
	turmaYear = StringField('Class year', validators=[DataRequired()])
	submit = SubmitField('Create')
	
class BatchStudentImportForm(FlaskForm):
	target_course = SelectField('Class ID', choices=Turma.getTurmaChoiceListForForm (), validators=[DataRequired()])
	excel_file = FileField(validators=[FileRequired()], label='Excel File')
	submit = SubmitField('Process...')
	
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
		
