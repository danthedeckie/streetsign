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
"""
---------------------------------
streetsign_server.post_types.html
---------------------------------

HTML / rich text post type.

"""

__NAME__ = 'Rich Text'
__DESC__ = 'HTML / Rich Text Post'

from flask import render_template_string
import re
import bleach

from streetsign_server.post_types import my

def form(data):
    ''' the form for editing this type of post '''
    # pylint: disable=star-args
    return render_template_string(my('form.html'), **data)

def safehtml(text):
    ''' used by 'recieve' to clean html,
        and not allow scripts and other nasties. '''

    return bleach.clean(text, strip=True,
        tags=["div", "span", "b", "i", "u",
              "em", "ul", "li", "ol", "a", "br",
              "code", "blockquote", "strong",
              "small", "big", "img", "table",
              "tr", "td", "th", "thead",
              "tfoot", "h1", "h2", "h3", "h4", "h5", "h6", "p"],
        attributes=['class', 'href', 'alt', 'src', 'style', 'width','height'])

def safecolor(text, default="#fff"):
    ''' check that a color string is actually a html hex-type color... '''
    if not text:
        return default
    try:
        return re.search("#[0-9a-fA-F]+", text).group()
    except AttributeError:
        return default

def receive(data):
    ''' turn the contents posted back to us from the form into
        a dict which can be JSON'd by the system, and dumped as
        text into the database. '''
    #############
    # TODO: sanify color input.

    return {'type': 'html',
            'owntextcolor': data.get('owntextcolor', False),
            'color': safecolor(data.get('color', False)),
            'content': safehtml(data.get('content', ''))}

def display(data):
    ''' return the data ready for the display js to do stuff with. '''
    return data['content']

def screen_js():
    ''' return the js needed to display this content. '''
    return my('screen.js')
