from flask.ext.admin import AdminIndexView, expose
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin.contrib.fileadmin import FileAdmin
from wtforms.fields import SelectField, PasswordField
from models import User, Tag, Post, Comment, post_tags
from flask import g, url_for, redirect, request, flash

# To determine the conditions for administrative access.
class AdminAuthentication(object):
	def is_accessible(self):
		return g.user.is_authenticated and g.user.is_admin()

# A base mixin that combines the admin authentication fucntion and the ModelView function that will then be passed in to other fucntions.
class BaseModelView(AdminAuthentication, ModelView):
	pass

# For modifying existing tags. 
class SlugModelView(BaseModelView):
	def on_model_change(self, form, model, is_created):
		model.generate_slug()
		return super(SlugModelView, self).on_model_change(form, model, is_created)

# The entry management section of the admin dashboard which allows admins to see all the posts currently in the database regardless of status.
# Admins can also create, modify and delete entries directly from the dashboard.
# Ability to search with varies filters, of specific attributes.
class PostModelView(SlugModelView):
	_status_choices = [(choice, label) for choice, label in [
		(Post.STATUS_PUBLIC, 'Public'),
		(Post.STATUS_DRAFT, 'Draft'),
		(Post.STATUS_DELETED, 'Deleted'),
	]]
	column_choices = {
		'status': _status_choices,
	}
	column_filters = [
		'status', User.name, User.email, 'created_timestamp'
	]
	column_list = ['title', 'status', 'author', 'tease', 'tag_list', 'created_timestamp']
	column_searchable_list = ['title', 'body']
	column_select_related_list = ['author']

	form_ajax_refs = {
		'author': {
			'fields': (User.name, User.email),
		},
	}
	form_args = {
		'status': {'choices': _status_choices, 'coerce': int},
	}
	form_columns = ['title', 'body', 'status', 'author', 'tags']
	form_overrides = {'status': SelectField}

# The user management section of the admin dashboard which allows admins to see all the users currently in the database.
# Admins can also create, modify and delete users directly from the dashboard.
# Ability to search with varies filters, of specific attributes.
class UserModelView(SlugModelView):
	column_filters = [
		User.name, User.email, 'active', 'registered_on', 'confirmed', 'admin'
	]
	column_list = ['email', 'name', 'active', 'registered_on', 'confirmed', 'admin']

	column_searchable_list = ['name', 'email']
	
	form_columns = ['email', 'password', 'name', 'active', 'admin']
	form_extra_fields = {
		'password': PasswordField('New password'),
	}

	def on_model_change(self, form, model, is_created):
		if form.password.data:
			model.password_hash = User.set_password(form.password.data)
		return super(UserModelView, self).on_model_change(form, model, is_created)

# The comment management section of the admin dashboard which allows admins to see all the users currently in the database.
# Admins can also create, modify and delete users directly from the dashboard.
# Ability to search with varies filters, of specific attributes.
class CommentModelView(SlugModelView):
	_status_choices = [(choice, label) for choice, label in [
		(Comment.STATUS_PENDING_MODERATION, 'Pending'),
		(Comment.STATUS_PUBLIC, 'Public'),
		(Comment.STATUS_SPAM, 'Spam'),
		(Comment.STATUS_DELETED, 'Deleted'),
	]]
	column_choices = {
		'status': _status_choices,
	}
	column_filters = [Comment.name, Comment.email, Comment.url, 'created_timestamp', 'status']

	column_list = ['name', 'email', 'url', 'created_timestamp', 'status']

	column_searchable_list = ['name', 'email']

	form_args = {
		'status': {'choices': _status_choices, 'coerce': int},
	}
	form_overrides = {'status': SelectField}


# Static files management section where admins can delete static files such as images, css and js files etc.
class BlogFileAdmin(AdminAuthentication, FileAdmin):
	pass

# Provides a portal for admin access and authentication.
class IndexView(AdminIndexView):
	@expose('/')
	def index(self):
		if not (g.user.is_authenticated):
			return redirect(url_for('user_blueprint.login', next=request.path))
		elif not (g.user.is_admin()):
			flash('Administrator access denied!', 'danger')
			return redirect(url_for('user_blueprint.login', next=request.path))
		return self.render('admin/index.html')