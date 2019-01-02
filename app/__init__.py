from flask import Flask
from config import Config

# SSL
from flask_sslify import SSLify

# SQL
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Log-in
from flask_login import LoginManager

# Bootstrap
from flask_bootstrap import Bootstrap

# Logging handlers
import logging, os
from logging.handlers import RotatingFileHandler

workUpApp = Flask(__name__)
workUpApp.config.from_object(Config)

# SSL
sslify = SSLify(workUpApp)

# SQL
db = SQLAlchemy(workUpApp)
migrate = Migrate(workUpApp, db)

# Log-in
login = LoginManager(workUpApp)
login.login_view = 'login'

# Bootstrap
bootstrap = Bootstrap(workUpApp)

# Create a logs folder if non-existant
uploadFolderPath = os.path.join(workUpApp.config['APP_ROOT'], 'uploads')
if not os.path.exists(os.path.join(uploadFolderPath)):
	os.mkdir(uploadFolderPath)

# Log errors to local log
if not workUpApp.debug:
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

from app import views, models, errors

