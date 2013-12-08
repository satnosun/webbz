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



