"""
The flask application package.
"""
from flask import Flask
import os
from .flask_api import api, db
from .flask_site import site

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# Update HOST and PASSWORD appropriately.
HOST = "35.189.7.222"
USER = "root"
PASSWORD = "admin@1234"
DATABASE = "Library"

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://{}:{}@{}/{}".format(USER, PASSWORD, HOST, DATABASE)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config['SECRET_KEY'] = 'SjdnUends821Jsdlkvxh391ksdODnejdDw'

db.init_app(app)

app.register_blueprint(api)
app.register_blueprint(site)

