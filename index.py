from flask import Flask, g, request, render_template
 
app = Flask(__name__)
app.debug = True
 
@app.route('/')
def hello():
    return render_template('hello.html')
 
from bae.core.wsgi import WSGIApplication
application = WSGIApplication(app)
