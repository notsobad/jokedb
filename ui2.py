#!/usr/bin/python
#coding=utf-8
import sys
import os
import datetime
import urlparse
import random
import hashlib
import re
from model import Joke
from pagination import Pagination
from bson.objectid import ObjectId
import tornado.ioloop
import tornado.web
import tornado
import tornado.httpclient
from tornado.options import define, options

static_path = 'static'

class MainHandler(tornado.web.RequestHandler):
	def get(self):
		self.render('index.html')

class JumpHandler(tornado.web.RequestHandler):
	def get(self):
		url = self.get_argument('url', None)
		self.redirect(url)


class AddHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("add.html")

	def post(self):
		item = {}
		cont = self.get_argument('cont', '').strip().encode('utf-8')
		m = hashlib.md5()
		m.update(cont)
		md5 = m.hexdigest()
		if not cont:
			pass
		item['cont'] = cont
		item['md5'] = md5
		item['source'] = 'ishuoxiao'
		item['r'] = random.random() 
		
		j = Joke()
		_item = j.coll.find_one({'md5':md5})
		if _item:
			_id = _item['_id']
		else:
			_id = j.coll.save(item)
			
		self.redirect(reverse_url("joke", str(_id)))

class DeleteHandler(tornado.web.RequestHandler):
	def get(self, pk):
		_id = ObjectId(pk)
		j = Joke()
		j.coll.remove({'_id':_id})
		self.redirect(self.reverse_url("random_page"))
		
class EditHandler(tornado.web.RequestHandler):
	def get(self, pk):
		_id = ObjectId(pk)
		j = Joke()
		item = j.coll.find_one({'_id':_id})
		self.render("edit.html", item=item)

	def post(self, pk):
		_id = ObjectId(pk)
		j = Joke()
		item = j.coll.find_one({'_id':_id})

		cont = self.get_argument('cont', '').strip().encode('utf-8')
		m = hashlib.md5()
		m.update(cont)
		md5 = m.hexdigest()
		if not cont:
			pass
		item['cont'] = cont
		item['md5'] = unicode(md5)
		item['r'] = random.random() 
		#j.coll.update({'_id': _id}, {'$set':item}, upsert=True)
		j.coll.save(item)
		flash(u"修改成功！")
		return redirect(url_for("joke", pk=pk))
			

class AboutHandler(tornado.web.RequestHandler):
	def get(self):
		self.render("about.html")

class PagesHandler(tornado.web.RequestHandler):
	def get(self, page):
		print page
		page = int(page)
		per_page = 5
		j = Joke()
		count = j.count
		items = j.coll.find().sort('_id',1).skip( (page - 1) * per_page ).limit(per_page)
		pagination = Pagination(page, 20, count)
		print items
		self.render("jokes.html", items=items, pagination=pagination)


class JokeHandler(tornado.web.RequestHandler):
	def get(self, pk):
		print pk
		_id = ObjectId(pk)
		j = Joke()
		items = j.coll.find({'_id':{'$gte':_id}}).sort('_id',1).limit(2)
		item = items[0]
		try:
			next_pk = items[1]['_id']
		except:
			next_pk = item['_id']
		self.render("joke.html", item=item, next_pk=next_pk)

class SearchHandler(tornado.web.RequestHandler):
	def get(self, q, page=1):
		q = re.escape(q.strip())
		RE_Q = re.compile(q)
		per_page = 20
		j = Joke()
		docs = j.coll.find({'cont': RE_Q})
		count = docs.count()
		items = docs.sort('_id',1).skip( (page - 1) * per_page ).limit(per_page)
		pagination = Pagination(page, 20, count)
		self.render("jokes.html", items=items, pagination=pagination)


class RandomHandler(tornado.web.RequestHandler):
	def get(self):
		r = random.random()
		j = Joke()
		item = j.coll.find_one({'r':{'$gte':r}})
		if not item:
			item = j.coll.find_one({'r':{'$lte':r}})
				
		self.redirect( self.reverse_url('joke', str(item['_id'])) )



define("port", default=9527, help="port to listen")
define("debug", default=False, help="enable debug?")
tornado.options.parse_command_line()
settings = {
	'template_path' : os.path.join(os.path.dirname(__file__), 'templates'),
	'debug' : options.debug
}

app = tornado.web.Application([
	tornado.web.url(r'/', MainHandler, name="main"),
	tornado.web.url(r'/jump/', JumpHandler, name="jump"),
	tornado.web.url(r'/add/', AddHandler, name="add"),
	tornado.web.url(r'/edit/([^/]+)/', EditHandler, name="edit"),
	tornado.web.url(r'/delete/([^/]+)/', DeleteHandler, name="delete"),
	tornado.web.url(r'/about/', AboutHandler, name="about"),
	tornado.web.url(r'/random/', RandomHandler, name="random_page"),
	tornado.web.url(r'/page/(\d+)/', PagesHandler, name="page"),
	tornado.web.url(r'/joke/([^/]+)/', JokeHandler, name="joke"),
	tornado.web.url(r'/search/([^/]+)/', SearchHandler, name="search"),
	(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path}),
], **settings)

if __name__ == '__main__':
	app.listen(options.port)
	tornado.ioloop.IOLoop.instance().start()
