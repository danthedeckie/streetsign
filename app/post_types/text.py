from flask import render_template, url_for, escape

def form(data, typeid):
    return render_template('post_types/text.html', post_type=typeid)

def receive(data):
    return {'type':'text', 'content': escape(data.get('content',''))}

def display(data):
    return data['content']

