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

    ---------------------------

    app/views/__init__.py

    brings in all the main views from the other files.

"""

from flask import render_template, g
##########################
# views submodules:
import app.views.users_and_auth
import app.views.feeds_and_posts
import app.views.user_files
import app.views.screens
import app.user_session as user_session

# set up the app
from app import app
from app.models import DB, Post, Screen, Feed, User

######################################################################
# Basic App stuff:

@app.before_request
def before_the_action():
    ''' load some variables in for template etc to use, and connect the DB '''

    g.site_vars = app.config.get('SITE_VARS')
    DB.connect()

@app.teardown_request
def end_of_request(exception):
    ''' close the database '''
    DB.close()


@app.route('/')
@app.route('/index.html')
def index():
    ''' main front page / dashboard / index. '''
    try:
        user = user_session.get_user()
    except user_session.NotLoggedIn as e:
        user = User()

    # TODO:
    posts_to_publish = Post.select()\
                           .where(Post.published==False)

    return render_template('dashboard.html',
        feeds = Feed.select(),
        posts = Post.select().where(Post.author == user)\
                    .order_by(Post.write_date)\
                    .limit(15),
        posts_to_publish = posts_to_publish,
        screens=Screen.select(),
        user=user)
