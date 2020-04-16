from flask import Flask, request, abort, flash, current_app, session, Response, render_template, url_for, redirect
from flask_login import login_required, current_user
from flask_restful import Resource, reqparse

from app import db
import app.models
from app.models import LibraryUpload, ApiKey
from app.api.schemas import LibraryUploadSchema
from app.api import bp, models
from app.api.forms import ApiCreationForm

import json, secrets

# API management GUI Routes
@bp.route("/api/manage")
@login_required
def manage_api_keys():
	if app.models.is_admin(current_user.username):	
		api_keys = ApiKey.query.all()
		return render_template('api/manage_api_keys.html', api_keys = api_keys)
	abort (403)
	
@bp.route("/api/create", methods=['GET', 'POST'])
@login_required
def create_api_key():
	if app.models.is_admin(current_user.username):
		key = secrets.token_urlsafe(40)
		form = ApiCreationForm(key = key)
		if form.validate_on_submit():
			key = form.key.data
			description = form.description.data
			app.api.models.create_new_api_key(key, description)
			flash ('API key successfully created', 'success')
			return redirect(url_for('api.manage_api_keys'))
		return render_template('api/create_api_key.html', form = form)
	abort (403)
	
@bp.route("/api/delete/<int:id>")
@login_required
def delete_api_key(id):
	if app.models.is_admin(current_user.username):
		if app.api.models.delete_api_key (id):
			flash ('API key successfully created', 'success')
		else:
			flash ('A problem occured while deleting your API key', 'error')
		return redirect(url_for('api.manage_api_keys'))
	abort (403)


# API routes
library_uploads_schema = LibraryUploadSchema (many = True)
library_upload_schema = LibraryUploadSchema ()
class LibraryListApi (Resource):
	
	def get(self):
		if models.validate_api_key (request.headers.get('key')):
			library_uploads = library_uploads_schema.dump(LibraryUpload.query.all())
			return {'library_uploads': library_uploads}, 200
		else: return {}, 401

class LibraryUploadApi (Resource):
	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument('title', type = str, location = 'json')
		self.reqparse.add_argument('description', type = str, location = 'json')
		super(LibraryUploadApi, self).__init__()
		
	def get(self, id):
		args = self.reqparse.parse_args()
		if models.validate_api_key (request.headers.get('key')):
			library_upload = library_upload_schema.dump(LibraryUpload.query.get(id))
			return {'library_upload': library_upload}, 200
		else: return {}, 401
	
	def put(self, id):
		args = self.reqparse.parse_args()
		if models.validate_api_key (request.headers.get('key')):
			library_upload = LibraryUpload.query.filter_by(id=id).first()
			if not library_upload:
				return {'message': 'Upload does not exist'}, 400
			library_upload.title = args['title']
			library_upload.description = args['description']
			db.session.commit()
			
			result = library_upload_schema.dump(library_upload)
			return {'library_upload': result}, 200
		else: return {}, 401