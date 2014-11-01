import datetime
import random
import hashlib
import pymongo
import jieba
import jieba.analyse
from bson.objectid import ObjectId
import rank

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

	def get_ver(self, key=None):
		if not key:
			key = str(datetime.datetime.now())
		m = hashlib.md5()
		m.update(key)
		return m.hexdigest()[:3]

	def find(self, q):
		return self.coll.find(q).limit(10)
	
	def get_id(self, pk):
		if isinstance(pk, ObjectId):
			return pk
		return ObjectId(pk)

	def incr(self, pk, obj):
		_id = self.get_id(pk)
		return self.coll.update({'_id':_id}, {'$inc': obj})
	
	def vote(self, pk, up=0, down=0):
		'''
		May have problem when multi user vote at same time.
		'''
		_id = self.get_id(pk)
		item = self.get(pk)
		item['up'] += up
		item['down'] += down
		item['rank'] = rank.hot(item['up'], item['down'], item['created'])
		item['ver'] = self.get_ver()
		self.coll.save(item)
		return item['ver']

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
			'ver' : self.get_ver(),
		}
		self.coll.update({'_id': _id}, {'$set': obj})
		return obj

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
			'created' : datetime.datetime.now(),
			'ver' : self.get_ver(),
		}
		#_item = self.coll.update({'md5': md5}, {'$set': item}, upsert=True)
		_id = self.coll.save(item)
		return str(_id)

	def random(self, keyword='', exclude=None):
		r = random.random()
		query = {'r':{'$gte':r}}
		if exclude:
			query['_id'] = {'$nin' : [ObjectId(_id) for _id in exclude]}

		if keyword:	
			query['tags'] = keyword

		item = self.coll.find_one(query)
		if not item:
			query['r'] = {'$lte':r}
			item = self.coll.find_one(query)
		return item

	@property
	def count(self):
		return self.coll.find().count()
