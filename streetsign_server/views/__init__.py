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
#    ---------------------------
'''
    streetsign_server.views
    -----------------------

    brings in all the main views from the other files.

'''
from __future__ import print_function
from flask import render_template, g, Response, url_for

# set up the app
from streetsign_server import app
from streetsign_server.models import Post, Screen, Feed, User, config_var

from streetsign_server.helpers.database import DB

import streetsign_server.views.api

######################################################################
# Basic App stuff:

@app.before_request
def before_the_action():
    ''' load some variables in for template etc to use, and connect the DB '''

    g.site_vars = app.config.get('SITE_VARS')
    DB.init(app.config.get('DATABASE_FILE'))
    DB.connect()

@app.teardown_request
def end_of_request(exception): # pylint: disable=unused-argument
    ''' close the database '''
    DB.close()

@app.route('/')
def index():
    ''' main administration dashboard '''

    return render_template('newdash.html')

