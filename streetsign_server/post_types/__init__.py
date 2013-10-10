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

    -------------------------------------

    Main methods for working with multiple post_types.

"""



from os.path import dirname, basename, splitext, isfile
from importlib import import_module
from glob import glob

PATH = dirname(__file__)

_editors = {}

def path_to_module(path):
    ''' given a path (/var/blah/x.py) return the name of x.py for
        importing (just x) '''

    return splitext(basename(path))[0]

def modules():
    ''' a list of all post types modules which can be used/imported '''

    all_list = [ path_to_module(p) for p in glob(PATH + '/*.py') ]
    all_list.remove('__init__')
    return all_list

def module_dict(name):
    ''' turns a name (string) into a dict ready for use in importing, '''

    # a bit of a stupid function for now.  I'm sure it'll be more useful later.

    return {'id': name, 'name': name}

def types():
    ''' return a list of dicts of all post types.
        TODO: find a way to cache this. '''

    return [ module_dict(m) for m in modules() ]

def load(type_name):
    ''' load a module, and return it. (caches in this module) '''

    if type_name in _editors:
        return _editors[type_name]

    #if isfile(PATH + '/' + type_name):
    e = import_module( 'streetsign_server.post_types.' +  type_name )
    _editors[type_name] = e
    return(e)

def receive(posttype, form):
    ''' hand a form object from a request on to the appropriate handler '''

    editor = load(posttype)
    return(editor.receive(form))

def renderer_js(posttype):
    ''' return the javascript for rendering a module's data '''

    editor = load(posttype)
    return(editor.renderer_js())

def renderers():
    ''' return the javascript for ALL post_types to be rendered. (as a list
        - you still need to combine it as you like... '''

    return [(e, load(e).screen_js()) for e in modules()]
