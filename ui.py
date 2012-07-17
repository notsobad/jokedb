#!/usr/bin/python
#coding=utf-8
from flask import Flask,request, render_template,redirect,url_for
from flask.ext.sqlalchemy import SQLAlchemy
import flask
import jinja2
import datetime
import urlparse
import random
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, Integer, String
from model import Joke
from pagination import Pagination
from bson.objectid import ObjectId

app = Flask(__name__)

def url_for_other_page(page):
	args = request.view_args.copy()
	args['page'] = page
	return url_for(request.endpoint, **args)
app.jinja_env.globals['url_for_other_page'] = url_for_other_page

@app.route('/jump/')
def jump():
	url = request.args.get('url')
	return flask.redirect(url)

@app.route('/j/<pk>')
def joke(pk):
	_id = ObjectId(pk)
	j = Joke()
	items = j.coll.find({'_id':{'$gte':_id}}).sort('_id',1).limit(2)
	item = items[0]
	try:
		next_pk = items[1]['_id']
	except:
		next_pk = item['_id']
	return render_template("joke.html", item=item, next_pk=next_pk)

@app.route('/r')
def random_page():
	r = random.random()
	print r
	j = Joke()
	item = j.coll.find_one({'r':{'$gte':r}})
	if not item:
		item = j.coll.find_one({'r':{'$lte':r}})
			
	return flask.redirect( url_for('joke', pk=str(item['_id'])) )

@app.route('/')
def index():
	return flask.redirect('/page/1')

@app.route("/page/<int:page>")
def pages(page):
	per_page = 5
	j = Joke()
	count = j.count
	items = j.coll.find().sort('_id',1).skip( (page - 1) * per_page ).limit(per_page)
	pagination = Pagination(page, 20, count)
	return render_template("index.html", items=items, pagination=pagination)

@app.route("/about.html")
def about():
	return render_template("about.html")

if __name__ == "__main__":
	app.debug = True
	app.run(host='0.0.0.0')
