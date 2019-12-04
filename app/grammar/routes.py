from flask import render_template, flash, redirect, url_for, request, abort, current_app, session, Response
from flask_login import current_user, login_required

from app.grammar import bp, forms
from app.grammar.forms import GrammarSubmissionForm

from app.files import models
from app.models import Assignment, Upload, Comment, Turma, User, AssignmentTaskFile, Enrollment, PeerReviewForm, CommentFileUpload, Lesson, AttendanceCode, LessonAttendance
from wtforms import SubmitField
import app.models

from app import db
import requests

# Check grammar
@bp.route("/check/", methods=['GET', 'POST'])
@login_required
def check_grammar():
	form = GrammarSubmissionForm()
	text = ''
	if form.validate_on_submit():
		url = 'https://api.perfecttense.com/correct'
		payload = open("request.json")
		headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
		r = requests.post(url, data=payload, headers=headers)
	return render_template('grammar/check_grammar.html', form = form) 