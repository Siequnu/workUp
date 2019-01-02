from app import workUpApp

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, RadioField, FormField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo	
	
class PeerReviewForm(FlaskForm):
	agreeDisagreeFivePartLikertScale = [('stronglyagree', 'Strongly agree'), ('agree', 'Agree'), ('neutral', 'Neutral'), ('disagree', 'Disagree'), ('stronglydisagree', 'Strongly disagree')]
	wordCountLabel= 'Did this piece meet the word limit requirement of approximately 500 words? (10% over is acceptable)'
	wordCount = RadioField(label=wordCountLabel, choices=agreeDisagreeFivePartLikertScale)
	
	essayRequirementLabel = "Did this piece meet the requirement of an engagement with at least three academic sources?"
	essayRequirementRadio = RadioField(label=essayRequirementLabel, choices=agreeDisagreeFivePartLikertScale)
	essayRequirementDescription = StringField('Comment and justification:', validators=[DataRequired()])
	
	essayRequirementLabel = "Did the essay critically engage with the concepts and theories covered in the course?"
	criticallyEngageRadio = RadioField(label=essayRequirementLabel, choices=agreeDisagreeFivePartLikertScale)
	criticallyEngageDescription = StringField('Comment and justification:', validators=[DataRequired()])
	
	essayRequirementLabel = "Has the author convincingly applied theoretical concepts from the course to screen media texts to thoroughly develop their argument? Or is the work is derivative of theoretical sources? Does the citation of more than one screen text impair the adequate development of the author's argument?"
	theoreticallyAppliedRadio = RadioField(label=essayRequirementLabel, choices=agreeDisagreeFivePartLikertScale)
	theoreticallyAppliedDescription = StringField('Comment and justification:', validators=[DataRequired()])
	
	essayRequirementLabel = "Was the writer's tone engaging in this piece?"
	writersToneRadio = RadioField(label=essayRequirementLabel, choices=agreeDisagreeFivePartLikertScale)
	writersToneDescription = StringField('Comment and justification:', validators=[DataRequired()])
	
	essayRequirementLabel = "Does this piece display innovative or original thought?"
	innovativeThoughtRadio = RadioField(label=essayRequirementLabel, choices=agreeDisagreeFivePartLikertScale)
	innovativeThoughtDescription = StringField('Comment and justification:', validators=[DataRequired()])
	
	essayRequirementLabel = "Was this piece stimulating and/or insightful?"
	stimatulatingPieceRadio = RadioField(label=essayRequirementLabel, choices=agreeDisagreeFivePartLikertScale)
	stimulatingPieceDescription = StringField('Comment and justification:', validators=[DataRequired()])
	
	furtherSuggestionsDescription = StringField('Do you have any suggestions for how this author can improve on this piece or develop it further for the final research essay? Have you got any suggestions that you believe might assist the author in general?', validators=[DataRequired()])
	submit = SubmitField('Submit')
	
class PeerReviewFormTwo (FlaskForm):
	
	essayRequirementLabel = 'Identify values in the paper (What did you like? What are the best parts? What are the strongest points? What surprised you?'
	valuesPaperField = TextAreaField(label=essayRequirementLabel, validators=[DataRequired()])
	
	essayRequirementLabel = "Describe the form of the paper (structure, organisation, surface errors, etc...)"
	formDescriptionField = TextAreaField(label=essayRequirementLabel, validators=[DataRequired()])
	
	essayRequirementLabel = "Describe the content of the paper (topic, meaning... Did it answer the prompt given?"
	contentDescriptionField = TextAreaField(label=essayRequirementLabel, validators=[DataRequired()])
	
	essayRequirementLabel = "Ask questions about the paper (What needs clarifying? What did you mean when you said...)"
	questionsAboutPaperField = TextAreaField(label=essayRequirementLabel, validators=[DataRequired()])
	
	essayRequirementLabel = "Suggest some points for the author to improve"
	pointsToImproveField = TextAreaField(label=essayRequirementLabel, validators=[DataRequired()])
	
	submit = SubmitField('Submit')

class FormModel (FlaskForm):
	pass
	
	
	