# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.debug = True
app.config.from_object('config')
db = SQLAlchemy(app)


import os
from flask.ext.login import LoginManager
from config import basedir
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

from app import views, models
