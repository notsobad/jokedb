from flask import Flask,request, render_template

app = Flask(__name__)


@app.route("/")
def hello():
	return "Hello World!"

@app.route("/add/", methods=["POST", "GET"])
def add_url():
	if request.method == 'POST':
		title = request.form['title'] 
		url = request.form['url'] 
		desc = request.form['desc'] 
		print title, url, desc
	return render_template("add_url.html")

if __name__ == "__main__":
	app.debug = True
	app.run(host='0.0.0.0')
