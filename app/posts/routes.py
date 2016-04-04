import os
from werkzeug import secure_filename
from flask import Flask, Blueprint, render_template, redirect, url_for, flash, session, request, g
from ..models import Post, Tag
from ..helpers import object_list
from forms import PostForm, ImageForm, CommentForm
from flask.ext.login import login_required, current_user
from app import app, db

# Set up the name of the blueprint which will then be registered to our main app module.
posts = Blueprint('posts', __name__,)

# Generate a list of all the posts that are filtered by status.
# Provide a basic search feature for the list of post. Searchable by body and title.
def entry_list(template, query, **context):
	query = filter_status_by_user(query)
	valid_statuses = (Post.STATUS_DRAFT, Post.STATUS_PUBLIC)
	query = query.filter(Post.status.in_(valid_statuses))
	if request.args.get('q'):
		search = request.args['q']
		query = query.filter(
			(Post.body.contains(search)) |
			(Post.title.contains(search)))
	return object_list(template, query, **context)

# If current user is authenticated, will display public posts or pots from the current user
# Posts that are marked as deleted will not be displayed.
def filter_status_by_user(query):
	if not current_user.is_authenticated:
		return query.filter(Post.status == Post.STATUS_PUBLIC)
	else:
		return query.filter(
			(Post.status == Post.STATUS_PUBLIC) |
			((Post.author == current_user) & 
				(Post.status != Post.STATUS_DELETED)))
	return query

# Get posts by slugs or if author is present
def get_post_or_404(slug, author=None):
	query = Post.query.filter(Post.slug == slug)
	if author:
		query = query.filter(Post.author == author)
	else:
		query = filter_status_by_user(query)
	return query.first_or_404()

# Index page for all posts.
@posts.route('/')
def index():
	posts = Post.query.order_by(Post.created_timestamp.desc())
	return entry_list('posts/index.html', posts)

# Provide image upload feature.
# All images uploaded to will places in the static folder.
@posts.route('/image-upload/', methods=['GET', 'POST'])
@login_required
def image_upload():
	if request.method == 'POST':
		form = ImageForm(request.form)
		if form.validate():
			image_file = request.files['file']
			filename = os.path.join(app.config['IMAGES_DIR'], secure_filename(image_file.filename))
			image_file.save(filename)
			flash('Upload successfully %s' % os.path.basename(filename), 'success')
			return redirect(url_for('posts.index'))
	else:
		form = ImageForm()

	return render_template('posts/image_upload.html', form=form)

# Create new posts and add new posts to the database upon for validation.
@posts.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
	if request.method == 'POST':
		form = PostForm(request.form)
		if form.validate():
			post = form.save_post(Post(author=g.user))
			db.session.add(post)
			db.session.commit()
			flash('Post "%s" created successfully.' % post.title, 'success')
			return redirect(url_for('posts.detail', slug=post.slug))
	else:
		form = PostForm()
	return render_template('posts/create.html', form=form)

# Edit existing posts.
# Users must login to edit posts.
# Users can only edit posts that belong to them, not others.
@posts.route('/<slug>/edit/', methods=['GET', 'POST'])
@login_required
def edit(slug):
	post = get_post_or_404(slug, author=None)
	if current_user == post.author:
		if request.method == 'POST':
			form = PostForm(request.form, obj=post)
			if form.validate():
				post = form.save_post(post)
				db.session.add(post)
				db.session.commit()
				flash('Post "%s" has been saved.' % post.title, 'success')
				return redirect(url_for('posts.detail', slug=post.slug))
		else:
			form = PostForm(obj=post)
	else:
		return redirect(url_for('posts.detail', slug=post.slug))

	return render_template('posts/edit.html', post=post, form=form)

# User must login before they can delete a post.
# Users can only their own posts, not others.
@posts.route('/<slug>/delete/', methods=['GET', 'POST'])
@login_required
def delete(slug):
	post = get_post_or_404(slug, author=None)
	if current_user == post.author:
		if request.method == 'POST':
			post.status = Post.STATUS_DELETED
			db.session.add(post)
			db.session.commit()
			flash('Post "%s" has been deleted.' % post.title, 'success')
			return redirect(url_for('posts.index'))
	else:
		return redirect(url_for('posts.detail', slug=post.slug))

	return render_template('posts/delete.html', post=post)

# Create a list of tags which will then be served on the tag index page.
@posts.route('/tags/')
def tag_index():
	return redirect(url_for('posts.index'))

# Display posts of specific tags.
@posts.route('/tags/<slug>')
def tag_detail(slug):
	tag = Tag.query.filter(Tag.slug == slug).first_or_404()
	posts = tag.posts.order_by(Post.created_timestamp.desc())
	return object_list('posts/tag_detail.html', posts, tag=tag)

# Display the post detail page where users can read and comment on.
# Serve as a portal for editing and deleting posts.
@posts.route('/<slug>/')
def detail(slug):
	post = get_post_or_404(slug)
	form = CommentForm(data={'post_id': post.id})
	return render_template('posts/detail.html', post=post, form=form)