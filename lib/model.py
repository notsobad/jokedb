import datetime
import random
import hashlib
import pymongo
import jieba
import jieba.analyse
from bson.objectid import ObjectId

jieba.initialize()
NUM_TAGS = 15

class Joke:
	def __init__(self):
		self.db = pymongo.Connection().jokedb
		self.coll = self.db.jokes
	
	def gen_tags(self, cont):
		tags = jieba.analyse.extract_tags(cont, topK=NUM_TAGS)
		return tags

	def get(self, pk):
		_id = self.get_id(pk)
		return self.coll.find_one({'_id':_id})
	
	def find(self, q):
		return self.coll.find(q).limit(10)
	
	def get_id(self, pk):
		if isinstance(pk, ObjectId):
			return pk
		return ObjectId(pk)

	def update(self, pk, item):
		_id = self.get_id(pk)
		return self.coll.update({'_id':_id}, {'$set': item})

	def incr(self, pk, obj):
		_id = self.get_id(pk)
		return self.coll.update({'_id':_id}, {'$inc': obj})
	
	def delete(self, pk):
		_id = self.get_id(pk)
		return self.coll.remove({'_id':_id})
	
	def _md5(self, cont):
		m = hashlib.md5()
		m.update(cont)
		return unicode(m.hexdigest())

	def update(self, **kwargs):
		cont = kwargs.get('cont', '')
		pk = kwargs.get('pk', '')
		if not cont:
			return None
		_id = self.get_id(pk)
		obj = {
			'cont' : cont,
			'md5' : self._md5(cont),
			'tags' : self.gen_tags(cont),
		}
		self.coll.update({'_id': _id}, {'$set': obj})

	def add(self, **kwargs):
		cont = kwargs.get('cont', '')
		pk = kwargs.get('pk', '')
		if not cont:
			return None
		
		md5 = self._md5(cont)
		item = {
			'up' : 0,
			'down' : 0,
			'rank' : 0,
			'cont' : cont,
			'md5' : md5,
			'r' : random.random(),
			'source' : 'ishuoxiao',
			'tags' : self.gen_tags(cont),
			'created' : datetime.datetime.now()
		}
		#_item = self.coll.update({'md5': md5}, {'$set': item}, upsert=True)
		_id = self.coll.save(item)
		return str(_id)

	@property
	def count(self):
		return self.coll.find().count()
