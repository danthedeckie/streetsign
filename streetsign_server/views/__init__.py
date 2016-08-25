# -*- coding: utf-8 -*-
# StreetSign Digital Signage Project
#     (C) Copyright 2013 Daniel Fairhead
#
#    StreetSign is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    StreetSign is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with StreetSign.  If not, see <http://www.gnu.org/licenses/>.
#
#    ---------------------------
'''
    streetsign_server.views
    -----------------------

    brings in all the main views from the other files.

'''
from __future__ import print_function
from flask import render_template, g, Response, url_for

##########################
# views submodules:
import streetsign_server.views.users_and_auth
import streetsign_server.views.feeds_and_posts
import streetsign_server.views.user_files
import streetsign_server.views.screens
import streetsign_server.user_session as user_session

# set up the app
from streetsign_server import app
from streetsign_server.models import DB, Post, Screen, Feed, User, config_var

######################################################################
# Basic App stuff:

@app.before_request
def before_the_action():
    ''' load some variables in for template etc to use, and connect the DB '''

    g.site_vars = app.config.get('SITE_VARS')
    DB.init(app.config.get('DATABASE_FILE'))
    DB.connect()

@app.teardown_request
def end_of_request(exception): # pylint: disable=unused-argument
    ''' close the database '''
    DB.close()


@app.route('/')
@app.route('/index.html')
def index():
    ''' main front page / dashboard / index. '''
    try:
        user = user_session.get_user()
    except user_session.NotLoggedIn:
        user = User()

    if not user:
        user = User()


    publishable_feeds = user.publishable_feeds()


    posts_to_publish = Post.select()\
                           .where((Post.published == False) &
                                  (Post.feed << publishable_feeds))

    screens = Screen.select()
    aliases = config_var('screens.aliases', [])

    for alias in aliases:
        for screen in screens:
            if screen.urlname == alias['screen_name']:
                alias['screen'] = screen
                break
        else:
            alias['screen'] = None

    return render_template('dashboard.html',
                           aliases=aliases,
                           feeds=Feed.select(),
                           publishable_feeds=publishable_feeds,
                           posts=Post.select().where(Post.author == user)\
                                     .order_by(Post.write_date.desc())\
                                     .limit(15),
                           posts_to_publish=posts_to_publish,
                           screens=screens,
                           user=user)

@app.route('/robots.txt')
def robots_txt():
    ''' block all well-behaved search engines. '''
    return Response('User-agent: *\nDisallow: /', mimetype='text/plain')


# Expected Error Handlers:

@app.errorhandler(user_session.NotLoggedIn)
def not_logged_in(err):
    ''' Not Logged In handler '''
    # TODO: nicer looking.
    print(err)

    return '''<!doctype html>
    <body><h1>StreetSign</h1>
    <h2>Permission Denied</h2>
    You\'re not logged in!
    <a href="{}">Return to StreetSign</a>'''.format(url_for('index')), 403
