import pymongo
from bson.objectid import ObjectId

class Joke:
	def __init__(self):
		self.db = pymongo.Connection().jokedb
		self.coll = self.db.jokes
	
	def get(self, pk):
		_id = ObjectId(pk)
		return self.coll.find_one({'_id':_id})
	
	def find(self, q):
		return self.coll.find(q).limit(10)

	def update(self, pk, item):
		_id = ObjectId(pk)
		return self.coll.update({'_id':_id}, {'$set': item})

	def incr(self, pk, obj):
		_id = ObjectId(pk)
		return self.coll.update({'_id':_id}, {'$inc': obj})
	
	def delete(self, pk):
		_id = ObjectId(pk)
		return self.coll.remove({'_id':_id})
	
	def _md5(self, s):
		m = hashlib.md5()
		m.update(cont)
		return m.hexdigest()

	def add(self, **kwargs):
		cont = kwargs.get('cont', '')
		if not cont:
			return None

		item = {
			'up' : 0,
			'down' : 0,
			'rank' : 0,
			'cont' : cont,
			'md5' : self._md5(cont),
			'r' : random.random(),
			'source' : 'ishuoxiao',
		}
		
		_item = self.coll.update({'md5': md5}, {'$set': item})
		return str(_item['_id'])

	@property
	def count(self):
		return self.coll.find().count()
