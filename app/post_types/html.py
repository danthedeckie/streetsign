from flask import render_template, url_for, json

def form(data, typeid):
    return render_template('post_types/html.html', post_type=typeid)

def receive(data):
    return {'type':'html', 'content': data.get('content','')}

def display(data):
    return data['content']

