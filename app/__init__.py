from flask import Flask
from config import *

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap  # This loads bootstrap-flask
from flask_mail import Mail
from flask_executor import Executor
from flask_toastr import Toastr
from flask_compress import Compress
import flask_excel as excel
from flask_qrcode import QRcode
from flask_marshmallow import Marshmallow


import logging
import os
from logging.handlers import RotatingFileHandler

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'user.login'
bootstrap = Bootstrap()
mail = Mail()
executor = Executor()
toastr = Toastr()
compress = Compress()
ma = Marshmallow()


def create_app(config_class):
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
    compress.init_app(workup_app)
    excel.init_excel(workup_app)
    qrcode = QRcode(workup_app)
    ma.init_app(workup_app)

    # Import templates
    from app.errors import bp as errors_bp
    workup_app.register_blueprint(errors_bp)

    from app.user import bp as user_bp
    workup_app.register_blueprint(user_bp, url_prefix='/user')

    from app.statements import bp as statements_bp
    workup_app.register_blueprint(statements_bp, url_prefix='/statements')

    from app.classes import bp as classes_bp
    workup_app.register_blueprint(classes_bp, url_prefix='/classes')

    from app.files import bp as files_bp
    workup_app.register_blueprint(files_bp, url_prefix='/files')

    from app.assignments import bp as assignments_bp
    workup_app.register_blueprint(assignments_bp, url_prefix='/assignments')

    from app.references import bp as references_bp
    workup_app.register_blueprint(references_bp, url_prefix='/references')

    from app.grammar import bp as grammar_bp
    workup_app.register_blueprint(grammar_bp, url_prefix='/grammar')

    from app.collaboration import bp as collaboration_bp
    workup_app.register_blueprint(
        collaboration_bp, url_prefix='/collaboration')

    from app.consultations import bp as consultations_bp
    workup_app.register_blueprint(
        consultations_bp, url_prefix='/consultations')

    from app.mentors import bp as mentors_bp
    workup_app.register_blueprint(mentors_bp, url_prefix='/mentors')

    from app.api import bp as api_bp
    workup_app.register_blueprint(api_bp)

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
        file_handler = RotatingFileHandler(os.path.join(
            logsPath, 'workup_app.log'), maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        workup_app.logger.addHandler(file_handler)

        workup_app.logger.setLevel(logging.INFO)
        workup_app.logger.info('WorkUp App startup')

    db.create_all()
    db.session.commit()

    return workup_app
