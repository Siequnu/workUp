from flask import Flask
from config import Config

# Create class and load variables
app = Flask(__name__)
app.config.from_object(Config)
import views