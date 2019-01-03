from app import workUpApp

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, RadioField, FormField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

from app.models import User, Turma


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
	
	turmaNumberAndLabelList = Turma.getTurmaChoiceListForForm ()
	turmaId = SelectField('Class ID', choices=turmaNumberAndLabelList, validators=[DataRequired()])
	
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
		