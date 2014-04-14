#!/usr/bin/env python
#encoding: utf-8

import sys
import time

import pymongo
from pymongo.errors import AutoReconnect

import config

class CMongo():
	""" MongoDB 接口 """
	def __init__(self, servers=None, **kw):
		self._conn = None

		if not servers:
			servers = config.mongo_uri
		self._servers = servers
		
		self._args = kw


	def get_connection(self):
		if not self._conn:
			while True:
				try:
					self._conn = pymongo.Connection(self._servers, **self._args)
					break
				except AutoReconnect, e:
					print >>sys.stderr, 'pymongo.Connection: %s' % str(e)
					time.sleep(10)

		return self._conn

	
	def __del__(self):
		if self._conn:
			self._conn.disconnect()
			self._conn = None


