# -*- coding: utf-8 -*-
import hashlib
from app import db
from datetime import datetime

LEVEL_USER = 0
LEVEL_PLAYER = 3
LEVEL_SEER = 6
LEVEL_ADMIN = 9

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), unique = True)
    nickname = db.Column(db.String(64), unique = True)
    password = db.Column(db.String(32), nullable=False)
    reg_time = db.Column(db.DateTime, default = datetime.now)
    level = db.Column(db.SmallInteger, default = LEVEL_USER)
    exp = db.Column(db.Integer, default = 0)
    topics = db.relationship('Topic', backref = 'author', lazy = 'dynamic')
    replys = db.relationship('Reply', backref = 'author', lazy = 'dynamic')


    def __init__(self, username, nickname, password):
        self.username = username
        self.nickname = nickname
        self.password = hashlib.md5(password).hexdigest()  #呵呵，这样在插入数据自动给密码哈希了！

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return '<User %r>' % (self.nickname)

class Bz(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    status = db.Column(db.String(64))
    stage = db.Column(db.String(64))
    start_time = db.Column(db.DateTime, default = datetime.now)
    end_time = db.Column(db.DateTime)
    staff_num = db.Column(db.SmallInteger, default = 0)
    player_num = db.Column(db.Integer, default = 0)

class Topic(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    board_id = db.Column(db.Integer)
    category = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    post_time = db.Column(db.DateTime, default = datetime.now)
    replys = db.relationship('Reply', backref = 'thread', lazy = 'dynamic')

class Reply(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    post_time = db.Column(db.DateTime, default = datetime.now)


