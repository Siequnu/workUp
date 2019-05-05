from flask import Flask
from config import Config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap #This loads bootstrap-flask
from flask_mail import Mail
from flask_executor import Executor
from flask_toastr import Toastr
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from flask_redis import Redis

import logging, os
from logging.handlers import RotatingFileHandler

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'user.login'
bootstrap = Bootstrap()
mail = Mail()
executor = Executor()
toastr = Toastr()
limiter = Limiter(key_func=get_remote_address)

redis = Redis()

def create_app(config_class=Config):
	workup_app = Flask(__name__)
	workup_app.config.from_object(config_class)
	
	db.init_app(workup_app)
	migrate.init_app(workup_app, db)
	workup_app.app_context().push()
	
	login.init_app(workup_app)
	bootstrap = Bootstrap(workup_app)
	mail.init_app(workup_app)
	executor.init_app(workup_app)
	toastr.init_app(workup_app)
	limiter.init_app(workup_app)
	redis.init_app(workup_app)
	
	
	# Import templates
	from app.errors import bp as errors_bp
	workup_app.register_blueprint(errors_bp)

	from app.user import bp as user_bp
	workup_app.register_blueprint(user_bp, url_prefix='/user')
	
	from app.files import bp as files_bp
	workup_app.register_blueprint(files_bp, url_prefix='/files')
	
	from app.assignments import bp as assignments_bp
	workup_app.register_blueprint(assignments_bp, url_prefix='/assignments')
	
	from app.main import bp as main_bp
	workup_app.register_blueprint(main_bp)
	
	# Create an uploads folder if non-existant
	if not os.path.exists(os.path.join(workup_app.config['UPLOAD_FOLDER'])):
		os.mkdir(workup_app.config['UPLOAD_FOLDER'])
		
	# Create a thumbnails folder if non-existant
	if not os.path.exists(os.path.join(workup_app.config['THUMBNAIL_FOLDER'])):
		os.mkdir(workup_app.config['THUMBNAIL_FOLDER'])
	
	# Log errors to local log
	if not workup_app.debug and not workup_app.testing:
		logsPath = os.path.join(workup_app.config['APP_ROOT'], 'logs')
		if not os.path.exists(os.path.join(logsPath)):
			os.mkdir(logsPath)
		file_handler = RotatingFileHandler(os.path.join(logsPath, 'workup_app.log'), maxBytes=10240, backupCount=10)
		file_handler.setFormatter(logging.Formatter(
			'%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
		file_handler.setLevel(logging.INFO)
		workup_app.logger.addHandler(file_handler)
		
		workup_app.logger.setLevel(logging.INFO)
		workup_app.logger.info('WorkUp App startup')
	
	db.create_all()
	db.session.commit()
		
	return workup_app

# Import other classes
from app import models

