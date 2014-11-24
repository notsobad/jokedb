import pprint
from os import path as osp
import pymongo
import json
from bson.objectid import ObjectId
import redis

BASEDIR = osp.dirname(osp.dirname(osp.realpath(__file__)))
TAGS_FILE = '%s/static/tags.json' % BASEDIR


def count_tags():
    db = pymongo.Connection().jokedb
    coll = db.jokes
    items = coll.find()
    tags = {}
    for item in items:
        for tag in item['tags']:
            tags[tag] = tags.get(tag, 0) + 1
    return tags


def dump_tags(tags):
    data = {k: tags[k] for k in tags if tags[k] >= 20}
    json.dump(data, open(TAGS_FILE, 'w+'), indent=None)


def tags2redis():
    db = pymongo.Connection().jokedb
    rd = redis.Redis()
    coll = db.jokes
    items = coll.find()
    for item in items:
        for tag in item['tags']:
            rd.sadd('tag:%s' % tag, str(item['_id']))

if __name__ == '__main__':
    # print TAGS_FILE
    #tags = count_tags()
    # dump_tags(tags)
    tags2redis()
