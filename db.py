#!.virtualenv/bin/python -i

import app

from app.models import *

def make():
    app.models.create_all()
    ############################
    # 3 basic users:
    def user_exists(name):
        return app.models.User.select() \
                              .where(app.models.User.loginname==name).exists()

    if not user_exists('admin'):
        user = app.models.User(loginname='admin', displayname='Admin',
                           emailaddress='admin@localhost', is_admin=True)
        user.set_password('password')

        user.save()

        group = app.models.Group(name='admins', display='Admins').save()

    if not user_exists('jim'):
        user = app.models.User(loginname='jim', displayname='James Hacker MP',
                               emailaddress='jim@no10.gov.uk', is_admin=False)

        user.set_password('password')
        user.save()

    if not user_exists('nobody'):
        user = app.models.User(loginname='nobody', displayname='Nobody',
                               emailaddress='devnull@localhost')

        user.set_password('password')
        user.save()


    #################################
    # default feeds:

    news = app.models.Feed(name='News')

    news.save()

    app.models.Post(type='html', feed=news, author=User(id=1), content='{"content":"First Post"}').save()

    app.models.Screen(urlname='Default').save()
