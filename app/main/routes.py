from flask import Flask, Blueprint, render_template, session, redirect, url_for, flash, request
from flask.ext.login import login_user, logout_user, login_required
from datetime import datetime
from .form import RegForm
from ..models import User
from ..token import generate_confirmation_token
import datetime
from ..email import send_email

# Name of this blueprint for app module registration.
main_blueprint = Blueprint('main', __name__,)

# Define route and alternative routes for the index page of our website.
# Validate form data then, before user registration, datatbase is inquried for any exsiting or duplicate users.
# Email confimration is sent and user is logged in with unconfimred status.
@main_blueprint.route('/', methods=['GET', 'POST'])
@main_blueprint.route('/index', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		form = RegForm(request.form)
		if form.validate():
			user = User.query.filter_by(email=form.email.data).first()
			if user is None or user.provider != 'own':
				provider = 'own'
				user = User.register(provider=provider, name=form.name.data, email=form.email.data, password=form.password.data)
				token = generate_confirmation_token(user.email)
				confirm_url = url_for('user_blueprint.confirm_email', token=token, _external=True)
				html = render_template('user/activate.html', confirm_url=confirm_url)
				subject = 'Please confirm your email.'
				send_email(user.email, subject, html)
				login_user(user)
				flash('A confirmation email has been sent.', 'success')
				return redirect(url_for('user_blueprint.unconfirmed'))
			else:
				flash('Looks like this email address has already been registered.', 'warning')
	else:
		form = RegForm()
	return render_template('main/index.html', form=form)