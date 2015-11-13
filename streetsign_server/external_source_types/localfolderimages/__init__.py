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
    Look in a local images folder (on this computer) for pictures, and pull
    them into a feed.

'''

__NAME__ = 'Local Folder (images)'
__MODULE__ = 'localfolderimages'

from flask import render_template_string, json
from os.path import join as pathjoin, isdir, isfile, exists, basename, dirname
from glob import glob

from streetsign_server.external_source_types import my
from streetsign_server.post_types.image import allow_filetype

DEFAULT_TAGS = "span,b,i,u,em,img"

def receive(request):
    ''' get data from the admin, extract the data, and return the object we
        actually need to save. '''

    return {"path": request.form.get('path', ''),
            "display_template": request.form.get('display_template', '{}'),
            "current_posts": json.loads(request.form.get('current_posts', '[]')),
            "allowed_tags": request.form.get('allowed_tags', DEFAULT_TAGS),
            }

def form(data):
    ''' the form for editing this type of post '''
    # pylint: disable=star-args
    return render_template_string(my('form.html'),
                                  default_tags=DEFAULT_TAGS, **data)

def test(data):
    ''' we get sent a copy of the data, and should reply with some HTML
        that reassures the user if the path/whatever is correct (preferably
        with some data from the feed) '''
    if exists(data['path']) and isdir(data['path']):
        files = glob(pathjoin(data['path'], '*'))

        return ('<br/>'.join([f for f in files if allow_filetype(f)])
               + '<hr/><i>Not uploading:<br/>' 
               + '<br/>'.join([f for f in files if not allow_filetype(f)]))
    else:
        return '...'


def get_new(data):
    ''' ok, actually go get us some new posts, alright? (return new posts, and
        update data with any hidden fields updated that we need to
        (current_posts, for instance))'''

    current_files = glob(pathjoin(data['path'], '*'))

    current_files = [f for f in current_files if allow_filetype(f)]

    previous_list = data['current_posts']

    new_posts = []

    for filename in current_files:
        if basename(filename) not in previous_list:
            new_posts.append({'type': 'image', 'url': 'file://' + filename})

    data['current_posts'] = [basename(f) for f in current_files]

    return new_posts
