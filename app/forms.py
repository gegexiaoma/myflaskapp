# coding=utf-8
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required

class NameForm(Form):
	name = StringField(u'每天都有新鲜事，请记录点你的想法?', validators=[Required()])
	submit = SubmitField(u'提交')
