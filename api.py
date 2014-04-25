#!/usr/bin/python
#coding=utf-8
import sys
import os
import datetime
import urlparse
import random
import hashlib
import re
from lib.model import Joke
from lib.pagination import Pagination
from bson.objectid import ObjectId
import tornado.ioloop
import tornado.web
import tornado
import tornado.httpclient
from tornado.options import define, options

class APIJokeHandler(tornado.web.RequestHandler):
	def get(self, pk):
		j = Joke()
		item = j.get(pk)
		item['pk'] = str(item['_id'])
		item['created'] = str(item['created'])
		del item['_id']
		self.write(item)

class VoteHandler(tornado.web.RequestHandler):
	def post(self):
		'''
		pk=4ff9bb18fc5d007006dbfc8d&act=up
		'''
		pk = self.get_argument('pk')
		act = self.get_argument('act')
		j = Joke()
		assert act in ('up', 'down')
		up = down = 0
		if act == 'up':
			up = 1
		else:
			down = 1
		j.vote(pk, up=up, down=down)
		self.write({'status':'ok'})

urls_map = [
	tornado.web.url(r'/api/joke/([^/]+)/', APIJokeHandler, name="api-joke"),
	tornado.web.url(r'/api/vote/', VoteHandler, name="api-vote"),
]
