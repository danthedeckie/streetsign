# -*- coding: utf-8 -*-
# StreetSign Digital Signage Project
# (C) Copyright 2013 Daniel Fairhead
#
# StreetSign is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# StreetSign is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with StreetSign.  If not, see <http://www.gnu.org/licenses/>.

"""
---------------------------------
streetsign_server.post_types.text    
---------------------------------

plain text post type.

"""

__NAME__ = 'Plain Text'
__DESC__ = 'Plain text, formatting etc.' \
           ' inherited from the zone it\'s displayed in'

from flask import render_template_string, escape

from streetsign_server.post_types import my

def form(data):
    ''' return the html for editing a text post '''
    # pylint: disable=star-args
    return render_template_string(my('form.html'), **data)

def receive(data):
    ''' recieve the data from the form, and return the dict to save in the
        db '''
    return {'type':'text', 'content': escape(data.get('content',''))}

def display(data):
    ''' return the data to send to the display system (screen) '''
    return data['content']

def screen_js():
    ''' the js needed to display a post correctly. '''
    return my('screen.js')
