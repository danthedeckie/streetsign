# -*- coding: utf-8 -*-
#  StreetSign Digital Signage Project
#     (C) Copyright 2014 Daniel Fairhead
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
import tweepy
from urllib import quote
import re

from streetsign_server.external_source_types import my

DEFAULT_TAGS = "span,b,i,u,em,img"

HASHTAGS = re.compile(r'#(\w*)')
ATUSER = re.compile(r'@(\w*)')
URL = re.compile(r'[^"](http[s]?://[^ ]*)')

def twitterify(text, cleanup=None):
    ''' replace plain tweet with HTMLified tweet (hashtags, usernames, links) '''
    # pylint: disable=line-too-long, bad-continuation,bad-whitespace

    url_url = r' <a target="_new" href="\1">\1</a> '
    tag_url = r' <a target="_new" href="https://twitter.com/hashtag/\1">#\1</a> '
    user_url = r' <a target="_new" href="https://twitter.com/\1">@\1</a> '

    if cleanup == 'strip_tags_and_urls':
        tag_url = r''
        url_url = r''

    elif cleanup == 'pictures_only':
        return ''

    return re.sub(HASHTAGS, tag_url,
                  re.sub(ATUSER, user_url,
                         re.sub(URL, url_url, text)))

def receive(request):
    ''' get data from the web interface, extract the data, and return the object we
        actually need to save. '''

    try:
        current_posts = json.loads(request.form.get('current_posts', '[]'))
    except TypeError:
        print 'current_posts', request.form.get('current_posts', '[]')

    return {"query": request.form.get('query', ''),

            "show_user": request.form.get('show_user', ''),
            "feed_type": request.form.get('feed_type', 'user_timeline'),
            "display_options": request.form.get('display_options', 'full_everything'),
            "filter_type": request.form.get('filter_type', 'full_everything'),

            "api_key": request.form.get('api_key', ''),
            "api_secret": request.form.get('api_secret', ''),
            "user_key": request.form.get('user_key', ''),
            "user_secret": request.form.get('user_secret', ''),

            "current_posts": current_posts,
            } #pylint: disable=bad-continuation

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

    data = data.to_dict()
    data['current_posts'] = []

    try:
        tweets = get_new(data)
    except Exception as e: #pylint: disable=broad-except
        return '<h1>Invalid settings</h1><pre>' + str(e) + '</pre>'
    return render_template_string(my('test.html'), tweets=tweets)

def get_new(data):
    ''' ok, actually go get us some new posts, alright? (return new posts, and
        update data with any hidden fields updated that we need to
        (current_posts, for instance))'''

    auth = tweepy.OAuthHandler(data['api_key'], data['api_secret'])
    auth.set_access_token(data['user_key'], data['user_secret'])

    api = tweepy.API(auth)

    if data['feed_type'] == 'user_timeline':
        feed = api.user_timeline(screen_name=data['query'])
    elif data['feed_type'] == 'retweeted_by_me':
        feed = api.retweets_of_me()
    elif data['feed_type'] == 'home_timeline':
        feed = api.home_timeline()
    elif data['feed_type'] == 'mentions':
        feed = api.mentions_timeline()
    elif data['feed_type'] == 'search':
        feed = api.search(q=quote(data['query']))
    else:
        feed = api.home_timeline()

    # confusing... TODO: fix why we need this
    previous_list = data.get('current_posts', '[]')
    if type(previous_list) != list:
        previous_list = json.loads(previous_list)

    new_posts = []

    for entry in feed:
        entry.text = twitterify(entry.text, data['display_options'])

        if entry.id not in previous_list:
            try:
                photo_count = len([e for e in entry.entities['media']
                                   if e['type']=='photo'])
            except:
                photo_count = 0

            if data['filter_type'] == 'pictures_only' and not photo_count:
                continue
            elif data['filter_type'] == 'text_only' and photo_count:
                continue

            new_posts.append({'type': 'html', 'color': None,
                              'content': TWEET_TEMPLATE.render(tweet=entry, **data)})

    data['current_posts'] = [e.id for e in feed]

    return new_posts
