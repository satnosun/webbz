#-*- coding: utf-8 -*-
import sys
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

from flask import g, request, render_template, session, url_for, escape, redirect, flash
from flask.ext.login import login_user, logout_user, current_user, login_required
from app import app, db, login_manager
from forms import RegistrationForm, LoginForm, TopicForm, ReplyForm
from models import User, Topic, Reply, Bz, Role, Player, Action, Settle, Feedback, LEVEL_USER, LEVEL_PLAYER, LEVEL_SEER, LEVEL_ADMIN, LEVEL_PRE_PLAYER, LEVEL_PRE_SEER
import CaptchasDotNet
import hashlib
from flask.ext.admin import Admin, BaseView, expose, AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView


admin = Admin(app, name='三国版杀', index_view=AdminIndexView(name='概况'))
class MyBaseView(BaseView):
    def is_accessible(self):
        return g.user.is_authenticated()
    @expose('/')
    def index(self):
        return self.render('admin/index.html')
    
    @expose('/test/')
    def test(self):
        return self.render('admin/test.html')


admin.add_view(MyBaseView(name='Hello', endpoint='hello'))
admin.add_view(MyBaseView(name='Hello 1', endpoint='test1', category='Test'))
#admin.add_view(MyBaseView(name='test'))

class UserView(ModelView):
    # Disable model creation
    can_create = False

    # 重写显示的字段
    column_list = ('username', 'password', 'level')

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(UserView, self).__init__(User, session, **kwargs)

class BzView(ModelView):
    # 重写显示的字段
    column_list = ('id', 'name', 'status')

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(BzView, self).__init__(Bz, session, **kwargs)
class PlayerView(ModelView):
    # 重写显示的字段
    column_list = ('id', 'name', 'nickname')

    def __init__(self, session, **kwargs):
        # You can pass name and other parameters if you want to
        super(PlayerView, self).__init__(Player, session, **kwargs)

admin.add_view(BzView(db.session))
admin.add_view(PlayerView(db.session))

admin.add_view(UserView(db.session))


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

@login_manager.user_loader
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

@app.route('/rule')
def rule():
    return render_template('rule.html',
        title = '规则')

@app.route('/event')
def event():
    return render_template('event.html',
        title = '活动')
		
@app.route('/game')
def game():
    return render_template('game.html',
        title = '游戏')
		
@app.route('/status')
def status():
    bz = db.session.query(Bz).filter(Bz.status != u'已完结').first()
    bzs = Bz.query.all()
    p_left = Player.query.filter_by(name = '').first()
    return render_template('status.html',
        bzs = bzs,
        bz = bz,
        p_left = p_left,
        user = g.user,
        title = '概况')

@app.route('/apply_player')
def apply_player():
    if g.user.level == LEVEL_USER:
        u = User.query.filter_by(id = g.user.id).first()
        u.level = LEVEL_PRE_PLAYER
        db.session.commit()
        return redirect(url_for("status"))
    else:
        return redirect(request.args.get("next") or url_for("index"))

@app.route('/apply_seer')
def apply_seer():
    if g.user.level == LEVEL_USER:
        u = User.query.filter_by(id = g.user.id).first()
        u.level = LEVEL_PRE_SEER
        db.session.commit()
        return redirect(url_for("status"))
    else:
        return redirect(request.args.get("next") or url_for("index"))

@app.route('/pick_player')
def pick_player():
    pass

@app.route('/pick_seer')
def pick_seer():
    if g.user.level == LEVEL_ADMIN:
        users_pre = User.query.filter_by(level=LEVEL_PRE_SEER).all()
        users_seer = User.query.filter_by(level=LEVEL_SEER).all()
        return render_template('pick_seer.html',
            users_pre = users_pre,
            users_seer = users_seer,
            title = '任命天庭')
    else:
        return redirect(url_for("status"))

@app.route('/cl/<int:user_id>&<int:level>')
def change_level(user_id, level):
    if g.user.level == LEVEL_ADMIN:
        u = User.query.filter_by(id=user_id).first()
        u.level = level
        db.session.commit()
        return redirect(url_for("pick_seer"))

@app.route('/naming_id', methods=['GET', 'POST'])
def naming_id():
    bz = db.session.query(Bz).filter(Bz.status != u'已完结').first()
    if g.user.level == LEVEL_SEER:
        players = Player.query.all()
        players_num = len(players)
        players_left = range(1, bz.player_num-players_num+1)
        if request.method == 'POST':
            list_playernames = request.form['str_playernames'].split(",")
            i = 0
            for player in players:
                player.name = list_playernames[i]
                i = i + 1
                db.session.commit()
            while bz.player_num - i:
                player = Player(name=list_playernames[i])
                i = i + 1
                db.session.add(player)
                db.session.commit()
            return redirect(url_for("status"))
        return render_template('naming_id.html',
            players = players,
            players_left = players_left,
            title = '命名马甲')
    else:
        return redirect(url_for("status"))

@app.route('/cbs/<int:bz_id>&<status>')
def change_bz_status(bz_id, status):
    bz = db.session.query(Bz).filter(Bz.status != u'已完结').first()
    if g.user.level == LEVEL_SEER:
        return redirect(url_for("status"))

@app.route('/roll_role')
def roll_role():
    pass


    




