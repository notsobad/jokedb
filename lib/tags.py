import sys
import jieba
import jieba.analyse
from optparse import OptionParser
from model import Joke

jieba.initialize()
NUM_TAGS = 15

def get_tags(cont):
	tags = jieba.analyse.extract_tags(cont, topK=NUM_TAGS)
	return tags

def update_tag(pk):
	pass

def recreate_tags():
	j = Joke()
	items = j.coll.find()
	for item in items:
		tags = get_tags(item['cont'])
		#j.update(item['_id'], {'tags':tags})
		j.update(**item)
		print 'update: %s, %s tags' % (item['_id'], len(tags))

if __name__ == '__main__':
	recreate_tags()
