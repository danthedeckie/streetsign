from flask import render_template, url_for, request, session, redirect, \
                  flash, json, g
import app.user_session as user_session
import app.post_types as post_types
from glob import glob
from os.path import basename, dirname
from importlib import import_module
import urllib
from app import app
from app.models import DB, User, Group, Feed, Post, Screen, \
                       writeable_feeds, by_id

######################################################################
# Basic App stuff:

@app.before_request
def attach_db():

    g.site_vars = app.config.get('SITE_VARS')
    DB.connect()

@app.teardown_request
def detach_db(exception):
    DB.close()


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

@app.route('/feeds/<int:feedid>', methods=['GET','POST'])
def feedpage(feedid):
    try:
        feed = Feed.get(id=feedid)
    except:
        flash('invalid feed id! (' + feedid + ')')
        return redirect(url_for('feedlist'))

        
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
def postlist():
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
        return redirect(url_for('postlist'))

@app.route('/posts/<int:postid>', methods=['GET','POST'])
def postpage(postid):
    if not user_session.logged_in():
        flash("You're not logged in!")
        return redirect(url_for(postlist))

    try:
        post = Post.get(Post.id==postid)
        editor = post_types.load(post.type)
        user = user_session.get_user()

    except Post.DoesNotExist:
        flash('Sorry! Post id:{0} not found!'.format(postid))
        return(redirect(url_for('postlist')))

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


##################################################################

###########################################
#
# Start simple screen pages:

def form_json(name, default):
    ''' make sure form input is valid JSON '''
    try:
        return json.dumps(json.loads(request.form.get(name,json.dumps(default))))
    except:
        return json.dumps(default)

@app.route('/simplescreens/')
def screenslist():
    return render_template('screenslist.html',
        screens=Screen.select())

@app.route('/simplescreens/edit/<int:screenid>', methods=['GET','POST'])
def simplescreenedit(screenid):
    try:
        if screenid == -1:
            screen = Screen()
        else:
            screen = Screen(id=screenid).get()
            backgrounds = [basename(x) for x in glob(app.config['SITE_VARS']['user_dir']+ '*')]
    
    except Screen.DoesNotExist:
        flash('Invalid Screen ID! Screen does NOT exist!')
        return redirect(url_for('index'))

    if request.method == 'POST':
        if not user_session.logged_in():
            flash("You're not logged in!")
            return redirect(url_for(postlist))

        user = user_session.get_user()
        if not user.is_admin:
            flash('Sorry. You are NOT an admin!')
            redirect(url_for('index'))

        screen.background = request.form.get('background')
        screen.urlname = urllib.quote(request.form.get('urlname'),'')
        screen.settings = form_json('settings',{'css':[]})
        screen.zones = form_json('zones',{})
        screen.save()
        flash('saved.')

    return render_template('screen_editor.html',
                feeds=Feed.select(),
                backgrounds = backgrounds,
                screen=screen)

@app.route('/simplescreens/<template>/<screenname>')
def simplescreen(template, screenname):
    return render_template('simplescreens/' + template + '.html',
                           screendata=Screen.get(urlname=screenname))

@app.route('/simplescreens/posts_from_feeds/<json_feeds_list>')
def simplescreens_posts_from_feeds(json_feeds_list):
    feeds_list = json.loads(json_feeds_list)
    posts = [p.dict_repr() for p in 
             Post.select().join(Feed)
             .where((Feed.id << feeds_list)
                   &(Post.active == True))]
    return json.dumps({'posts':posts})

@app.route('/json/feed/<int:feedid>')
def api_feed(feedid):
    return '{"id":{0}, "posts":[]}'.format(feedid)
