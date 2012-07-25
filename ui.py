#!/usr/bin/python
#coding=utf-8
from flask import Flask,request, render_template,redirect,url_for,session,flash
from flask.ext.sqlalchemy import SQLAlchemy
import flask
import jinja2
import datetime
import urlparse
import random
import hashlib
import re
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Table, Column, Integer, String
from model import Joke
from pagination import Pagination
from bson.objectid import ObjectId

app = Flask(__name__)
app.secret_key = '\x9a\xf8pJp\xbf\xbdBY\xb0\xfd\xa68\xac\x809j\x0c\xd6\x89\xc5,\xcf\xc2'

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
	return render_template("index.html")

@app.route("/page/<int:page>")
def pages(page):
	per_page = 5
	j = Joke()
	count = j.count
	items = j.coll.find().sort('_id',1).skip( (page - 1) * per_page ).limit(per_page)
	pagination = Pagination(page, 20, count)
	return render_template("jokes.html", items=items, pagination=pagination)

@app.route("/about.html")
def about():
	return render_template("about.html")

@app.route("/edit/<pk>", methods=['POST', 'GET'])
def edit(pk):
	_id = ObjectId(pk)
	j = Joke()
	item = j.coll.find_one({'_id':_id})

	if request.method == 'POST':
		cont = request.form.get('cont', '').strip().encode('utf-8')
		m = hashlib.md5()
		m.update(cont)
		md5 = m.hexdigest()
		if not cont:
			pass
		item['cont'] = cont
		item['md5'] = unicode(md5)
		item['r'] = random.random() 
		#j.coll.update({'_id': _id}, {'$set':item}, upsert=True)
		j.coll.save(item)
		flash(u"修改成功！")
		return redirect(url_for("joke", pk=pk))
		
	else:
		return render_template("edit.html", item=item)


@app.route("/delete/<pk>", methods=['POST', 'GET'])
def delete(pk):
	_id = ObjectId(pk)
	j = Joke()
	j.coll.remove({'_id':_id})
	flash(u"删除成功!")
	return redirect(url_for("random_page"))
	

@app.route("/add", methods=['POST', 'GET'])
def add():
	if request.method == 'POST':
		item = {}
		cont = request.form.get('cont', '').strip().encode('utf-8')
		m = hashlib.md5()
		m.update(cont)
		md5 = m.hexdigest()
		if not cont:
			pass
		item['cont'] = cont
		item['md5'] = md5
		item['source'] = 'ishuoxiao'
		item['r'] = random.random() 
		

		j = Joke()
		_item = j.coll.find_one({'md5':md5})
		if _item:
			_id = _item['_id']
		else:
			_id = j.coll.save(item)
			
		return redirect(url_for("joke", pk=str(_id)))

	return render_template("add.html")

@app.route("/search/<q>", methods=['POST', 'GET'])
@app.route("/search/<q>/<int:page>", methods=['POST', 'GET'])
def search(q, page=1):
	q = re.escape(q.strip())
	RE_Q = re.compile(q)
	per_page = 20
	j = Joke()
	docs = j.coll.find({'cont': RE_Q})
	count = docs.count()
	items = docs.sort('_id',1).skip( (page - 1) * per_page ).limit(per_page)
	pagination = Pagination(page, 20, count)
	return render_template("jokes.html", items=items, pagination=pagination)


@app.route("/fml", methods=['POST', 'GET'])
def login():
	if request.method == 'POST':
		pwd = request.form.get('pwd', '')
		if pwd == 'notsobad':
			session['is_admin'] = True 
			session['username'] = 'admin'
			return redirect(url_for('pages', page=1))
	return render_template("login.html")

@app.route("/logout", methods=['POST', 'GET'])
def logout():
	session.pop('username','')
	session.pop('is_admin', '')
	return redirect(url_for("index"))


if __name__ == "__main__":
	app.debug = True
	app.run(host='0.0.0.0')
