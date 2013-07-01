from flask import render_template, url_for, request, session, redirect, flash
from app import app
from app.models import User, Group, Feed, Post, user_login

######################################################################
# Basic App stuff:

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    # TODO: is using the request.endpoint the best way to do this?
    #       would it be better to use an absolute URL?  I dunno if this
    #       is better against XSS?

    return_to = request.form.get('from','index')
    try:
        user = user_login(request.form['username'], request.form['password'])
        session['username'] = request.form['username']
        session['logged_in'] = True
    except:
        flash('Invalid username or password! Sorry!')

    return redirect(url_for(return_to))

@app.route('/logout', methods=['POST'])
def logout():
    return_to = request.form.get('from','index')
    session.pop('username', None)
    session.pop('logged_in', None)
    return redirect(url_for(return_to))

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
