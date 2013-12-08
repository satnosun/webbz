#-*- coding: utf-8 -*-
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

from flask import g, request, render_template, session, url_for, escape, redirect, flash
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from forms import RegistrationForm, LoginForm
from models import User, LEVEL_USER, LEVEL_PLAYER, LEVEL_SEER, LEVEL_ADMIN
import CaptchasDotNet
import hashlib

@app.route('/')
@app.route('/index')
def index():
    form = LoginForm()
    return render_template('index.html',
        form = form,
        title = '首页')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    captchas = CaptchasDotNet.CaptchasDotNet(
                                client   = 'satnosun',
                                secret   = 'Vsffpr0tVJeAOGF3TUMFd05470WRNFASJRcTBe60',
                                #alphabet = 'abcdefghkmnopqrstuvwxyz',
                                #letters  = 6,
                                width    = 200,
                                height   = 70
                                )
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            flash('用户名已存在！')
            return redirect(request.args.get("next") or url_for("register"))
        user = User.query.filter_by(username=form.nickname.data).first()
        if user is not None:
            flash('昵称已存在！')
            return redirect(request.args.get("next") or url_for("register"))
        random_string = form.random.data
        captcha = form.captcha.data
        captchas.validate(random_string)
        if not captchas.verify(captcha):
            flash('验证码输入错误')
            return redirect(request.args.get("next") or url_for("register"))
        user = User(form.username.data, form.nickname.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('注册成功！')
        return redirect(url_for('index'))
    form.random.data = captchas.random()
    return render_template('register.html', form=form, captchas=captchas)

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if g.user is not None and g.user.is_authenticated():
        flash('您已经登录')
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            flash('用户名不存在！')
            return redirect(request.args.get("next") or url_for("login"))
        if user.password != hashlib.md5(form.password.data).hexdigest():
            flash('密码错误！')
            return redirect(url_for('login'))
        session['remember_me'] = form.remember_me.data
        session['username'] = form.username.data
        remember_me = False
        if 'remember_me' in session:
            remember_me = session['remember_me']
            session.pop('remember_me', None)
        login_user(user, remember = remember_me)
        flash("登录成功")
        return redirect(request.args.get("next") or url_for("index"))
    return render_template('login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/profile")
@login_required
def profile():
    pass

