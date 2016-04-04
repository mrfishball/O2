import wtforms
from wtforms import validators
from..models import User

class LoginForm(wtforms.Form):
	#name = fields.StringField('What is your name?', validators=[Required(), Length(1, 16)])
	email = wtforms.StringField('Email address', [validators.Required(), validators.Email()], description='Email address')
	password = wtforms.PasswordField('Password', [validators.Required()], description='Password')
	remember_me = wtforms.BooleanField('Remeber me?', default=True)
	submit = wtforms.SubmitField('Login')