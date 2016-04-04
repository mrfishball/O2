from functools import wraps
from flask import flash, redirect, url_for
from flask.ext.login import current_user

# A decorator function that checks if the users'email addresses on file have been confirmed.
# Certain features on the site are limited to confimred accounts only.
def check_confirmed(func):
	@wraps(func)
	def decorated_function(*args, **kwargs):
		if current_user.confirmed is False:
			return redirect(url_for('user_blueprint.unconfirmed'))
		return func(*args, **kwargs)
	return decorated_function