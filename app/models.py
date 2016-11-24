import datetime, re, hashlib, urllib
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.login import UserMixin

# Give our blog entries some nice URLs. 
# The slugify function takes a string such as 
# A post about Flask and uses a regular expression 
# to turn a string that is human-readable in to a URL, 
# and so returns a-post-about-flask.
def slugify(s):
	return re.sub('[^\w]+', '-', s).lower()

# To Generate gravatar for users and commentors.
def gravatar(self, size):
		return 'http://www.gravatar.com/avatar.php?%s' % urllib.urlencode({
		'gravatar_id': hashlib.md5(self.email).hexdigest(),
		'size': str(size)})

# class Social(UserMixin, db.Model):
# 	id = db.Column(db.Integer, primary_key=True)
# 	provider = db.Column(db.String(64))
# 	email = db.Column(db.String(120), index=True)
# 	name = db.Column(db.String(64))
# 	slug = db.Column(db.String(64), unique=True)
# 	active = db.Column(db.Boolean, default=True)
# 	admin = db.Column(db.Boolean, default=False)
# 	confirmed = db.Column(db.Boolean, default=True)
# 	confirmed_on = db.Column(db.DateTime, default=datetime.datetime.now)
# 	registered_on = db.Column(db.DateTime, default=datetime.datetime.now)

# 	def __init__(self, *args, **kwargs):
# 		super(Social, self).__init__(*args, **kwargs)
# 		self.generate_slug()
# 		self.avatar()

# 	def generate_slug(self):
# 		if self.name:
# 			self.slug = slugify(self.name)

# 	def avatar(self, size=None):
# 		return gravatar(self, size)

# 	@staticmethod
# 	def register(provider, email, name):
# 		registered_on = datetime.datetime.now()
# 		social = Social(provider=provider, email=email, name=name, registered_on=registered_on)
# 		db.session.add(social)
# 		db.session.commit()
# 		return social

# 	def __repr__(self):
# 		return '<Social %r>' % (self.email)

# The User table that has a static function for can be called by any User object to register new users.
# Avatars and slugs(based on the names of the users) will also be create upon registration.
class User(UserMixin, db.Model):
	#__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	provider = db.Column(db.String(64))
	email = db.Column(db.String(120), nullable=False, index=True)
	name = db.Column(db.String(120))
	slug = db.Column(db.String(120), unique=True)
	active = db.Column(db.Boolean, default=True)
	admin = db.Column(db.Boolean, default=False)
	registered_on = db.Column(db.DateTime, default=datetime.datetime.now)
	confirmed = db.Column(db.Boolean)
	confirmed_on = db.Column(db.DateTime, default=None)
	posts = db.relationship('Post', backref='author', lazy='dynamic')
	password_hash = db.Column(db.String(225))

	def __init__(self, *args, **kwargs):
		super(User, self).__init__(*args, **kwargs)
		self.generate_slug()
		self.avatar()

	def generate_slug(self):
		if self.name:
			self.slug = slugify(self.name)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	def avatar(self, size=None):
		return gravatar(self, size)

	def is_admin(self):
		return self.admin
		
	@staticmethod
	def register(name, email, password, provider, confirmed=False):
		registered_on = datetime.datetime.now()
		user = User(confirmed=confirmed, name=name, email=email, registered_on=registered_on, provider=provider)
		user.set_password(password)
		db.session.add(user)
		db.session.commit()
		return user

	def __repr__(self):
		return '<User %r>' % (self.email)
		
post_tags = db.Table('post_tags',
	db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
	db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)


# Bloe entry table with pre-defined statuses.
# A slug will be automatically generated for each post upon creation.
class Post(db.Model):
	#__tablename__ = 'posts'
	STATUS_PUBLIC = 0
	STATUS_DRAFT = 1
	STATUS_DELETED = 2

	id = db.Column(db.Integer, primary_key=True)
	author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	title = db.Column(db.String(100))
	slug = db.Column(db.String(100), unique=True)
	body = db.Column(db.Text)
	status = db.Column(db.SmallInteger, default=STATUS_PUBLIC)
	created_timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
	modified_timestamp = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
	
	tags = db.relationship('Tag', secondary=post_tags,
		backref=db.backref('posts',lazy='dynamic'))

	comments = db.relationship('Comment', backref='post', lazy='dynamic')

	@property
	def tag_list(self):
	    return ', '.join(tag.name for tag in self.tags)
	@property
	def tease(self):
	    return self.body[:150]

	def __init__(self, *args, **kwargs):
		super(Post, self).__init__(*args, **kwargs)  # Call parent constructor.
		self.generate_slug()

	def generate_slug(self):
		self.slug = ''
		if self.title:
			self.slug = slugify(self.title)

	def __repr__(self):
		return '<Post %r>' % (self.title)

# Tag table with auotmatic generation of slug upon creation
class Tag(db.Model):
	#__tablename__ = 'tags'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64))
	slug = db.Column(db.String(64), unique=True)

	def __init__(self, *args, **kwargs):
		super(Tag, self).__init__(*args, **kwargs)
		self.slug = slugify(self.name)

	def __repr__(self):
		return '<Tag %r>' % (self.name)

# Comment table with statuses that are pre-defined.
class Comment(db.Model):
	STATUS_PENDING_MODERATION = 0
	STATUS_PUBLIC = 1
	STATUS_SPAM = 8
	STATUS_DELETED = 9

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64))
	email = db.Column(db.String(64))
	url = db.Column(db.String(100))
	ip_address = db.Column(db.Text)
	body = db.Column(db.Text)
	status = db.Column(db.SmallInteger, default=STATUS_PUBLIC)
	created_timestamp = db.Column(db.DateTime, default=datetime.datetime.now)
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

	def __init__(self, *args, **kwargs):
		super(User, self).__init__(*args, **kwargs)
		self.avatar()

	def avatar(self, size=None):
		return gravatar(self, size)

	def __repr__(self):
		return '<Comment from %r>' % (self.name,)
