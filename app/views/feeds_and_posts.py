from flask import render_template, url_for, request, session, redirect, \
                  flash, json, g
import app.user_session as user_session
import app.post_types as post_types
from werkzeug import secure_filename
from datetime import datetime
from app.views.utils import PleaseRedirect

from app.logic.feeds_and_posts import try_to_set_feed, \
                                      if_i_cant_write_then_i_quit, \
                                      can_user_write_and_publish, \
                                      post_form_intake

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
        user = user_session.get_user()
    except:
        flash('invalid feed id! (' + feedid + ')')
        return redirect(url_for('feeds'))

    if request.method == 'POST':
        if not user_session.logged_in():
            flash("You're not logged in!")
            return redirect(url_for('feeds'))

        if not user.is_admin:
            flash('Sorry! Only Admins can change these details.')
            return redirect(request.referrer)

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
            flash('Deleted')
            return redirect(url_for('feeds'))

    return render_template('feed.html',
                     feed=feed,
                     user=user,
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

    user = user_session.get_user()

    if request.method == 'GET':
        # send a blank form for the user:

        feed = int(request.args.get('initial_feed',1))
        return render_template('postnew.html',
                current_feed=feed,
                post=Post(),
                feedlist = writeable_feeds(user),
                can_write = True,
                post_types=post_types.types())

    else: # POST. new post!
        post_type = request.form.get('post_type')
        editor = post_types.load(post_type)

        post = Post(type=post_type, author=user)

        try:
            post.feed = try_to_set_feed(post, request.form, user)

            if_i_cant_write_then_i_quit(post, user)

            post_form_intake(post, request.form, editor)

        except PleaseRedirect as e:
            flash (e.msg)
            redirect(e.url if e.url else request.url)

        post.save()
        flash('Saved!')

        return redirect(request.referrer) #url_for('posts'))

@app.route('/posts/<int:postid>', methods=['GET','POST'])
def postpage(postid):
    if not user_session.logged_in():
        flash("You're not logged in!")
        return redirect(url_for('posts'))

    try:
        post = Post.get(Post.id==postid)
        editor = post_types.load(post.type)
        user = user_session.get_user()

    except Post.DoesNotExist:
        flash('Sorry! Post id:{0} not found!'.format(postid))
        return(redirect(url_for('posts')))

    if request.method == 'POST':
        try:
            # if the user is allowed to set the feed to what they've
            # requested, then do it.

            post.feed = try_to_set_feed(post, request.form, user)

            # check for write permission, and if the post is
            # already published, publish permission.

            if_i_cant_write_then_i_quit(post, user)

        except PleaseRedirect as e:
            flash(e.msg)
            redirect(e.url)

        # if it's a publish or delete request, handle that instead:
        DO = request.form.get('action','edit')
        if DO == 'delete':
            post.delete_instance()
            flash('Deleted')
            return redirect(request.referrer)
        elif DO == 'publish':
            if post.feed.user_can_publish(user):
                post.published = True
                post.publisher = user
                post.publish_date = datetime.now()
                post.save()
                flash ('Published')
            else:
                flash ('Sorry, You do NOT have publish' \
                       ' permissions on this feed.')
            return redirect(request.referrer)
        elif DO == 'unpublish':
            if post.feed.user_can_publish(user):
                post.published = False
                post.publisher = None
                post.publish_date = None
                post.save()
                flash ('Unpublished!')
            else:
                flash ('Sorry, you do NOT have permission' \
                       ' to unpublish on this feed.')
            return redirect(request.referrer)

        # finally get around to editing the content of the post...
        try:
            post_form_intake(post, request.form, editor)

            post.save()
            flash('Updated.')
        except:
            flash('invalid content for this data type!')

    # Should we bother displaying 'Post' button, and editable controls
    # if the user can't write to this post anyway?

    can_write, can_publish = can_user_write_and_publish(user, post)

    return render_template('post_editor.html',
                            post = post,
                            post_type = post.type,
                            current_feed = post.feed.id,
                            feedlist = writeable_feeds(user),
                            can_write = can_write,
                            form_content = editor.form(json.loads(post.content)))

@app.route('/posts/edittype/<typeid>')
def postedit_type(typeid):
    ''' returns an editor page, of type typeid '''
    editor = post_types.load(typeid)
    user = user_session.get_user()

    return render_template('post_type_container.html',
                           post_type = typeid,
                           form_content = editor.form(request.form))



