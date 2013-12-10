#-*- coding: utf-8 -*-
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

from flask import g, request, render_template, session, url_for, escape, redirect, flash
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, lm
from forms import RegistrationForm, LoginForm, TopicForm, ReplyForm
from models import User, Topic, Reply, LEVEL_USER, LEVEL_PLAYER, LEVEL_SEER, LEVEL_ADMIN
import CaptchasDotNet
import hashlib

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html',
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

@app.route('/forum')
def forum():
    return render_template('forum.html',
        title = '论坛')

@app.route('/b/<int:board_id>')
def show_board(board_id):
    if board_id == 0:
        topics = Topic.query.all()
        return render_template('board.html',
            board_id = board_id,
            topics = topics,
            title = '新建')

@app.route('/t/<int:topic_id>')
def show_topic(topic_id):
    topic = Topic.query.filter_by(id = topic_id).first()
    replys = Reply.query.all()
    return render_template('topic.html',
            topic = topic,
            replys = replys,
            title = '新建')

@app.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = TopicForm()
    flash(form.board_id.data)
    if form.validate_on_submit():
        u = User.query.filter_by(id = g.user.id).first()
        topic = Topic(board_id=form.board_id.data, category=form.category.data, author=u, title=form.title.data, content=form.content.data)
        db.session.add(topic)
        db.session.commit()
        flash("发表成功")
        return redirect(request.args.get("next") or url_for("index"))
    form.board_id.data = request.args.get('board_id', '')
    return render_template('new.html',
        form = form,
        title = '新建')

@app.route('/reply', methods=['GET', 'POST'])
@login_required
def reply():
    form = ReplyForm()
    if form.validate_on_submit():
        u = User.query.filter_by(id = g.user.id).first()
        t = Topic.query.filter_by(id = form.topic_id.data).first()
        reply = Reply(thread=t, author=u, content=form.content.data)
        db.session.add(reply)
        db.session.commit()
        flash("回复成功")
        return redirect(request.args.get("next") or url_for("index"))
    form.topic_id.data = request.args.get('topic_id', '')
    return render_template('reply.html',
        form = form,
        title = '新建')
