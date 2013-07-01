#!.virtualenv/bin/python -i

import app

app.models.create_all()

def make():
    ############################
    # basic admin user.
    if not app.models.User.select().where(app.models.User.loginname=='admin').exists():
        user = app.models.User(loginname='admin', displayname='Admin',
                           emailaddress='admin@localhost', is_admin=True)
        user.set_password('password')

        user.save()

        group = app.models.Group(name='admins', display='Admins').save()

    ############################
    # default post types:

    app.models.PostType(name='text',
                        description='Simple Plain Text. No Formatting.',
                        handler='plaintext').save()


    app.models.PostType(name='html',
                        description='Formattable text, with styles, etc.',
                        handler='html').save()

    app.models.PostType(name='image',
                        description='Single simple image.',
                        handler='image').save()


    #################################
    # default feeds:

    app.models.Feed(name='News').save()
