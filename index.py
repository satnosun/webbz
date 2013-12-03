from flask import Flask, g, request, render_template
 
app = Flask(__name__)
app.debug = True
 
@app.route('/')
@app.route('/index')
def hello():
    return render_template('index.html')
 
if __name__ == '__main__':
    app.run(host='0.0.0.0')
