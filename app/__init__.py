from flask import Flask
from config import Config
from flask_sslify import SSLify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
import logging, os
from logging.handlers import RotatingFileHandler

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'user.login'
bootstrap = Bootstrap()

def create_app(config_class=Config):
	workUpApp = Flask(__name__)
	workUpApp.config.from_object(config_class)
	db.init_app(workUpApp)
	
	migrate.init_app(workUpApp, db)
	workUpApp.app_context().push()
	
	login.init_app(workUpApp)
	bootstrap = Bootstrap(workUpApp)
	#sslify = SSLify(workUpApp)
	
	# Import templates
	from app.errors import bp as errors_bp
	workUpApp.register_blueprint(errors_bp)

	from app.user import bp as user_bp
	workUpApp.register_blueprint(user_bp, url_prefix='/user')
	
	from app.files import bp as files_bp
	workUpApp.register_blueprint(files_bp, url_prefix='/files')
	
	from app.assignments import bp as assignments_bp
	workUpApp.register_blueprint(assignments_bp, url_prefix='/assignments')
	
	from app.main import bp as main_bp
	workUpApp.register_blueprint(main_bp)
	
	# Create an uploads folder if non-existant
	if not os.path.exists(os.path.join(workUpApp.config['UPLOAD_FOLDER'])):
		os.mkdir(workUpApp.config['UPLOAD_FOLDER'])
		
	# Create a thumbnails folder if non-existant
	if not os.path.exists(os.path.join(workUpApp.config['THUMBNAIL_FOLDER'])):
		os.mkdir(workUpApp.config['THUMBNAIL_FOLDER'])
	
	# Log errors to local log
	if not workUpApp.debug and not workUpApp.testing:
		logsPath = os.path.join(workUpApp.config['APP_ROOT'], 'logs')
		if not os.path.exists(os.path.join(logsPath)):
			os.mkdir(logsPath)
		file_handler = RotatingFileHandler(os.path.join(logsPath, 'workUpApp.log'), maxBytes=10240, backupCount=10)
		file_handler.setFormatter(logging.Formatter(
			'%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
		file_handler.setLevel(logging.INFO)
		workUpApp.logger.addHandler(file_handler)
		
		workUpApp.logger.setLevel(logging.INFO)
		workUpApp.logger.info('workUpApp startup')
		
	return workUpApp

# Import other classes
from app import models

