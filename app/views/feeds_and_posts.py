from flask import render_template, url_for, request, session, redirect, \
                  flash, json, g
import app.user_session as user_session
import app.post_types as post_types
from werkzeug import secure_filename
from app import app
from app.models import DB, User, Group, Feed, Post, Screen, \
                       writeable_feeds, by_id

####################################################################
# Feeds & Posts:

@app.route('/feeds', methods=['GET','POST'])
def feeds():
    if request.method == 'POST':
        if not user_session.is_admin():
            flash('Only Admins can do this!')
            return redirect(url_for('feeds'))

        action = request.form.get('action','create')

        if action == 'create':
            if not request.form.get('title','').strip():
                flash("I'm not making you an un-named feed!")
                return redirect(url_for('feeds'))
            Feed(name=request.form.get('title','blank').strip()).save()

    return render_template('feeds.html', feeds=Feed.select())

@app.route('/feeds/<int:feedid>', methods=['GET','POST'])
def feedpage(feedid):
    try:
        feed = Feed.get(id=feedid)
    except:
        flash('invalid feed id! (' + feedid + ')')
        return redirect(url_for('feeds'))

        
    if request.method == 'POST':
        action = request.form.get('action','none')

        if action == 'edit':
            feed.name = request.form.get('title', feed.name).strip()
            inlist = request.form.getlist

            feed.set_authors(by_id(User, inlist('authors')))
            feed.set_publishers(by_id(User, inlist('publishers')))
            feed.set_author_groups(by_id(Group, inlist('author_groups')))
            feed.set_publisher_groups(by_id(Group, inlist('publisher_groups')))

            feed.save()
            flash('Saved')
        elif action == 'delete':
            feed.delete_instance()

    return render_template('feed.html',
                     feed=feed,
                     allusers=User.select(),
                     allgroups=Group.select()
                )



##########################################
# Posts:


@app.route('/posts')
def posts():
    return render_template('posts.html', posts=Post.select())

@app.route('/posts/new', methods=['GET','POST'])
def post_new():
    if not user_session.logged_in():
        flash("You're not logged in!")
        return redirect(url_for('index'))

    if request.method == 'GET':
        feeds = []
        if 'initial_feed' in request.args:
            feed = int(request.args.get('initial_feed'))
        else:
            feed = 0
        return render_template('postnew.html',
                initial_feed=feed,
                post_types=post_types.types())
    else: # POST. new post!
        post_type = request.form.get('post_type')

        u = user_session.get_user()
        p = Post(type=post_type, author=u)

        try:
            f = Feed(id=request.form.get('post_feed'))
            if f.user_can_write(u):
                p.feed = f
        except Feed.DoesNotExist:
            flash('Invalid Feed ID!')

        p.content=json.dumps(post_types.receive(post_type, request.form))

        p.save()
        return redirect(url_for('posts'))

@app.route('/posts/<int:postid>', methods=['GET','POST'])
def postpage(postid):
    if not user_session.logged_in():
        flash("You're not logged in!")
        return redirect(url_for(posts))

    try:
        post = Post.get(Post.id==postid)
        editor = post_types.load(post.type)
        user = user_session.get_user()

    except Post.DoesNotExist:
        flash('Sorry! Post id:{0} not found!'.format(postid))
        return(redirect(url_for('posts')))

    if request.method == 'POST':
        if not post.feed and 'feedid' in request.form:
            # new feed.
            feed = Feed(id = request.form.get(feedid))
            if feed.user_can_write(user):
                post.feed = feed
                flash('Posted to {0}'.format(feed.name))
            else:
                # This shouldn't happen very often - so don't worry about
                # losing post data.  If it's an issue, refactor so it's stored
                # but not written to the feed...
                flash("Sorry, you don't have permission to write to {0}"
                      .format(feed.name))
                return redirect(url_for('index'))

        # if we don't have write permission, then this isn't our post!
        if not post.feed.user_can_write(user):
            flash("Sorry, this post is in feed '{0}', which"
                  " you don't have permission to post to."
                  " Edit cancelled.".format(post.feed.name))
            return redirect(url_for('postpage', postid=postid))

        # if this post is already published, be careful about editing it!
        if post.published and not post.feed.user_can_publish(user):
            flash('Sorry, this post is published, and you do not have'
                  'permission to edit published posts in "{0}".'.format(f.name))
            return redirect(url_for('postpage', postid=postid))


        # finally get around to editing the content of the post...
        try:
            content=json.dumps(editor.receive(request.form))
            post.content = content
            post.save()
            flash('Updated.')
        except:
            flash('invalid content for this data type!')

    # TODO: figure out how to do post display times, etc...

    return render_template('post_editor.html',
                            post = post,
                            post_type = post.type,
                            feedlist = writeable_feeds(user),
                            form_content = editor.form(json.loads(post.content)))

@app.route('/posts/edittype/<typeid>')
def postedit_type(typeid):
    ''' returns an editor page, of type typeid '''
    editor = post_types.load(typeid)
    user = user_session.get_user()

    return render_template('post_editor_loaded.html',
                           post_type = typeid,
                           initial_feed=int(request.args.get('initial_feed')),
                           feedlist = writeable_feeds(user),
                           form_content = editor.form(request.form))



