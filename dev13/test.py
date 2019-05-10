from flask import Flask, render_template
from flask_fontawesome import FontAwesome

app = Flask(__name__)
fa = FontAwesome(app)

@app.route('/')
def index():
    return render_template('index.html')

app.run(host='127.0.0.1', port=8080)