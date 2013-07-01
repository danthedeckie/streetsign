from flask import render_template, url_for, escape

def form(data, **kwargs):
    return render_template('post_types/text.html', **kwargs) 

def receive(data):
    return {'type':'text', 'content': escape(data.get('content',''))}

def display(data):
    return data['content']

