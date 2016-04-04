import wtforms
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, EqualTo
from wtforms import ValidationError
from ..models import User

# A registration form for new users with required fields which users must provide infomation to in order for the form to be processed.
class RegForm(wtforms.Form):
	name = StringField('Name', validators=[Required(), Length(1, 16)], description="Name")
	email = StringField('Email address', validators=[Required(), Length(1, 64), Email()], description="Email")
	password = PasswordField('Password', validators=[
        Required(), EqualTo('password2', message='Passwords do not match.')], description="Password")
	password2 = PasswordField('Confirm password', validators=[Required()], description="Confirm password")
	submit = SubmitField('Register')