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
#    ---------------------------------
"""
    streetsign_server.views.utils
    -----------------------------

    No actual views in here, only bits and pieces to make views more
    fun.
"""
from flask import request

class PleaseRedirect(Exception):
    '''
    so redirects can be passed back to views from logic functions.
    >>> def view_blah(...):
            try:
                do_stuff()
            except app.PleaseRedirect as e:
                flash(str(e.msg))
                redirect(e.url)
    '''
    def __init__(self, url='index', msg='Something went wrong'):
        self.msg = msg
        self.url = url

# these are some quick functions for getting sanitized form items,
# later we should probably transition to WTForms, or similar. But these
# will do for now.

def getint(name, default, minimum=0, maximum=999999999):
    """ get an integer from the request.form, capped with min and max,
        and a default.  If its not a valid integer, return the default.  """
    try:
        return min(max(int(request.form.get(name, default)), minimum), maximum)
    except:
        return default

def getbool(name, default):
    """ get a bool from the request.form.  if it's not valid, return the
        default. """
    try:
        return bool(request.form.get(name, default))
    except:
        return default

def getstr(name, default):
    """ get a string from request.form. if it's not there, then return the
        default. """
    return request.form.get(name, default)
