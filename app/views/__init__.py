''' app/views/__init__.py (C) 2013 Daniel Fairhead
                              Part of 'concertino' digital signage project

'''
from flask import render_template, url_for, request, session, redirect, \
                  flash, json, g
##########################
# views submodules:
import app.views.users_and_auth
import app.views.feeds_and_posts
import app.views.user_files
import app.views.screens

# set up the app
from app import app
from app.models import DB

######################################################################
# Basic App stuff:

@app.before_request
def before_the_action():
    ''' load some variables in for template etc to use, and connect the DB '''

    g.site_vars = app.config.get('SITE_VARS')
    DB.connect()

@app.teardown_request
def end_of_request(exception):
    ''' close the database '''
    DB.close()


@app.route('/')
@app.route('/index.html')
def index():
    ''' main front page / dashboard / index. '''
    return render_template('index.html')
