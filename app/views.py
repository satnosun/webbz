#-*- coding: utf-8 -*-
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

from flask import g, request, render_template, session, url_for, escape, redirect, flash
from app import app, db
from forms import RegistrationForm
from models import User, LEVEL_USER, LEVEL_PLAYER, LEVEL_SEER, LEVEL_ADMIN

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
        title = '首页')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User(form.username.data, form.nickname.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        #flash('Thanks for registering')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)
