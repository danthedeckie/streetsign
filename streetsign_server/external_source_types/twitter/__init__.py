# -*- coding: utf-8 -*-
#  StreetSign Digital Signage Project
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
    Pull data from an Twitter feed

'''

__NAME__ = 'Twitter importer'

__MODULE__ = 'twitter'

from flask import render_template_string, json
from jinja2 import Template
import bleach
from collections import defaultdict
import tweepy

from streetsign_server.external_source_types import my

DEFAULT_TAGS = "span,b,i,u,em,img"

def receive(request):
    ''' get data from the web interface, extract the data, and return the object we
        actually need to save. '''

    return {"user_id": request.form.get('user_id', ''),
            "show_avatar" : request.form.get('show_avatar', ''),
            "feed_type" : request.form.get('feed_type', 'user_timeline'),

            "api_key": request.form.get('api_key', ''),
            "api_secret": request.form.get('api_secret', ''),
            "user_key": request.form.get('user_key', ''),
            "user_secret": request.form.get('user_secret', ''),

            "current_posts": json.loads(request.form.get('current_posts', '[]')),
            }

def form(data):
    ''' the form for editing this type of post '''
    # pylint: disable=star-args
    return render_template_string(my('form.html'),
                                  default_tags=DEFAULT_TAGS, **data)

TWEET_TEMPLATE = Template(my('tweet.html'))

def test(data):
    ''' we get sent a copy of the data, and should reply with some HTML
        that reassures the user if the url/whatever is correct (preferably
        with some data from the feed) '''

    tweets = get_new(data)

    return render_template_string(my('test.html'), tweets=tweets)

def get_new(data):
    ''' ok, actually go get us some new posts, alright? (return new posts, and
        update data with any hidden fields updated that we need to
        (current_posts, for instance))'''

    auth = tweepy.OAuthHandler(data['api_key'], data['api_secret'])
    auth.set_access_token(data['user_key'], data['user_secret'])

    api = tweepy.API(auth)

    if data['feed_type'] == 'user_timeline':
        feed = api.user_timeline(data['user_id'])
    elif data['feed_type'] == 'retweeted_by_me':
        feed = api.retweeted_by_me()
    else:
        feed = api.home_timeline()

    previous_list = json.loads(data['current_posts'])

    new_posts = []

    #templater = make_templater(data)

    for entry in feed:
        if entry.id not in previous_list:
            new_posts.append({'type': 'html', 'color': None,
                              'content': TWEET_TEMPLATE.render(tweet=entry, **data)})

    data['current_posts'] = [e.id for e in feed]

    return new_posts
