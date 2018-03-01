from app import workUpApp

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember me')
	submit = SubmitField('Sign In')
	

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField('Repeat password', validators=[DataRequired(), EqualTo('password')])
	studentNumber = StringField('Student number', validators=[DataRequired()])
	classId = SelectField('Class ID', choices=workUpApp.config['CLASS_CHOICES'], validators=[DataRequired()])
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
		
		
class AssignmentCreationForm(FlaskForm):
	title = StringField('Assignment title', validators=[DataRequired()])
	description = StringField('Assignment description', validators=[DataRequired()])
	due_date = DateField('Due date:', validators=[DataRequired()])
	target_course = SelectField('Class ID', choices=workUpApp.config['CLASS_CHOICES'], validators=[DataRequired()])
	submit = SubmitField('Create')
	
	
class ClassCreationForm(FlaskForm):
	classNumber = StringField('Class number', validators=[DataRequired()])
	classLabel = StringField('Class label', validators=[DataRequired()])
	classTerm = StringField('Class term', validators=[DataRequired()])
	classYear = StringField('Class year', validators=[DataRequired()])
	submit = SubmitField('Create')