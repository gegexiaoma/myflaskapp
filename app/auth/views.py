# coding=utf-8
from flask import render_template, redirect, request, url_for, flash, current_app
from . import auth
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User
from .. import db
from .forms import LoginForm, RegistrationForm,ChangePasswordForm,\
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm
from ..email import send_email

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.' and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))
        
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')
    

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit(): 
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash(u'用户名错误或者密码错误.')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'你已退出.')
    return redirect(url_for('main.index'))
    

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, u'确认账户', 'auth/email/confirm', user=user, token=token)
        flash(u'确认邮件已发送.')
        send_email(current_app.config['FLASKY_ADMIN'], u'新加用户', 'auth/email/new_user', user=user)
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)
    

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash(u'你已经确认你的账户. 谢谢!')
    else:
        flash(u'非法链接或者链接已过时限.')
    return redirect(url_for('main.index'))



@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, u'确认账户', 'auth/email/confirm', user=current_user, token=token)
    flash(u'新确认邮件已发送.')
    return redirect(url_for('main.index'))
    
@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash(u'密码已更改.')
            return redirect(url_for('main.index'))
        else:
            flash(u'错误密码.')
    return render_template('auth/change_password.html',form=form)
    
@auth.route('/reset', methods=['GET', 'POST'])
def reset():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, u'重置密码', 'auth/email/reset_password', user=user, token=token, next=request.args.get('next'))
            send_email(current_app.config['FLASKY_ADMIN'], u'重置密码', 'auth/email/new_user', user=user)
        flash(u'重置密码邮件已发送.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
    
@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash(u'密码已更改.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)
    
@auth.route('/change_email_request', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, u'确认邮箱地址', 'auth/email/change_email', user=current_user, token=token)
            flash(u'新邮箱地址确认邮件已发送.')
            return redirect(url_for('main.index'))
        else:
            flash(u'错误邮箱或密码.')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change_email_request/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash(u'邮箱地址已更改.')
    else:
        flash(u'不合理请求.')
    return redirect(url_for('main.index'))

