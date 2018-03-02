from app import workUpApp

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, RadioField, FormField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User, Class


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
	
	classNumberAndLabelList = Class.getClassChoiceListForForm ()
	classId = SelectField('Class ID', choices=classNumberAndLabelList, validators=[DataRequired()])
	
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
	target_course = SelectField('Class ID', choices=Class.getClassChoiceListForForm (), validators=[DataRequired()])
	submit = SubmitField('Create')
	
	
class ClassCreationForm(FlaskForm):
	classNumber = StringField('Class number', validators=[DataRequired()])
	classLabel = StringField('Class label', validators=[DataRequired()])
	classTerm = StringField('Class term', validators=[DataRequired()])
	classYear = StringField('Class year', validators=[DataRequired()])
	submit = SubmitField('Create')
	
class PeerReviewForm(FlaskForm):
	agreeDisagreeFivePartLikertScale = [('stronglydisagree', 'Strongly disagree'), ('disagree', 'Disagree'), ('neutral', 'Neutral'), ('agree', 'Agree'), ('stronglyagree', 'Strongly agree') ]
	wordCountLabel= 'Did this piece meet the word limit requirement of approximately 500 words? (10% over is acceptable)'
	wordCount = RadioField(label=wordCountLabel, choices=agreeDisagreeFivePartLikertScale)
	
	essayRequirementLabel = "Did this piece meet the requirement of an engagement with at least three academic sources?"
	essayRequirement = RadioField(label=essayRequirementLabel, choices=agreeDisagreeFivePartLikertScale)
	essayRequirementDescription = StringField('Comment and justification:', validators=[DataRequired()])
	
	essayRequirementLabel = "Did this piece meet the requirement of an engagement with at least three academic sources?"
	essayRequirement = RadioField(label=essayRequirementLabel, choices=agreeDisagreeFivePartLikertScale)
	essayRequirementDescription = StringField('Comment and justification:', validators=[DataRequired()])
	
	essayRequirementLabel = "Did this piece meet the requirement of an engagement with at least three academic sources?"
	essayRequirement = RadioField(label=essayRequirementLabel, choices=agreeDisagreeFivePartLikertScale)
	essayRequirementDescription = StringField('Comment and justification:', validators=[DataRequired()])
	
	essayRequirementLabel = "Did this piece meet the requirement of an engagement with at least three academic sources?"
	essayRequirement = RadioField(label=essayRequirementLabel, choices=agreeDisagreeFivePartLikertScale)
	essayRequirementDescription = StringField('Comment and justification:', validators=[DataRequired()])
	
	essayRequirementLabel = "Did this piece meet the requirement of an engagement with at least three academic sources?"
	essayRequirement = RadioField(label=essayRequirementLabel, choices=agreeDisagreeFivePartLikertScale)
	essayRequirementDescription = StringField('Comment and justification:', validators=[DataRequired()])
	submit = SubmitField('Create')