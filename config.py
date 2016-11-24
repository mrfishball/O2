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
	MAIL_USERNAME = 'your-email'
	MAIL_PASSWORD = 'password'

	# mail accounts
	MAIL_DEFAULT_SENDER = 'your-email'

	OAUTH_CREDENTIALS = {
    'facebook': {
        'id': '361820247484435',
        'secret': '1d5067a42ddce5ce1c3230602b40e09b'
    },
    'google': {
        'id': '630855590588-vo8prdaiqt3ekvk1u5afujm7t9bvgvrr.apps.googleusercontent.com',
        'secret': 'ePBeiRpdFVIwvinFyrxQ1Kl_'
    }
}

class DevelopmentConfig(BaseConfig):
	TESTING = True
	DEBUG = True
	WTF_CSRF_ENABLED = True
	SQLALCHEMY_DATABASE_URI = 'sqlite:///%s/dev.db' % basedir
	SQLALCHEMY_TRACK_MODIFICATIONS = False

