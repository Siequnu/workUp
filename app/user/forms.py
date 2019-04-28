from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, RadioField, FormField, TextAreaField, SelectMultipleField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_wtf.file import FileField, FileRequired
from app.models import User, Turma


class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember me')
	submit = SubmitField('Sign In')

class EditUserForm (FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	student_number = StringField('Student number', validators=[DataRequired()])
	turma_id_and_label_list = Turma.get_class_list_for_forms ()
	turma_id = SelectMultipleField('Class', choices=turma_id_and_label_list, validators=[DataRequired()])
	submit = SubmitField('Edit user')

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	student_number = StringField('Student number', validators=[DataRequired()])
	
	turma_id_and_label_list = Turma.get_class_list_for_forms ()
	turma_id = SelectMultipleField('Class', choices=turma_id_and_label_list, validators=[DataRequired()])
	
	signUpCode = StringField('Sign-up code', validators=[DataRequired()])
	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('Please use a different username.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None:
			raise ValidationError('Please use a different email address.')
				
class EmailForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email()])
	submit = SubmitField('Request password reset.')

class PasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Reset password.')
		
		
class BatchStudentImportForm(FlaskForm):
	target_course = SelectField('Class ID', choices=Turma.get_class_list_for_forms (), validators=[DataRequired()])
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