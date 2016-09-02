# -*- coding: utf-8 -*-
# StreetSign Digital Signage Project
#     (C) Copyright 2016 Daniel Fairhead
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
    streetsign_server.views.api
    -----------------------

    JSON api (WIP)

'''
from __future__ import print_function

from functools import wraps

from flask import g, Response, url_for, jsonify, request, json

# set up the app
from streetsign_server import app
from streetsign_server.models import Post, Screen, Feed, User, config_var

from streetsign_server.helpers.database import DB

###############
# New API stuff:

def jsonroute(func):
    @wraps(func)
    def wrapped(*vargs, ** kwargs):
        if True:
            return jsonify(func(*vargs, **kwargs))
        else:
            #,except Exception as exp:
            raise exp # TODO Remove for production
            return jsonify({'error': str(exp)}), 501
    return wrapped


@app.route('/api/posts')
@jsonroute
def api_posts():
    if request.method == 'GET':

        posts = Post.select()

        if 'feeds' in request.args:
            posts = posts.where(Post.feed << \
                [int(i) for i in request.args['feeds'].split(',')])

        return {'posts': posts}

@app.route('/api/feeds')
@jsonroute
def api_feeds():
    if request.method == 'GET':

        feeds = Feed.select()

        return {'feeds': feeds}

@app.route('/api/feed/<int:feedid>')
@jsonroute
def api_feed(feedid):
    return Feed.get(Feed.id == int(feedid)).dict_repr()
