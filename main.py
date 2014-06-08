#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import re
import urllib
import webapp2
import jinja2
import logging

from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

import utils

template_dir = os.path.join(os.path.dirname(__file__), "Templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class User(ndb.Model):
	"""Models a WPC user"""
	username = ndb.StringProperty(required=True)
	email = ndb.StringProperty(required=True)
	password_hash = ndb.StringProperty(required=True, indexed=False)

class Album(ndb.Model):
	"""Models an album in WPC"""
	title = ndb.StringProperty(required=True)
	created = ndb.DateTimeProperty(auto_now_add=True)
	updated = ndb.DateTimeProperty(auto_now=True)

class Picture(ndb.Model):
	"""Models a picture in WPC"""
	caption = ndb.StringProperty(indexed=False)
	blobKey = ndb.BlobKeyProperty()
	created = ndb.DateTimeProperty(auto_now_add=True)
	updated = ndb.DateTimeProperty(auto_now=True)

	@classmethod
	def query_book(cls, ancestor_key):
		return cls.query(ancestor=ancestor_key).order(-cls.updated)

class Blog(ndb.Model):
	"""Models a blog in WPC"""
	title = ndb.StringProperty(required=True)
	content = ndb.TextProperty(required=True)
	created = ndb.DateTimeProperty(auto_now_add=True)
	updated = ndb.DateTimeProperty(auto_now=True)

	@classmethod
	def query_book(cls, ancestor_key):
		return cls.query(ancestor=ancestor_key).order(-cls.updated)

class PageHandler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

	def pageError(self):
		self.redirect("/")

	def setSecureCookie(self, name, val):
		secureVal = utils.secureCookieVal(name, val)
		self.response.headers.add_header('Set-Cookie', "%s=%s" % (name, str(secureVal)))

	def readSecureCookie(self, name):
		secureVal = self.request.cookies.get(name)
		if secureVal and utils.checkSecureCookieVal(name, secureVal):
			return secureVal.split('|')[0]

	def delCookie(self, name):
		self.response.headers.add_header('Set-Cookie', "%s=" % name)

	def login(self, user):
		self.setSecureCookie('userinfo', "id=%s" % user.key.id())

	def logout(self):
		self.delCookie('userinfo')

	def initialize(self, *a, **kw):
		webapp2.RequestHandler.initialize(self, *a, **kw)
		self.user = self.userCookieAuthenticate()

	def userCookieAuthenticate(self):
		userinfo = utils.formatCookie(self.readSecureCookie('userinfo'))
		userid = userinfo.get('id')
		if userid:
			return User.get_by_id(userid)

class MainHandler(PageHandler):
	def get(self):
		self.render('index.html')

	def post(self):
		try:
			formType = self.request.get('formType')
			if formType == "signin":
				email = self.request.get('email')
				password = self.request.get('password')
				if email and password:
					user = User.get_by_id(email)
					if user:
					#	if password == user.password:
						if utils.validPassword(email, password, user.password_hash):
						#	userinfoCookieVal = str("email="+email)
						#	self.response.headers.add_header('Set-Cookie', str("userinfo="+utils.SecureCookieVal("userinfo", userinfoCookieVal)))
						#	self.response.headers.add_header('Set-Cookie', str("userinfo=email="+email))
							self.login(user)
							self.redirect("/home")
						else:
							errorMsg = "Invalid password!"
							self.render('index.html', signinEmail=email, signinError=errorMsg)
					else:
						errorMsg = "Account doesn't exist for this Email ID!"
						self.render('index.html', signinEmail=email, signinError=errorMsg)
				else:
					errorMsg = "Enter both Email ID and Password!"
					self.render('index.html', signinEmail=email, signinError=errorMsg)
			else:
				username = self.request.get('username')
				email = self.request.get('email')
				password = self.request.get('password')
				verifyPassword = self.request.get('verifyPassword')
				if username and email and password and (verifyPassword == password):
					prev_user = User.get_by_id(email)
					if prev_user:
						errorMsg = "Account already exists for this Email ID!"
						self.render('index.html', username=username, signupEmail=email, signupError=errorMsg)
					else:
						user = User(id=email, username=username, email=email)
						user.password_hash = utils.hashPassword(email, password)
						user.put()
					#	self.response.headers.add_header('Set-Cookie', str("userinfo=email="+email))
					#	self.response.headers.add_header('Set-Cookie', str("userinfo="+utils.SecureCookieVal("userinfo", userinfoCookieVal)))
						self.login(user)
						self.redirect("/home")
				else:
					errorMsg = "Enter all fields!"
					self.render('index.html', username=username, signupEmail=email, signupError=errorMsg)
		except:
			self.pageError()
		
class HomeHandler(PageHandler):
	def get(self):
		try:
			self.render('home.html', username=self.user.username)
		except:
			self.pageError()

class MyStudioHandler(PageHandler):
	def get(self):
		try:
			self.render('myStudio.html', username=self.user.username)
		except:
			self.pageError()

class MyBlogHandler(PageHandler):
	def get(self):
		try:
			blogs = Blog.query_book(self.user.key).fetch()
			self.render('myBlog.html', username=self.user.username, blogs=blogs)
		except:
			self.pageError()

	def post(self):
		try:
			title = self.request.get('title')
			content = self.request.get('content')
			if title and content:
				blog = Blog(title=title, content=content, parent=self.user.key)
				blog.put()
				self.redirect("/myBlog")
			else:
				blogs = Blog.query_book(self.user.key).fetch()
				errorMsg = "Enter both title and content!"
				self.render('myBlog.html', username=self.user.username, title=title, content=content, submitError=errorMsg, blogs=blogs)
		except:
			self.pageError()

class BlogPermalinkHandler(PageHandler):
	def get(self, resource):
		try:
			blog = Blog.get_by_id(int(resource), parent=self.user.key)
			self.render('blogPermalink.html', username=self.user.username, blog=blog)
		except:
			self.pageError()

	def post(self, resource):
		action = self.request.get('actionType')
		blog = Blog.get_by_id(int(resource), parent=self.user.key)
		if action == "delete":
			blog.key.delete()
			self.redirect('/myBlog')

class MyGalleryHandler(PageHandler):
	def get(self):
		try:
			pictures = Picture.query_book(self.user.key).fetch()
			upload_url = blobstore.create_upload_url('/uploadImage')
			self.render('myGallery.html', username=self.user.username, upload_url=upload_url, pictures=pictures)
		except:
			self.pageError()

class ImagePermalinkHandler(PageHandler):
	def get(self, resource):
		try:
			pic = Picture.get_by_id(int(resource), parent=self.user.key)
			self.render('imagePermalink.html', username=self.user.username, pic=pic)
		except:
			self.pageError()

	def post(self, resource):
		action = self.request.get('actionType')
	#	key = self.request.get('postKey')
		pic = Picture.get_by_id(int(resource), parent=self.user.key)
		if action == "delete":
			blobKey = pic.blobKey
			blobInfo = blobstore.BlobInfo.get(blobKey)
			blobInfo.delete()
			pic.key.delete()
			self.redirect('/myGallery')

class ImageUploadHandler(blobstore_handlers.BlobstoreUploadHandler, PageHandler):
	def post(self):
		try:
			caption = self.request.get('caption')
			upload = self.get_uploads('image')
			if len(upload)>0:
				blobInfo = upload[0]
				pic = Picture(parent=self.user.key, caption=caption)
				pic.blobKey = blobInfo.key()
				pic.put()
			#	self.redirect('/serveImage/%s' % blobInfo.key())
				self.redirect('/myGallery')
			else:
				pictures = Picture.query_book(self.user.key).fetch()
				upload_url = blobstore.create_upload_url('/uploadImage')
				errorMsg = "Please upload a file!"
				self.render('myGallery.html', username=self.user.username, upload_url=upload_url, pictures=pictures, caption=caption, submitError=errorMsg)
		except:
			self.pageError()

class ImageServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
	def get(self, resource):
		try:
			resource = str(urllib.unquote(resource))
			blobInfo = blobstore.BlobInfo.get(resource)
			self.send_blob(blobInfo)
		except:
			self.pageError()

class LogoutHandler(PageHandler):
	def get(self):
		self.logout()
		self.redirect('/')

app = webapp2.WSGIApplication([
			('/', MainHandler),
			('/home', HomeHandler),
			('/myStudio', MyStudioHandler),
			('/myBlog', MyBlogHandler),
			('/myBlog/blg/([^/]+)', BlogPermalinkHandler),
			('/myGallery', MyGalleryHandler),
			('/myGallery/img/([^/]+)', ImagePermalinkHandler),
			('/uploadImage', ImageUploadHandler),
			('/serveImage/([^/]+)', ImageServeHandler),
			('/logout', LogoutHandler)
			], debug=True)
