# -*- coding: utf-8 -*-

"""  Concertino Digital Signage Project
     (C) Copyright 2013 Daniel Fairhead

    Concertino is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Concertino is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Concertino.  If not, see <http://www.gnu.org/licenses/>.

    -----------------------------------------
    Views for screen output, and editing the screens.

"""



from flask import render_template, url_for, request, session, redirect, \
                  flash, json, g
import app.user_session as user_session
import app.post_types as post_types
from glob import glob
from os.path import basename
import urllib
from datetime import datetime
from app import app
from md5 import md5
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

@app.route('/screens/')
def screens():
    return render_template('screens.html',
        screens=Screen.select())

@app.route('/screens-edit/<screenid>', methods=['GET','POST'])
@app.route('/screens-edit/<int:screenid>', methods=['GET','POST'])
def screenedit(screenid):
    try:
        if int(screenid) == -1:
            flash('New Screen')
            screen = Screen()
        else:
            screen = Screen().get(Screen.id==int(screenid))

        backgrounds = [basename(x) for x in \
                       glob(app.config['SITE_VARS']['user_dir']+ '*')]

    except Screen.DoesNotExist:
        flash('Invalid Screen ID! Screen does NOT exist!')
        return redirect(url_for('index'))

    if request.method == 'POST':
        if not user_session.logged_in():
            flash("You're not logged in!")
            return redirect(url_for('posts'))

        user = user_session.get_user()
        if not user.is_admin:
            flash('Sorry. You are NOT an admin!')
            redirect(url_for('index'))

        if request.form.get('action','update') == 'delete':
            screen.delete_instance()
            flash('deleted')
            return redirect(request.referrer)

        screen.background = request.form.get('background')
        screen.urlname = urllib.quote(request.form.get('urlname'),'')
        screen.settings = request.form.get('settings',{'css':''})
        screen.zones = form_json('zones',{})
        screen.save()
        flash('saved.')

    return render_template('screen_editor.html',
                feeds=Feed.select(),
                backgrounds = backgrounds,
                screen=screen)

@app.route('/screens/<template>/<screenname>')
def screendisplay(template, screenname):
    return render_template('screens/' + template + '.html',
                           screendata=Screen.get(urlname=screenname))

@app.route('/screens/posts_from_feeds/<json_feeds_list>')
def screens_posts_from_feeds(json_feeds_list):
    feeds_list = json.loads(json_feeds_list)

    time_now = datetime.now()

    posts = [p.dict_repr() for p in \
             Post.select().join(Feed)
             .where((Feed.id << feeds_list)
                   &(Post.status == 0)
                   &(Post.active_start < time_now)
                   &(Post.active_end > time_now)
                   &(Post.published)
                   )]
    return json.dumps({'posts':posts})

@app.route('/json/feed/<int:feedid>')
def api_feed(feedid):
    return '{"id":{0}, "posts":[]}'.format(feedid)

@app.route('/screens/json/<int:screenid>/<version>')
def screen_version(screenid, version):
    try:
        screen = Screen.get(id=int(screenid))
    except:
        screen = Screen()

    screenjson = screen.json_all()

    return json.dumps({'screen': screenid, \
                       'md5':  md5(screenjson).hexdigest(), \
                       'screen': json.loads(screenjson)})


@app.route('/screens/post_types.js')
def post_types_js():
    return (render_template('post_types.js',types=post_types.renderers()),
            200,
            {'Content-Type':'application/javascript'})
