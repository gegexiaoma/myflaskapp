# coding=utf-8
from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from ..models import User


class LoginForm(Form):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64),Email()])
    password = PasswordField(u'密码', validators=[Required()])
    remember_me = BooleanField(u'记住我')
    submit = SubmitField(u'登录')
    
    
class RegistrationForm(Form):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, u'用户名必须是字母，数字，点或下划线')])
    password = PasswordField(u'密码', validators=[Required(), EqualTo('password2', message=u'两次密码必须匹配.')])
    password2 = PasswordField(u'确认密码', validators=[Required()])
    submit = SubmitField(u'注册')
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已注册.')
            
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户没已被注册.')
            
class ChangePasswordForm(Form):
    old_password = PasswordField(u'旧密码', validators=[Required()])
    password = PasswordField(u'新密码', validators=[
        Required(), EqualTo('password2', message='两次密码必须匹配.')])
    password2 = PasswordField(u'确认新密码', validators=[Required()])
    submit = SubmitField(u'更改密码')


class PasswordResetRequestForm(Form):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64),
                                            Email()])
    submit = SubmitField(u'重置密码请求')


class PasswordResetForm(Form):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64),
                                            Email()])
    password = PasswordField(u'新密码', validators=[
        Required(), EqualTo('password2', message='两次密码必须匹配.')])
    password2 = PasswordField(u'确认新密码', validators=[Required()])
    submit = SubmitField(u'重置密码')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')

class ChangeEmailForm(Form):
    email = StringField(u'新邮箱', validators=[Required(), Length(1, 64),
                                                Email()])
    password = PasswordField(u'密码', validators=[Required()])
    submit = SubmitField(u'更改邮箱地址')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已注册.')
