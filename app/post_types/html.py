from flask import render_template, url_for, json

def form(data):
    return render_template('post_types/html.html', **data)

def receive(data):
    return {'type':'html', 'content': data.get('content','')}

def display(data):
    return data['content']

