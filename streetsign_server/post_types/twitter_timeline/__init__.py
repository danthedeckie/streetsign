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

Embedded twitter timeline widget.

"""

__NAME__ = 'Embed a twitter timeline widget'
__DESC__ = 'Embed a twitter timeline widget as a post.'

from flask import render_template_string

from streetsign_server.post_types import my

def form(data):
    ''' the form for editing this type of post '''
    # pylint: disable=star-args
    return render_template_string(my('form.html'),
                                  renderer=my('screen.js'), **data)

def receive(data):
    ''' turn the contents posted back to us from the form into
        a dict which can be JSON'd by the system, and dumped as
        text into the database. '''

    return {'type': 'twitter_timeline',
            'content': data.get('query', ''),
            'query': data.get('query', '')}

def display(data):
    ''' return the data ready for the display js to do stuff with. '''
    return data['query']

def screen_js():
    ''' return the js needed to display this content. '''
    return my('screen.js')
