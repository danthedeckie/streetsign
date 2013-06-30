from flask import render_template, url_for, request
from app import app
from app.models import User, Group, Feed, Post

######################################################################
# Basic App stuff:

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')

##################################################################
# User Management:

@app.route('/users')
def userlist():
    return render_template('users.html', users=User.select())

@app.route('/groups')
def grouplist():
    return render_template('groups.html', groups=Group.select())


####################################################################
# Feeds & Posts:

@app.route('/feeds')
def feedlist():
    return render_template('feeds.html', feeds=Feed.select())

@app.route('/posts')
def postlist():
    return render_template('posts.html', posts=Post.select())
