from os.path import abspath, splitext
from flask import render_template_string, url_for, json

def my(ending):
    ''' given '.html', returns (if this is the foobar module)
        the contents of: /where/this/file/is/foodbar.html '''

    with open(splitext(abspath(__file__))[0] + ending,'r') as f:
        return f.read()

def form(data):
    ''' the form for editing this type of post '''
    return render_template_string(my('.form.html'), **data)

def receive(data):
    return {'type':'ajax_hit',
            'render_url': data.get('render_url',''),
            'display_url': data.get('display_url',''),
            'hide_url': data.get('hide_url',''),
            'content':'none'
            }

def display(data):
    return data['content']

def screen_js():
    return my('.screen.js')
