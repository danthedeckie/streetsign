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

    ---------------------------------

    factor out the session handling stuff, so that the views don't need to
    worry about it.

"""

from flask import session
from streetsign_server.models import user_login, user_logout, get_logged_in_user

def login(username, password):
    user, sessionid = user_login(username, password)
    session['username'] = user.loginname
    # note: this is *potentially* less secure. Always confirm against
    #       real user data before accepting any values:
    session['display_admin_stuff'] = user.is_admin
    session['sessionid'] = sessionid
    session['logged_in'] = True
    return user

class NotLoggedIn(Exception):
    pass

def get_user():
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
    return 'logged_in' in session

def logout():
    try:
        user_logout(session['username'], session['sessionid'])
    except:
        pass # somehow the session expired. but we're logging out anyway.
    session.pop('username', None)
    session.pop('sessionid', None)
    session.pop('display_admin_stuff', None)
    session.pop('logged_in', None)

def is_admin():
    # convenience method.  Makes certain views a lot shorter.
    try:
        return get_user().is_admin
    except:
        return False

