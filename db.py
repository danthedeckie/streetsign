#!.virtualenv/bin/python -i

'''
A set of useful database bits and pieces for StreetSign.
To be merged with run.py into a simple manage.py (django-style) script.

'''
#pylint: disable=wildcard-import, no-member, unused-wildcard-import, unused-import

import streetsign_server
from datetime import datetime

from streetsign_server.models import *

def make():
    ''' make the default first users, etc. '''
    create_all()
    ############################
    # 3 basic users:
    def user_exists(name):
        ''' test if a user exists '''
        return User.select().where(User.loginname == name).exists()

    if not user_exists('admin'):
        user = User(loginname='admin', displayname='Admin',
                           emailaddress='admin@localhost', is_admin=True)
        user.set_password('password')

        user.save()

        group = Group(name='admins', display='Admins').save() # pylint: disable=unused-variable

    if not user_exists('jim'):
        user = User(loginname='jim', displayname='James Hacker MP',
                               emailaddress='jim@no10.gov.uk', is_admin=False)

        user.set_password('password')
        user.save()

    if not user_exists('nobody'):
        user = User(loginname='nobody', displayname='Nobody',
                               emailaddress='devnull@localhost')

        user.set_password('password')
        user.save()


    #################################
    # default feeds:

    news = Feed(name='News')

    news.save()

    Post(type='html',
         feed=news,
         author=User(id=1),
         published=True,
         publish_date=datetime.now(),
         publisher=User(id=1),
         content='{"content":"First Post"}').save()

    Screen(urlname='Default').save()

if __name__ == '__main__':
    print 'welcome to the database shell.'
    print 'type:  make() to make default data'
    print 'or init() to connect to the database for interative work.'
    print 'dir() will show you the available functions and models'
