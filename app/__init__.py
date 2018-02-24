from flask import Flask
from config import Config

workUpApp = Flask(__name__)
workUpApp.config.from_object(Config)

from app import views