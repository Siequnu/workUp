from flask import Flask
from config import Config

# SQL
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Bootstrap
from flask_bootstrap import Bootstrap

workUpApp = Flask(__name__)
workUpApp.config.from_object(Config)

# SQL
db = SQLAlchemy(workUpApp)
migrate = Migrate(workUpApp, db)

# Log-in
login = LoginManager(workUpApp)
login.login_view = 'login'

# Bootstrap
bootstrap = Bootstrap(workUpApp)

from app import views, models, errors

