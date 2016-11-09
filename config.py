import os
basedir = os.path.dirname(os.path.realpath(__file__))
 
class BaseConfig(object):
	APPLICATION_DIR = os.path.dirname(os.path.realpath(__file__))
	STATIC_DIR = os.path.join('%s/app/' % APPLICATION_DIR, 'static')
	IMAGES_DIR = os.path.join('%s/' % STATIC_DIR, 'images')

	DEBUG = False
	SECRET_KEY = 'top secret!'
	SECRET_PASSWORD_SALT = 'top secret too!'
	WTF_CSRF_ENABLED = True

	# mail settings
	MAIL_SERVER = 'smtp.gmail.com'
	MAIL_PORT = 587
	MAIL_USE_TLS = False
	MAIL_USE_SSL = True

	# email authentication
	MAIL_USERNAME = 'hahahehe8787@gmail.com'
	MAIL_PASSWORD = 'uglymojo0723'

	# mail accounts
	MAIL_DEFAULT_SENDER = 'hahahehe8787@gmail.com'


class DevelopmentConfig(BaseConfig):

	TESTING = True
	DEBUG = True
	WTF_CSRF_ENABLED = True
	SQLALCHEMY_DATABASE_URI = 'sqlite:///%s/dev.db' % basedir
	SQLALCHEMY_TRACK_MODIFICATIONS = False

