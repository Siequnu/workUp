import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(12) or \
		'ignitors0gitanas*vapours3'
	MAX_CONTENT_LENGTH = 16 * 1024 * 1024
	APP_ROOT = os.path.dirname(os.path.abspath(__file__))
	UPLOAD_LOCATION = 'static/uploads'
	UPLOAD_FOLDER = os.path.join(APP_ROOT, UPLOAD_LOCATION)
	ALLOWED_EXTENSIONS = set(['txt', 'zip', 'pdf', 'doc', 'docx', 'pages'])
	ADMIN_USERS = {'siequnu'}
	
	# SQL
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'workUpApp.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False