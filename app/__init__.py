# -*- coding: utf-8 -*-
import os
from flask import Flask, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.admin import Admin
from config import basedir

# 创建flask应用
app = Flask(__name__)
app.debug = True
app.config.from_object('config')

# 创建数据库
db = SQLAlchemy(app)

login_manager  = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



from app import views, models
