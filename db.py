#!.virtualenv/bin/python -i

import app

app.models.create_all()

def make():
    user = app.models.User(loginname='daniel', displayname='Daniel',
                           emailaddress='daniel@somewhere', is_admin=True)
    user.set_password('password')

    user.save()

    group = app.models.Group(name='admins', display='Admins')

