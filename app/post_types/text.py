from os.path import abspath, splitext
from flask import render_template_string, escape

def my(ending):
    ''' given '.html', returns (if this is the foobar module)
        the contents of: /where/this/file/is/foodbar.html '''

    with open(splitext(abspath(__file__))[0] + ending,'r') as f:
        return f.read()

def form(data):
    return render_template_string(my('.html'), **data)

def receive(data):
    return {'type':'text', 'content': escape(data.get('content',''))}

def display(data):
    return data['content']

def screen_js():
    return my('.screen.js')
