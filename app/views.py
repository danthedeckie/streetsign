from flask import render_template, url_for, request, session, redirect, \
                  flash, jsonify
import app.user_session as user_session
from importlib import import_module
from app import app
from app.models import User, Group, Feed, Post, PostType, post_type_module

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
        user_session.login(request.form['username'], request.form['password'])
    except:
        flash('Invalid username or password! Sorry!')

    return redirect(url_for(return_to))

@app.route('/logout', methods=['POST'])
def logout():
    return_to = request.form.get('from','index')

    # delete the session from the database:
    try:
        user_session.logout()
    except:
        flash('error logging out. That is odd')

    # return to where we were.
    return redirect(url_for(return_to))

##################################################################
# User Management:

@app.route('/users')
def userlist():
    return render_template('users.html', users=User.select())

@app.route('/users/<int:userid>')
def userpage(userid):
    return render_template('userpage.html', user=User.select(id=userid))

@app.route('/groups')
def grouplist():
    return render_template('groups.html', groups=Group.select())


####################################################################
# Feeds & Posts:

@app.route('/feeds', methods=['GET','POST'])
def feedlist():
    if request.method == 'POST':
        if not user_session.is_admin():
            flash('Only Admins can do this!')
            return redirect(url_for('feedlist'))

        action = request.form.get('action','create')

        if action == 'create':
            if not request.form.get('title','').strip():
                flash("I'm not making you an un-named feed!")
                return redirect(url_for('feedlist'))
            Feed(name=request.form.get('title','blank').strip()).save()

    return render_template('feeds.html', feeds=Feed.select())

@app.route('/feeds/<int:feedid>', methods=['GET','POST','DELETE'])
def feedpage(feedid):
    try:
        feed = Feed.get(id=feedid).get()
    except:
        flash('invalid feed id! (' + feedid + ')')
        return redirect(url_for('feedlist'))

    if request.method == 'GET':
        return render_template('feed.html', feed=feed)
    elif request.method == 'POST':
        action = request.form.get('action','none')

        if action == 'rename':
            feed.name = request.form.get('title', feed.name).strip()
            feed.save()
        elif action == 'delete':
            feed.delete_instance()

        return render_template('feeds.html', feeds=Feed.select())
    elif request.method == 'DELETE':
        # TODO;
        pass

@app.route('/posts')
def postlist():
    return render_template('posts.html', posts=Post.select())

@app.route('/posts/new', methods=['GET','POST'])
def post_new():
    if request.method == 'GET':
        return render_template('postnew.html',
                post_types=PostType.select().dicts())
    else: # POST. new post!
        editor = post_type_module(request.form.get('post_type'))
        return jsonify(editor.receive(request.form))
       

@app.route('/posts/edittype/<int:typeid>')
def postedit_type(typeid):
    editor = post_type_module(typeid)
    return editor.form(request.form, typeid)

########################################################################
# Bits and pieces of generated javascript & json 'clobber'

@app.route('/js/post_types.json')
def post_types_json():
    return jsonify(types=[x for x in PostType.select().dicts()])
