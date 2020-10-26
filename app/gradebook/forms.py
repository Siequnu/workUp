from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateField, SelectMultipleField, BooleanField, FormField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
	
class AssessmentCriteriaForm (FlaskForm):
    title = StringField ('Assessment title', validators=[DataRequired(), Length(max=450)])
    date = DateField('Date')
    submit = SubmitField('Submit')