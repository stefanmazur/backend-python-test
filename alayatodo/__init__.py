from flask import Flask, g, session
import sqlite3
from flask_sqlalchemy import SQLAlchemy

# configuration
DATABASE = '/Repo/backend-python-test/alayatodo.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE
SQLALCHEMY_TRACK_MODIFICATIONS = False

app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)
db.init_app(app)

import alayatodo.views

