# -*- coding: utf-8 -*-
import hashlib
from app import db
from datetime import datetime

LEVEL_USER = 0
LEVEL_PRE_PLAYER = 1
LEVEL_PRE_SEER = 2
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
    actions = db.relationship('Action', backref = 'bz', lazy = 'dynamic')
    settles = db.relationship('Settle', backref = 'bz', lazy = 'dynamic')
    feedbacks = db.relationship('Feedback', backref = 'bz', lazy = 'dynamic')

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

followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('player.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('player.id'))
)
    
class Role(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    name_group = db.Column(db.String(128))
    nation = db.Column(db.String(64))
    position = db.Column(db.String(64))
    tags = db.Column(db.String(64))
    tags_group = db.Column(db.String(256))
    skills = db.Column(db.String(64))
    skills_group = db.Column(db.String(256))

class Player(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    nickname = db.Column(db.String(64))
    blood = db.Column(db.Integer)
    rolename = db.Column(db.String(64))
    rolename_group = db.Column(db.String(128))
    nation = db.Column(db.String(64))
    position = db.Column(db.String(64))
    tags = db.Column(db.String(64))
    tags_group = db.Column(db.String(256))
    skills = db.Column(db.String(64))
    skills_group = db.Column(db.String(256))
    followed = db.relationship('Player', 
        secondary = followers, 
        primaryjoin = (followers.c.follower_id == id), 
        secondaryjoin = (followers.c.followed_id == id), 
        backref = db.backref('followers', lazy = 'dynamic'), 
        lazy = 'dynamic')
    def follow(self, player):
        if not self.is_following(player):
            self.followed.append(player)
            return self

    def is_following(self, player):
        return self.followed.filter(followers.c.followed_id == player.id).count() > 0


class Action(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.Text)
    bz_id = db.Column(db.Integer, db.ForeignKey('bz.id'))
    
class Settle(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.Text)
    bz_id = db.Column(db.Integer, db.ForeignKey('bz.id'))

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    content = db.Column(db.Text)
    bz_id = db.Column(db.Integer, db.ForeignKey('bz.id'))

