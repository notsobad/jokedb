#!/usr/bin/python
#coding=utf-8
import sys
import os
import datetime
import urlparse
import random
import hashlib
import re
import json
from bson.objectid import ObjectId
import tornado.ioloop
import tornado.web
import tornado
import tornado.httpclient
from tornado.options import define, options
from lib.model import Joke
from lib.pagination import Pagination
from api import urls_map
import settings

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

class BaseHandler(tornado.web.RequestHandler):
	def get_current_user(self):
		return self.get_secure_cookie('user')

class MainHandler(BaseHandler):
	def get(self):
		self.set_header('Cache-Control', 'max-age=3600')
		self.render('index.html')

class AddHandler(BaseHandler):
	@tornado.web.authenticated
	@tornado.web.addslash
	def get(self):
		self.render("add.html")

	def post(self):
		j = Joke()
		cont = self.get_argument('cont', '').strip().encode('utf-8')
		pk = j.add(cont=cont)
		self.redirect(self.reverse_url("joke", pk))

class DeleteHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self, pk):
		j = Joke()
		j.delete(pk)
		self.redirect(self.reverse_url("main"))
		
class EditHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self, pk):
		j = Joke()
		item = j.get(pk)
		self.render("edit.html", item=item)

	def post(self, pk):
		j = Joke()
		cont = self.get_argument('cont', '').strip().encode('utf-8')
		joke = j.update(cont=cont, pk=pk)
		self.redirect(self.reverse_url("joke", pk) + '?' + joke['ver'])

class AboutHandler(BaseHandler):
	def get(self):
		self.set_header('Cache-Control', 'max-age=3600')
		self.render("about.html")

class NewestHandler(BaseHandler):
	def get(self, page):
		page = int(page)
		per_page = 10
		j = Joke()
		count = j.count
		items = j.coll.find().sort('_id', -1).skip( (page - 1) * per_page ).limit(per_page)
		pagination = Pagination(page, per_page, count)
		self.set_header('Cache-Control', 'max-age=600')
		self.render("newest.html", items=items, pagination=pagination)


class TopHandler(BaseHandler):
	@tornado.web.addslash
	def get(self, page=1):
		page = int(page)
		per_page = 10
		j = Joke()
		count = j.count
		items = j.coll.find().sort('rank',-1).skip( (page - 1) * per_page ).limit(per_page)
		pagination = Pagination(page, per_page, count)
		self.set_header('Cache-Control', 'max-age=600')
		self.render("top.html", items=items, pagination=pagination)


class JokeHandler(BaseHandler):
	def get(self, pk):
		_id = ObjectId(pk)
		j = Joke()
		items = j.coll.find({'_id':{'$gte':_id}}).sort('_id',1).limit(2)
		item = items[0]

		try:
			next_pk = items[1]['_id']
		except:
			next_pk = item['_id']

		if self.request.headers.get('X-PJAX') == 'true':
			tpl = 'joke_body.html'
		else:
			tpl = 'joke.html'
		self.set_header('Cache-Control', 'max-age=3600')
		self.render(tpl, item=item, next_pk=next_pk)

class SearchHandler(BaseHandler):
	def get(self, q, page=1):
		if page:
			page = int(page)
		else:
			page = 1
		kw = re.escape(q.strip())
		RE_Q = re.compile(kw)
		per_page = 20
		j = Joke()
		docs = j.coll.find({'cont': RE_Q})
		count = docs.count()
		items = docs.sort('_id',1).skip( (page - 1) * per_page ).limit(per_page)
		pagination = Pagination(page, per_page, count)
		self.set_header('Cache-Control', 'max-age=3600')
		self.render("search.html", items=items, pagination=pagination, q=q)


class TagHandler(BaseHandler):
	def get(self, tag, page=1):
		if page:
			page = int(page)
		else:
			page = 1
		per_page = 20
		j = Joke()
		docs = j.coll.find({'tags': tag})
		count = docs.count()
		items = docs.sort('_id',1).skip( (page - 1) * per_page ).limit(per_page)
		pagination = Pagination(page, per_page, count)
		self.set_header('Cache-Control', 'max-age=3600')
		self.render("tag.html", items=items, pagination=pagination, tag=tag)


class RandomHandler(BaseHandler):
	def get(self):
		r = random.random()
		j = Joke()
		item = j.coll.find_one({'r':{'$gte':r}})
		if not item:
			item = j.coll.find_one({'r':{'$lte':r}})
		self.set_header('Cache-Control', 'no-cache')
		self.redirect( self.reverse_url('joke', str(item['_id'])) )

class LoginHandler(BaseHandler):
	def get(self):
		try:
			error_message = self.get_argument('error')
		except:
			error_message = ''
		self.set_header('Cache-Control', 'max-age=3600')
		self.render('login.html', error_message=error_message)

	def post(self):
		username = self.get_argument('username', '')
		password = self.get_argument('password', '')
		auth = self.check_permission(username, password)
		if auth:
			self.set_current_user(username)
			self.redirect(self.get_argument('next', '/'))
		else:
			error_msg = u'?error=' + tornado.escape.url_escape('login failed')
			self.redirect(u'/login/'+error_msg)

	def check_permission(self, username, password):
		return (username, password) == settings.AUTH

	def set_current_user(self, user):
		if user:
			self.set_secure_cookie('user', tornado.escape.json_encode(user))
		else:
			self.clear_cookie('user')

class LogoutHandler(BaseHandler):
	def get(self):
		self.clear_cookie('user')
		self.redirect(u'/login/')

class TagsHandler(BaseHandler):
	def get(self):
		self.set_header('Cache-Control', 'max-age=3600')
		cont = open('%s/static/tags.json' % BASE_DIR).read()
		tags = json.loads(cont)
		vals = tags.values()
		_max = max(vals)
		_min = min(vals)
		_slice = (_max- _min) / 5.0
		self.render("tags.html", tags=tags, _min=_min, _slice=_slice)

define("ip", default="0.0.0.0", help="ip to bind")
define("port", default=9527, help="port to listen")
define("debug", default=False, help="enable debug?")
tornado.options.parse_command_line()
confs = {
	'template_path' : os.path.join(os.path.dirname(__file__), 'templates'),
	'debug' : options.debug,
	'login_url' : '/login/',
	'cookie_secret' : 'dt4zRkC72CFnze8z3Jvmq7eif3XsWiyG',
}

app = tornado.web.Application([
	tornado.web.url(r'/', MainHandler, name="main"),
	tornado.web.url(r'/top/(\d+)/', TopHandler, name="top"),
	tornado.web.url(r'/add/', AddHandler, name="add"),
	tornado.web.url(r'/edit/([^/]+)/', EditHandler, name="edit"),
	tornado.web.url(r'/delete/([^/]+)/', DeleteHandler, name="delete"),
	tornado.web.url(r'/about/', AboutHandler, name="about"),
	tornado.web.url(r'/random/', RandomHandler, name="random_page"),
	tornado.web.url(r'/new/(\d+)/', NewestHandler, name="newest"),
	tornado.web.url(r'/joke/([^/]+)/', JokeHandler, name="joke"),
	tornado.web.url(r'/search/([^/]+)/(\d*)/', SearchHandler, name="search"),
	tornado.web.url(r'/tag/([^/]+)/(\d*)/', TagHandler, name="tag"),
	tornado.web.url(r'/login/', LoginHandler, name='login'),
	tornado.web.url(r'/logout/', LogoutHandler, name='logout'),
	tornado.web.url(r'/tags/', TagsHandler, name="tags"),
	(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static'}),
] + urls_map, **confs)

if __name__ == '__main__':
	app.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
