from flask import Flask, Blueprint, render_template, session, redirect, url_for, flash, request, make_response
from flask.ext.login import login_user, logout_user, login_required, current_user
from datetime import datetime
from ..models import User
from ..token import confirm_token, generate_confirmation_token
from .forms import LoginForm
from ..decorators import check_confirmed
from ..email import send_email
import random, string, httplib2, json, requests
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from config import basedir
from .oauth import OAuthSignIn

user_blueprint = Blueprint('user_blueprint', __name__,)

@user_blueprint.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@user_blueprint.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    oauth = OAuthSignIn.get_provider(provider)
    provider, token, name, email = oauth.callback()
    if email is None:
        flash('Authentication failed.')
        return redirect(url_for('main.index'))
    user = User.query.filter_by(email=email).first()
    if not user or user.provider != provider:
        user = User.register(confirmed=True, provider=provider, name=name, email=email, password=token)
    login_user(user)
    return redirect(request.args.get('next') or url_for('user_blueprint.user', email=email))

@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	session['state'] = state
	if current_user is not None and current_user.is_authenticated:
		return redirect(url_for('main.index'))
	elif request.method == 'POST':
		form = LoginForm(request.form)
		if form.validate():
			user = User.query.filter_by(email=form.email.data).first()
			if user is None or not user.verify_password(form.password.data):
				flash('Incorrect email or password!', 'danger')
				return redirect(url_for('user_blueprint.login', **request.args))
			login_user(user, remember=True)
			flash('hi, %s!' % user.name, 'success')
			return redirect(request.args.get('next') or url_for('user_blueprint.user', email=form.email.data))
	else:
		form = LoginForm()
	return render_template('user/login.html', form=form, STATE=state)

@user_blueprint.route('/logout')
def logout():
	logout_user()
	flash('You have been logged out.', 'success')
	return redirect(url_for('main.index'))

@user_blueprint.route('/protected', methods=['GET', 'POST'])
@login_required
@check_confirmed
def protected():
	return render_template('user/protected.html')

# @user_blueprint.route('/social/<email>', methods=['GET', 'POST'])
# @login_required
# @check_confirmed
# def social(email):
# 	user = Social.query.filter_by(email=email).first_or_404()
# 	if user is None:
# 		flash('User %s not found.' % email, 'warning')
# 		return redirect(url_for('main.index'))
# 	comment = random.randint(154, 2856)
# 	thumbsup = random.randint(267, 5213)
# 	return render_template('user/user.html', user=user, comment=comment, thumbsup=thumbsup)

@user_blueprint.route('/user/<email>', methods=['GET', 'POST'])
@login_required
@check_confirmed
def user(email):
	user = User.query.filter_by(email=email).first_or_404()
	if user is None:
		flash('User %s not found.' % email, 'warning')
		return redirect(url_for('main.index'))
	comment = random.randint(154, 2856)
	thumbsup = random.randint(267, 5213)
	return render_template('user/user.html', user=user, comment=comment, thumbsup=thumbsup)

@user_blueprint.route('/confirm/<token>')
@login_required
def confirm_email(token):
	try:
		email = confirm_token(token)
	except:
		flash('The confirmation link is invalid or has expired.', 'warning')
	user = User.query,filter_by(email=email).first_or_404()
	if user.confirmed:
		flash('Account already confirmed. Please login.', 'info')
	else:
		user.confirmed = True
		user.confirmed_on = datetime.datetime.now()
		db.session.add(user)
		db.session.commit()
		flash('You have confirmed your account. Thanks!', 'success')
	return redirect(url_for('user_blueprint.protected'))

@user_blueprint.route('/unconfirmed')
@login_required
def unconfirmed():
	if current_user.confirmed:
		return redirect('user_blueprint.protected')
	return render_template('user/unconfirmed.html')

@user_blueprint.route('/resend')
@login_required
def resend_confirmation():
	token = generate_confirmation_token(current_user.email)
	confirm_url = url_for('user_blueprint.confirm_email', token=token, _external=True)
	html = render_template('user/activate.html', confirm_url=confirm_url)
	subject = "Please confirm your email"
	send_email(current_user.email, subject, html)
	flash('A new confirmation email has been sent.', 'info')
	return redirect(url_for('user_blueprint.unconfirmed'))