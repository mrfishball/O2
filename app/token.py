from itsdangerous import URLSafeTimedSerializer
from app import app

# This generate a unique token for each email sent for email confirmation purposes.
def generate_confirmation_token(email):
	serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
	return serializer.dumps(email, salt=app.config['SECRET_PASSWORD_SALT'])

# This will confirm an email address by obtaining the token from the users's email addresses.
def confirm_token(token, expiration=3600):
	serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
	try:
		email = serializer.loads(token, salt=app.config['SECRET_PASSWORD_SALT'], max_age=expiration)
	except:
		return False
	return email