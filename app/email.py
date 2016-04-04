from flask.ext.mail import Message
from app import app, mail

# This function creates the necessary email template for email confirmation which will be sent automatically to the users upon account createion.
def send_email(to, subject, template):
	msg = Message(subject=subject, recipients=[to], html=template, sender=app.config['MAIL_DEFAULT_SENDER'])
	mail.send(msg)