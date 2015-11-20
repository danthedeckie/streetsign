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
'''

----------------------------
streetsign_server.post_types
----------------------------

Main methods for working with multiple post_types.

'''

from os.path import dirname, basename, splitext, isfile, abspath, \
                    join as pathjoin
from importlib import import_module
from glob import glob
import sys
import inspect

PATH = dirname(__file__)

_EDITORS = {}

def path_to_module(path):
    ''' given a path (/var/blah/x.py) return the name of x.py for
        importing (just x) '''

    #return splitext(basename(path))[0]
    return basename(dirname(path))

def my(filename, level=1): #pylint: disable=invalid-name
    ''' given a filename, returns the contents of that file in the *same*
        *directory* as the file which has the 'my' call in it. '''
    # pylint: disable=protected-access
    with open(pathjoin(dirname(abspath(inspect.getfile(sys._getframe(level)))) \
              , filename), 'r') as f:
        return f.read()

def modules():
    ''' a list of all post types modules which can be used/imported '''

    all_list = [path_to_module(p) for p in glob(PATH + '/*/__init__.py')]
    return all_list

def module_dict(name):
    ''' turns a name (string) into a dict ready for use in importing, '''

    return {'id': name, 'name': load(name).__NAME__}

_TYPES = []
def types():
    ''' return a list of dicts of all post types.  '''
    global _TYPES
    if not _TYPES:
        _TYPES = [module_dict(m) for m in modules()]
    return _TYPES

def load(type_name):
    ''' load a module, and return it. (caches in this module) '''

    if type_name in _EDITORS:
        return _EDITORS[type_name]

    #if isfile(PATH + '/' + type_name):
    try:
        e = import_module('streetsign_server.post_types.' +  type_name)
    except ImportError:
        if type_name == 'text':
            raise
        return load('text')
    _EDITORS[type_name] = e
    return e

def receive(posttype, form):
    ''' hand a form object from a request on to the appropriate handler '''

    editor = load(posttype)
    return editor.receive(form)

def renderer_js(posttype):
    ''' return the javascript for rendering a module's data '''

    editor = load(posttype)
    return editor.renderer_js()

def renderers():
    ''' return the javascript for ALL post_types to be rendered. (as a list
        - you still need to combine it as you like... '''

    return [(e, load(e).screen_js()) for e in modules()]
