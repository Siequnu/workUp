import os

class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(12) or 'ignitors0gitanas*vapours3'
	MAX_CONTENT_LENGTH = 16 * 1024 * 1024
	APP_ROOT = os.path.dirname(os.path.abspath(__file__))
	UPLOAD_LOCATION = 'static/uploads'
	UPLOAD_FOLDER = os.path.join(APP_ROOT, UPLOAD_LOCATION)
	ALLOWED_EXTENSIONS = set(['txt', 'zip', 'pdf', 'doc', 'docx', 'pages'])
	USERS= {
		"john": "hello",
		"susan": "bye"
	}
	ADMIN_USERS = {'john'}