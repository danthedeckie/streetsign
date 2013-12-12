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
