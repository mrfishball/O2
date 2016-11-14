import os
from flask import Flask, render_template, g, session, request, url_for
from werkzeug.contrib.atom import AtomFeed
from urlparse import urljoin
from flaskext.markdown import Markdown
from flask.ext.admin import Admin
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.restless import APIManager
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from flask_bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.login import LoginManager, current_user
from .momentjs import momentjs
from flask_mail import Mail
from config import DevelopmentConfig

app = Flask(__name__)

# Load in the configuration for the development environment.
# There are also testing configuration as well as a final deployment configuration.
app.config.from_object(DevelopmentConfig)

# Initialize extensions.
# These are the modules that are being pieced together to form our fully functional website.
# Such as boostrap for theming the site, database migration, login manager for managing current users, server side email authentication, user authentication etc.
lm = LoginManager()
lm.session_protection = 'strong'
lm.init_app(app)

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
Markdown(app, extensions=['codehilite'])
api = APIManager(app, flask_sqlalchemy_db=db)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
moment = Moment(app)
mail = Mail(app)

# Blueprint registration
# Each section of our website is served as individual, interconnected blueprint for better implemenation of features.
from main.routes import main_blueprint
from user.routes import user_blueprint
from posts.routes import posts
app.register_blueprint(main_blueprint)
# Used url_prefix for more readable URLs
app.register_blueprint(user_blueprint, url_prefix='/users')
app.register_blueprint(posts, url_prefix='/posts')

# Admin
# Handles the templating and rendering of the admin dashboard that allows site manager to curate the contents on the server.
# Such as create, modify and delete users, posts, comments, static files etc.
from admin import SlugModelView, UserModelView, PostModelView, BlogFileAdmin, IndexView, CommentModelView
admin = Admin(app, 'Administrator Dashboard', index_view=IndexView())
admin.add_view(PostModelView(models.Post, db.session))
admin.add_view(SlugModelView(models.Tag, db.session))
admin.add_view(UserModelView(models.User, db.session))
admin.add_view(CommentModelView(models.Comment, db.session))
admin.add_view(BlogFileAdmin(app.config['STATIC_DIR'], '/static/', name='Static Files'))

# Set default login landing page and flash message style.
lm.login_view = 'user_blueprint.login'
lm.login_message_category = 'info'

# API manager that handles json requests from the clients to the server.
from helpers import post_preprocessor
api.create_api(
	models.Comment,
	include_columns=['id', 'name', 'url', 'body', 'created_timestamp'],
	include_methods=['avatar'],
	methods=['GET', 'POST'],#, 'DELETE'],
	preprocessors={'POST': [post_preprocessor],
	})

# Login manager to manager users that are currently logged in to our website
@lm.user_loader
def load_user(id):
	return models.User.query.get(int(id)) or models.Social.query.get(int(id))

# Set the current user value so that we can use it to verify current users' sessions and user authentication.
@app.before_request
def before_request():
    g.user = current_user

@app.before_request
def _last_page_visited():
    if "current_page" in session:
        session["last_page"] = session["current_page"]
    session["current_page"] = request.path

#Generate an atom feed for our website.
@app.route('/latest.atom')
def recent_feed():
	feed = AtomFeed(
		'Latest Bog Posts',
		feed_url=request.url,
		url=request.url_root,
		author=request.url_root
	)
	posts = models.Post.query.filter(models.Post.status == models.Post.STATUS_PUBLIC).order_by(models.Post.created_timestamp.desc()).limit(15).all()
	for post in posts:
		feed.add(
			post.title,
			post.body,
			content_type='html',
			url=urljoin(request.url_root, url_for("posts.detail", slug=post.slug)),
			updated=post.modified_timestamp,
			published=post.created_timestamp)
	return feed.get_response()

# Instead of using generic error pages, we use templates that are tailored for our website to give an overall better experience.
@app.errorhandler(403)
def forbidden_page(error):
	return render_template("errors/403.html")

@app.errorhandler(404)
def page_not_found(error):
	return render_template("errors/404.html")

@app.errorhandler(500)
def server_error_page(error):
	return render_template("errors/500.html")