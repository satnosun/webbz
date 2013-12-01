from flask import Flask, g, request, render_template
 
app = Flask(__name__)
app.debug = True
 
@app.route('/')
def hello():
    return render_template('hello.html')
 
if __name__ == '__main__':
    app.run(host='0.0.0.0')
