from flask import render_template, url_for, request
from app import app

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')
