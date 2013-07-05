from flask import render_template, escape

def form(data):
    return render_template('post_types/text.html', **data)

def receive(data):
    return {'type':'text', 'content': escape(data.get('content',''))}

def display(data):
    return data['content']

