# -*- coding: utf-8 -*-
"""  StreetSign Digital Signage Project
     (C) Copyright 2013 Daniel Fairhead

    StreetSign is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    StreetSign is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with StreetSign.  If not, see <http://www.gnu.org/licenses/>.

    ---------------------------
    Pull data from an RSS feed

"""

__MODULE__ = 'rss'

from flask import render_template_string
import feedparser

from streetsign_server.external_source_types import my

def receive(request):
    ''' get data from the admin, extract the data, and return the object we
        actually need to save. '''
    return { "url": request.form.get('url',''),
        "display_detail": request.form.get('display_detail','')
        }

def form(data):
    ''' the form for editing this type of post '''
    # pylint: disable=star-args
    return render_template_string(my('.form.html'), **data)

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
        example_post = render_template_string(data['display_detail'],
            **first_post)
    except:
        example_post = "No First Post"

    return render_template_string(my('.test.html'), feed=feed,
        example_post=example_post)
