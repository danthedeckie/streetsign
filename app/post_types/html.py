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
    HTML / rich text post type.

"""

from os.path import abspath, splitext
from flask import render_template_string
import re

def my(ending):
    ''' given '.html', returns (if this is the foobar module)
        the contents of: /where/this/file/is/foodbar.html '''

    with open(splitext(abspath(__file__))[0] + ending,'r') as f:
        return f.read()

def form(data):
    ''' the form for editing this type of post '''
    return render_template_string(my('.form.html'), **data)

def safehtml(text):
    S = re.compile(r'<(.*?)script(.*?)>', re.MULTILINE | re.IGNORECASE)
    W = re.compile(r'\s+')
    return re.sub(W, ' ', re.sub(S, '', text.replace('\n',' '))).replace('<br/> ','<br/>\n')
def receive(data):
    ''' turn the contents posted back to us from the form into
        a dict which can be JSON'd by the system, and dumped as
        text into the database. '''

    return {'type':'html', 'content': safehtml(data.get('content',''))}

def display(data):
    return data['content']

def screen_js():
    return my('.screen.js')
