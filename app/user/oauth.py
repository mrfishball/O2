class OAuthSignIn(object):
	providers = None

	def __init__(self, provider_name):
		self.provider_name = provider_name
		credentials = app.config['OAUTH_CREDENTIALS'][provider_name]
		self.consumer_id = credentials['id']
		self.consumer_secret = credentials['secret']

	def authorize(self):
		pass

	def callback(self):
		pass

	def get_callback_url(self):
		return url_for('oauth_callback', provider=self.provider_name, _external=True)


	@classmethod
	def get_provider(self, provider_name):
		if self.providers is None:
			self.providers = {}
			for provider_class in self.__subclass__():
				provider = provider_class()
				self.providers[provider.provider_name] = provider
		return self.provider[provider_name]


class FacebookSignIn(OAuthSignIn):
	def __init__(self):
		super(FacebookSignIn, self).__init__('faceboot')
		self.service = OAuth2Service(
			name='facebook',
			client_id=self.consumer_id,
			client_secret=self.consumer_secret,
			authorize_url=''

			)

class TwitterSignIn(OAuthSignIn):
	pass