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
'''
    streetsign_server.user_session

    factor out the session handling stuff, so that the views don't need to
    worry about it.

'''

from flask import session
from streetsign_server.models import user_login, user_logout, get_logged_in_user

def login(username, password):
    ''' given a username and password, try to log in (via the db),
        create a new session id, and set all required session cookie values.
        Fails with a models password exception if not valid. '''

    user, sessionid = user_login(username, password)
    session['username'] = user.loginname
    session['userid'] = user.id
    # note: this is *potentially* less secure. Always confirm against
    #       real user data before accepting any values:
    session['display_admin_stuff'] = user.is_admin
    session['sessionid'] = sessionid
    session['logged_in'] = True
    return user

class NotLoggedIn(Exception):
    ''' Basic exception for when you MUST be logged in, but aren't. '''
    pass

def get_user():
    ''' if the user's session cookie thinks they're not logged in,
        raise NotLoggedIn.
        if the user thinks they are logged in, confirm against the server that
        they have an active session that we know about, and if not, clear the
        session they think they have. (Protection against session hi-jacking,
        and against changing your session user so something it shouldn't be.
        The encrypted sessions should not allow this anyway, but this is an
        extra precaution, for double paranoia. '''

    if not 'logged_in' in session:
        raise NotLoggedIn('Not logged in!')
    try:
        return get_logged_in_user(session['username'], session['sessionid'])
    except:
        session.pop('username', None)
        session.pop('sessionid', None)
        session.pop('display_admin_stuff', None)
        session.pop('logged_in', None)
        return None

def logged_in():
    ''' is there a 'logged_in' in the user's session cookie? '''

    return 'logged_in' in session

def logout():
    ''' remove our current session from the database session list, and
        clear all relevant session cookie vars. '''

    try:
        user_logout(session['username'], session['sessionid'])
    except:
        pass # somehow the session expired. but we're logging out anyway.
    session.pop('username', None)
    session.pop('sessionid', None)
    session.pop('display_admin_stuff', None)
    session.pop('logged_in', None)

def is_admin():
    ''' check session against db that the current user is an admin.  Doesn't
        raise any exceptions, simply returns False if there is an issue '''

    # convenience method.  Makes certain views a lot shorter.
    try:
        return get_user().is_admin
    except:
        return False

