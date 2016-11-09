from flask import Flask, Blueprint, render_template, session, redirect, url_for, flash, request, make_response
from flask.ext.login import login_user, logout_user, login_required, current_user
from datetime import datetime
from ..models import User, Social
from ..token import confirm_token, generate_confirmation_token
from .forms import LoginForm
from ..decorators import check_confirmed
from ..email import send_email
import random, string, httplib2, json, requests
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from config import basedir

user_blueprint = Blueprint('user_blueprint', __name__,)

CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web']['client_id']

@user_blueprint.route('/gconnect', methods=['POST'])
def gconnect():
	# Validate state token
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = session.get('credentials')
    stored_gplus_id = session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    session['credentials'] = credentials.to_json()
    session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    session['username'] = data['name']
    session['picture'] = data['picture']
    session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % session['username'])
    print "done!"
    return output

# @user_blueprint.route('/fbconnect', methods=['POST'])
# def fbconnect():
#     if request.args.get('state') != session['state']:
#         response = make_response(json.dumps('Invalid state parameter.'), 401)
#         response.headers['Content-Type'] = 'application/json'
#         return response
#     access_token = request.data

#     app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
#     app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']

#     url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
#     h = httplib2.Http()
#     result = h.request(url, 'GET')[1]

#     userinfo_url = 'https://graph.facebook.com/v2.4/me'

#     token = result.split("&")[0]

#     url = url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
#     h = httplib2.Http()
#     result = h.request(url, 'GET')[1]

#     data = json.loads(result)
#     session['provider'] = 'facebook'
#     session['username'] = data['name']
#     session['email'] = data['email']
#     session['facebook_id'] = data['id']

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