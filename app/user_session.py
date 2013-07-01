'''
    factor out the session handling stuff, so that the views don't need to
    worry about it.
'''
from flask import session
from app.models import user_login, user_logout, get_logged_in_user

def login(username, password):
    user, sessionid = user_login(username, password)
    session['username'] = user.loginname
    session['sessionid'] = sessionid
    session['logged_in'] = True
    return user

class NotLoggedIn(Exception):
    pass

def get_user():
    if not 'logged_in' in session:
        raise NotLoggedIn('Not logged in!')
    return get_logged_in_user(session['username'], session['sessionid'])

def logged_in():
    return 'logged_in' in session

def logout():
    try:
        user_logout(session['username'], session['sessionid'])
    except:
        pass # somehow the session expired. but we're logging out anyway.
    session.pop('username', None)
    session.pop('sessionid', None)
    session.pop('logged_in', None)

def is_admin():
    # convenience method.  Makes certain views a lot shorter.
    try:
        return get_user().is_admin
    except:
        return False

