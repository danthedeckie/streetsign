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
    Pull data from an RSS feed

'''

__NAME__ = 'RSS/XML/ATOM Feed'

__MODULE__ = 'rss'

from flask import render_template_string, json
from jinja2 import Template
import feedparser
import bleach
from collections import defaultdict

from streetsign_server.external_source_types import my

DEFAULT_TAGS = "span,b,i,u,em,img"

def receive(request):
    ''' get data from the admin, extract the data, and return the object we
        actually need to save. '''

    return {"url": request.form.get('url', ''),
            "display_template": request.form.get('display_template', '{}'),
            "current_posts": json.loads(request.form.get('current_posts', '[]')),
            "allowed_tags": request.form.get('allowed_tags', DEFAULT_TAGS),
            }

def form(data):
    ''' the form for editing this type of post '''
    # pylint: disable=star-args
    return render_template_string(my('form.html'),
                                  default_tags=DEFAULT_TAGS, **data)

def make_templater(data):
    ''' from the info in data, return a html cleaner function. '''

    tags = [x.strip() for x in
            data.get("allowed_tags", DEFAULT_TAGS).split(',')]
    try:
        template = Template(data.get('display_template', '{{title}}'))
    except:
        template = Template(" Bad Template ")

    def templater(item):
        ''' new function for running template... '''
        try:
            return bleach.clean(template.render(**defaultdict(lambda: '', item)),
                                tags=tags,
                                attributes=["class", "href", "alt", "src"],
                                strip=True)
        except:
            return "bad template."

    return templater



def test(data):
    ''' we get sent a copy of the data, and should reply with some HTML
        that reassures the user if the url/whatever is correct (preferably
        with some data from the feed) '''

    try:
        feed = feedparser.parse(data['url'])
    except Exception as e:
        return 'invalid url({})'.format(str(e))

    try:
        first_post = feed.entries[0]
        example_post = make_templater(data)(first_post)
    except Exception as e:
        example_post = str(e)

    return render_template_string(my('test.html'), feed=feed,
        example_post=example_post)

def get_new(data):
    ''' ok, actually go get us some new posts, alright? (return new posts, and
        update data with any hidden fields updated that we need to
        (current_posts, for instance))'''

    feed = feedparser.parse(data['url'])

    previous_list = data['current_posts']

    new_posts = []

    templater = make_templater(data)

    for entry in feed.entries:
        if entry.id not in previous_list:
            new_posts.append({'type': 'html', 'color': None,
                              'content': templater(entry)})

    data['current_posts'] = [e.id for e in feed.entries]

    return new_posts
