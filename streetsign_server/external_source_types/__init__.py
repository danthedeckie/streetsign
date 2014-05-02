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

    Main methods for working with multiple external source types.

    Yes, this is very similar to post_types.  If you feel like combining
    bits and making it more general, go for it.

"""

from os.path import dirname, basename, splitext, isfile, abspath, join as pathjoin
from importlib import import_module
from glob import glob
import sys
import inspect

PATH = dirname(__file__)

_EDITORS = {}

def path_to_module(path):
    ''' given a path (/var/blah/x/__init__.py) return the name of x for
        importing (just x) '''
    return basename(dirname(path))

def my(filename, level=1):  # pylint: disable=invalid-name
    ''' if this function is called from /x/y/z/blah.py,
        with filename='potato.html', it will return the contents of
        /x/y/z/potato.html. '''
    # pylint: disable=protected-access
    pathname = dirname(abspath(inspect.getfile(sys._getframe(level))))
    with open(pathjoin(pathname, filename), 'r') as f:
        return f.read()

def modules():
    ''' a list of all post types modules which can be used/imported '''

    all_list = [path_to_module(p) for p in glob(PATH + '/*/__init__.py')]
    return all_list

def module_dict(name):
    ''' turns a name (string) into a dict ready for use in importing, '''

    # a bit of a stupid function for now.  I'm sure it'll be more useful later.

    return {'id': name, 'name': load(name).__NAME__}

_TYPES = []
def types():
    ''' return a list of dicts of all post types. '''
    global _TYPES # pylint: disable=global-statement

    if _TYPES:
        return _TYPES
    else:
        _TYPES = [module_dict(m) for m in modules()]
        return _TYPES

def load(type_name):
    ''' load a module, and return it. (caches in this module) '''

    if type_name in _EDITORS:
        return _EDITORS[type_name]

    #if isfile(PATH + '/' + type_name):
    e = import_module('streetsign_server.external_source_types.' + type_name)
    _EDITORS[type_name] = e
    return e

def receive(posttype, form):
    ''' hand a form object from a request on to the appropriate handler '''

    editor = load(posttype)
    return editor.receive(form)
