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

import ProWritingAidSDK
from ProWritingAidSDK.rest import ApiException

configuration = ProWritingAidSDK.Configuration()
configuration.host = 'https://api.prowritingaid.com'
configuration.api_key['licenseCode'] = current_app.config['PRO_WRITING_AID_API_KEY']

api_instance = ProWritingAidSDK.TextApi(ProWritingAidSDK.ApiClient('https://api.prowritingaid.com'))

# Check grammar
@bp.route("/check/", methods=['GET', 'POST'])
@login_required
def check_grammar():
	form = GrammarSubmissionForm()
	if form.validate_on_submit():
		body = form.body.data 
		api_request = ProWritingAidSDK.TextAnalysisRequest(body, ["grammar"], "General", "en")
		api_response = api_instance.post(api_request)
	
		return render_template('grammar/check_grammar.html', form = form, api_response = api_response, body = body) 
	return render_template('grammar/check_grammar.html', form = form) 