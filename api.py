#!/usr/bin/python
#coding=utf-8
import sys
import os
import time
import datetime
import urlparse
import random
import hashlib
import re
import xml.etree.ElementTree as ET
from lib.model import Joke
from lib.pagination import Pagination
from bson.objectid import ObjectId
import tornado.ioloop
import tornado.web
import tornado
import tornado.httpclient
from tornado.options import define, options

WEIXIN_MSG_TPL = '''<xml>
<ToUserName><![CDATA[%(ToUserName)s]]></ToUserName>
<FromUserName><![CDATA[%(FromUserName)s]]></FromUserName>
<CreateTime>%(CreateTime)s</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[%(Content)s]]></Content>
<FuncFlag>%(FuncFlag)s</FuncFlag>
</xml>'''

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
		ver = j.vote(pk, up=up, down=down)
		self.write({'status':'ok', 'ver':ver})

class WeixinMsgHandler(tornado.web.RequestHandler):
	def post(self):
		'''Got msg from weixin
		'''
		tree = ET.fromstring(self.request.body)
		obj = {}
		for item in tree.getchildren():
			obj[item.tag] = item.text

		tag = obj['Content']
		j = Joke()
		item = j.random(keyword=obj['Content'])
		cont = ""
		if item:
			cont = item['cont']
		else:
			cont = u'奇怪，居然没找到...'
		ret = {
			'ToUserName' : obj['FromUserName'],
			'FromUserName' : obj['ToUserName'],
			'CreateTime' : int(time.time()),
			'Content' : cont,
			'FuncFlag' : 0
		}
		self.write(WEIXIN_MSG_TPL % ret)

urls_map = [
	tornado.web.url(r'/api/joke/([^/]+)/', APIJokeHandler, name="api-joke"),
	tornado.web.url(r'/api/vote/', VoteHandler, name="api-vote"),
	tornado.web.url(r'/api/weixin/msg/', WeixinMsgHandler, name="api-weixin-msg"),
]
