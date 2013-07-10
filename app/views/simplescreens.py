from flask import render_template, url_for, request, session, redirect, \
                  flash, json, g
import app.user_session as user_session
import app.post_types as post_types
from glob import glob
from os.path import basename
import urllib
from app import app
from app.models import Feed, Post, Screen, \
                       writeable_feeds, by_id


###########################################
#
# Simple Screen Pages.
#

def form_json(name, default):
    ''' make sure form input is valid JSON '''
    try:
        return json.dumps(json.loads(request.form.get(name,
                                                      json.dumps(default))))
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
            backgrounds = [basename(x) for x in \
                           glob(app.config['SITE_VARS']['user_dir']+ '*')]
    
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
