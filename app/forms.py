# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import BooleanField, TextField, PasswordField, HiddenField, StringField, validators

class RegistrationForm(Form):
    username = TextField('用户名', [validators.Length(min=3, max=32, message='长度应为3~32个字符')])
    nickname = TextField('昵称', [validators.Length(min=3, max=32, message='长度应为3~32个字符')])
    password = PasswordField('密码', [
        validators.Required(message='请填写密码'),
        validators.EqualTo('confirm', message='密码前后必须一致')
    ])
    confirm = PasswordField('重复密码')
    random = HiddenField()
    captcha = TextField('验证码', [validators.Required(message='请输入验证码')])
    accept_tos = BooleanField('我已经阅读并接受xxx', [validators.Required(message='请阅读并接受用户协议')])

class LoginForm(Form):
    username = TextField('用户名', [validators.Required(message='请输入用户名')])
    password = PasswordField('密码', [validators.Required(message='请输入密码')])
    remember_me = BooleanField('记住我', default = False)
