import wtforms
from wtforms.validators import DataRequired, Email, Optional, URL, Length
from ..models import Post, Tag


class TagField(wtforms.StringField):
	def _value(self):
		if self.data:
			# Display tags as a commma separated list.
			return ', '.join([tag.name for tag in self.data])
		return ''

	def get_tags_from_string(self, tag_string):
		raw_tags = tag_string.split(',')

		# Filter out any empty tag names.
		tag_names = [name.strip().lower() for name in raw_tags if name.strip().lower()]

		# Query the database and retrieve any tags we have already saved.
		existing_tags = Tag.query.filter(Tag.name.in_(tag_names))

		# Determine which tag names are new.
		new_names = set(tag_names) - set([tag.name for tag in existing_tags])

		# Create a list of unsaved Tag instances for the new tags.
		new_tags = [Tag(name=name) for name in new_names]

		# Return all the exisiting tags + all the new, unsaved tags.
		return list(existing_tags) + new_tags

	def process_formdata(self, valuelist):
		if valuelist:
			self.data = self.get_tags_from_string(valuelist[0])
		else:
			self.data = []

class ImageForm(wtforms.Form):
	file = wtforms.FileField('Image file')


class PostForm(wtforms.Form):
	title = wtforms.StringField('Title', validators=[DataRequired()], description='Headline for you post')
	body = wtforms.TextAreaField('Body', validators=[DataRequired()], description='Share your thoughts here')
	status = wtforms.SelectField(
		'Post status', 
		choices=(
			(Post.STATUS_PUBLIC, 'Public'), 
			(Post.STATUS_DRAFT, 'Draft')), 
			coerce=int)
	tags = TagField('Tags', description='Add tags / topics here, separated with commas.')

	def save_post(self, post):
		self.populate_obj(post)
		post.generate_slug()
		return post

class CommentForm(wtforms.Form):
	name = wtforms.StringField('Name', validators=[DataRequired()])
	email = wtforms.StringField('Email', validators=[DataRequired(), Email()])
	url = wtforms.StringField('URL', validators=[Optional(), URL()])
	body = wtforms.TextAreaField('Comment', validators=[DataRequired(), Length(min=10, max=3000)])
	post_id = wtforms.HiddenField(validators=[DataRequired()])

	def validate(self):
		if not super(CommentForm, self).validate():
			return False

		post = Post.query.filter(
			(Post.status == Post.STATUS_PUBLIC) &
			(Post.id == self.post_id)).first()
		if not post:
			return False
		return True