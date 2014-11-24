#!/usr/bin/python
# coding=utf-8
import sys
import os
import time
import datetime
import urlparse
import random
import hashlib
import re
import xml.etree.ElementTree as ET
from .lib.model import Joke
from .lib.pagination import Pagination
from bson.objectid import ObjectId
import tornado.ioloop
import tornado.web
import tornado
import tornado.httpclient
from tornado.options import define, options
import redis
from . import settings

rd = redis.Redis()

WEIXIN_MSG_TPL = '''<xml>
<ToUserName><![CDATA[%(ToUserName)s]]></ToUserName>
<FromUserName><![CDATA[%(FromUserName)s]]></FromUserName>
<CreateTime>%(CreateTime)s</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[%(Content)s]]></Content>
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
        self.write({'status': 'ok', 'ver': ver})


class WeixinMsgHandler(tornado.web.RequestHandler):

    def get(self):
        arr = sorted([settings.WEIXIN_TOKEN, self.get_argument(
            'timestamp', ''), self.get_argument('nonce', '')])
        m = hashlib.sha1()
        m.update(''.join(arr))
        sign = m.hexdigest()
        #__import__('pdb').set_trace()
        if sign == self.get_argument('signature', ''):
            self.write(self.get_argument('echostr', ''))
        else:
            self.send_error(403)

    def post(self):
        '''Got msg from weixin
                 <xml>
                 <ToUserName><![CDATA[toUser]]></ToUserName>
                 <FromUserName><![CDATA[fromUser]]></FromUserName>
                 <CreateTime>1348831860</CreateTime>
                 <MsgType><![CDATA[text]]></MsgType>
                 <Content><![CDATA[this is a test]]></Content>
                 <MsgId>1234567890123456</MsgId>
                 </xml>
        '''
        tree = ET.fromstring(self.request.body)
        obj = {}
        for item in tree.getchildren():
            obj[item.tag] = item.text

        cmd = obj['Content']
        uid = obj['FromUserName']

        j = Joke()
        item = None

        cont = ''
        help_text = (u"输入h、help显示本帮助\n"
                     u"输入r、random返回随机笑话\n"
                     u"输入关键词,如“老师”、“老板”、“公交车”等，就会返回对应的笑话。\n"
                     u"Have fun!")
        rd_key = 'weixin:%s' % uid
        exclude = rd.smembers(rd_key)
        if cmd in ('h', 'help'):
            cont = help_text
        elif cmd in ('r', 'random'):
            item = j.random(exclude=exclude)
        else:
            item = j.random(keyword=obj['Content'], exclude=exclude)

        if not cont:
            if item:
                rd.sadd(rd_key, str(item['_id']))
                rd.expire(rd_key, 300)
                cont = item['cont']
            else:
                cont = u'呃，没找到...试试其它词吧\n' + help_text

        ret = {
            'ToUserName': obj['FromUserName'],
            'FromUserName': obj['ToUserName'],
            'CreateTime': int(time.time()),
            'Content': cont,
        }
        self.write(WEIXIN_MSG_TPL % ret)

urls_map = [
    tornado.web.url(r'/api/joke/([^/]+)/', APIJokeHandler, name="api-joke"),
    tornado.web.url(r'/api/vote/', VoteHandler, name="api-vote"),
    tornado.web.url(r'/api/weixin/', WeixinMsgHandler, name="api-weixin"),
]
