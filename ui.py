#!/usr/bin/python
#coding=utf-8
from flask import Flask,request, render_template,redirect
import flask
import jinja2
from mymongo import CMongo
import datetime
import pymongo
import pymongo.objectid

app = Flask(__name__)
#env = jinja2.Environment(autoescape=True)

class HN:
	def __init__(self):
		pass
	
	def get(self, news_id):
		_id = pymongo.objectid.ObjectId(news_id)
		mongo = CMongo()
		m = mongo.get_connection()
		news = m.hn.news.find_one({'_id':_id})
		return news
	
	def create(self, obj):
		obj['create_time'] = datetime.datetime.now()
		obj['hit'] = 0
		obj['len'] = len(obj['desc'])
		obj['author'] = 'notsobad'
		obj['comment'] = 0
		mongo = CMongo()
		m = mongo.get_connection()
		return m.hn.news.save(obj)

	def remove(self):
		pass
		
	def find(self, q):
		mongo = CMongo()
		m = mongo.get_connection()
		return m.hn.news.find(q).sort('_id', pymongo.DESCENDING)

@app.route('/jump/')
def jump():
	url = request.args.get('url')
	return flask.redirect(url)

@app.route('/news/<news_id>.html')
def news(news_id):
	hn = HN()
	news = hn.get(news_id)
	return render_template("news.html", n=news)

@app.route("/")
def index():
	q = {}
	hn = HN()
	news = hn.find(q)
	return render_template("index.html", news=news)

@app.route("/about.html")
def about():
	return render_template("about.html")



@app.route("/add/", methods=["POST", "GET"])
def add_url():
	if request.method == 'POST':
		title = request.form['title'] 
		url = request.form['url'] 
		desc = request.form['desc'] 
		hn = HN()
		_id = hn.create({'title':title, 'url':url, 'desc':desc})
		next_url = flask.url_for('news', news_id=str(_id))
		return flask.redirect(next_url)


	return render_template("add_url.html")

@app.template_filter('pretty_date')
def pretty_date(time=False):
	"""
	Get a datetime object or a int() Epoch timestamp and return a
	pretty string like 'an hour ago', 'Yesterday', '3 months ago',
	'just now', etc
	"""
	from datetime import datetime
	now = datetime.now()
	if type(time) is int:
		diff = now - datetime.fromtimestamp(time)
	elif isinstance(time,datetime):
		diff = now - time 
	elif not time:
		diff = now - now
	second_diff = diff.seconds
	day_diff = diff.days

	if day_diff < 0:
		return ''

	if day_diff == 0:
		if second_diff < 10:
			return "just now"
		if second_diff < 60:
			return str(second_diff) + " seconds ago"
		if second_diff < 120:
			return  "a minute ago"
		if second_diff < 3600:
			return str( second_diff / 60 ) + " minutes ago"
		if second_diff < 7200:
			return "an hour ago"
		if second_diff < 86400:
			return str( second_diff / 3600 ) + " hours ago"
	if day_diff == 1:
		return "Yesterday"
	if day_diff < 7:
		return str(day_diff) + " days ago"
	if day_diff < 31:
		return str(day_diff/7) + " weeks ago"
	if day_diff < 365:
		return str(day_diff/30) + " months ago"
	return str(day_diff/365) + " years ago"
	

if __name__ == "__main__":
	app.debug = True
	app.run(host='0.0.0.0')
