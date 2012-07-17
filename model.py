import pymongo
import pymongo.objectid

class Joke:
	def __init__(self):
		self.db = pymongo.Connection().jokedb
		self.coll = self.db.jokes
	
	def get(self, pk):
		_id = pymongo.objectid.ObjectId(pk)
		joke = self.coll.find_one({'_id':_id})
		return joke
	
	def find(self, q):
		return self.coll.find(q).limit(10)

	@property
	def count(self):
		return self.coll.find().count()
