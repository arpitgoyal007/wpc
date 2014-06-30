from google.appengine.ext import ndb

class User(ndb.Model):
	name = ndb.StringProperty(required=True)
	email = ndb.StringProperty(required=True)
	passwordHash = ndb.StringProperty(required=True, indexed=False)
	following = ndb.KeyProperty(kind='User', repeated=True)
	followers = ndb.KeyProperty(kind='User', repeated=True)
	score = ndb.IntegerProperty(default=0)
	groups = ndb.KeyProperty(kind='Group', repeated=True)
	joined = ndb.DateTimeProperty(auto_now_add=True)

class Group(ndb.Model): # Parent=User (Admin)
	name = ndb.StringProperty(required=True)
	members = ndb.KeyProperty(kind='User', repeated=True)
	created = ndb.DateTimeProperty(auto_now_add=True)

class Itembook(ndb.Model):
	name = ndb.StringProperty(required=True)
	created = ndb.DateTimeProperty(auto_now_add=True)
	updated = ndb.DateTimeProperty(auto_now=True)

	@classmethod
	def of_ancestor(cls, ancestor_key):
		return cls.query(ancestor=ancestor_key).order(-cls.updated)

class Album(Itembook): # Parent=User
	entries = ndb.KeyProperty(kind='Picture', repeated=True)

class Diary(Itembook): # Parent=User
	entries = ndb.KeyProperty(kind='Blog', repeated=True)

class Favoritebook(ndb.Model): # Parent=User
	entries = ndb.KeyProperty(repeated=True)
	updated = ndb.DateTimeProperty(auto_now=True)

	@classmethod
	def of_ancestor(cls, ancestor_key):
		return cls.query(ancestor=ancestor_key).order(-cls.updated)

class Storybook(ndb.Model): # Parent=User
	stories = ndb.KeyProperty(kind='Story', repeated=True)
	updated = ndb.DateTimeProperty(auto_now=True)

	@classmethod
	def of_ancestor(cls, ancestor_key):
		return cls.query(ancestor=ancestor_key).order(-cls.updated)

class MyStorybook(ndb.Model): # Parent=User
	stories = ndb.KeyProperty(kind='Story', repeated=True)
	updated = ndb.DateTimeProperty(auto_now=True)

	@classmethod
	def of_ancestor(cls, ancestor_key):
		return cls.query(ancestor=ancestor_key).order(-cls.updated)

class Post(ndb.Model):
	created = ndb.DateTimeProperty(auto_now_add=True)
	updated = ndb.DateTimeProperty(auto_now=True)
	upvoted = ndb.KeyProperty(kind='User', repeated=True)
	downvoted = ndb.KeyProperty(kind='User', repeated=True)
	likes = ndb.IntegerProperty(default=0)

	@classmethod
	def of_ancestor(cls, ancestor_key):
		return cls.query(ancestor=ancestor_key).order(-cls.updated)

class Item(Post):
	comments = ndb.KeyProperty(kind='Comment', repeated=True)
	permission = ndb.StringProperty(default='Public')
	visibleTo = ndb.KeyProperty(kind='User', repeated=True)
	followed = ndb.KeyProperty(kind='User', repeated=True)

class Picture(Item): # Parent=User
	caption = ndb.StringProperty(default='')
	blobKey = ndb.BlobKeyProperty()
	description = ndb.TextProperty(default='')

class Blog(Item): # Parent=User
	title = ndb.StringProperty(required=True)
	content = ndb.TextProperty(required=True)

class Question(Post): # Parent=User
	content = ndb.StringProperty(required=True)
	answers = ndb.KeyProperty(kind='Answer', repeated=True)
	followed = ndb.KeyProperty(kind='User', repeated=True)

class Answer(Post): # Parent=User
	content = ndb.TextProperty(required=True)
	comments = ndb.KeyProperty(kind='Comment', repeated=True)

class Comment(Post): # Parent=User
	content = ndb.TextProperty(required=True)

class Story(ndb.Model): # Parent=User
	caption = ndb.StringProperty(required=True)
	created = ndb.DateTimeProperty(auto_now=True)
	itemKey = ndb.KeyProperty(required=True)
