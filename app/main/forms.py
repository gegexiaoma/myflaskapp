# coding=utf-8
from flask_wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, SelectField, BooleanField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp
from ..models import User, Role
from flask_pagedown.fields import PageDownField

class CommentForm(Form):
    body = StringField(u'写点评论', validators=[Required()])
    submit = SubmitField(u'提交')

class PostForm(Form):
    body = PageDownField(u"每天都有好心情，请记录下来?", validators=[Required()])
    submit = SubmitField(u'提交')

class EditProfileForm(Form):
    name = StringField(u'真实姓名', validators=[Length(1, 64)])
    location =StringField(u'位置',validators=[Length(1, 64)])
    about_me = TextAreaField(u'关于我')
    submit = SubmitField(u'提交')
    
class EditProfileAdminForm(Form):
    email = StringField(u'邮箱', validators=[Required(), Length(1, 64), Email()])
    username = StringField(u'用户名', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, u'用户名必须是字母，数字，点或下划线')])
    confirmed = BooleanField(u'已验证')
    role = SelectField(u'身份', coerce=int)
    name = StringField(u'真实姓名', validators=[Length(0, 64)])
    location = StringField(u'位置', validators=[Length(0, 64)])
    about_me = TextAreaField(u'关于我') 
    submit = SubmitField(u'提交')
    
    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)for role in Role.query.order_by(Role.name).all()]
        self.user = user
        
    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError(u'邮箱已注册.')
            
    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError(u'用户名已被使用.')
