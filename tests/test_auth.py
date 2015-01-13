'''
    First file on the noble epic tast of unit testing.
'''

import sys
import os

sys.path.append(os.path.dirname(__file__) + '/..')

from flask import jsonify

import streetsign_server
import streetsign_server.models as models
from streetsign_server.views.utils import admin_only, registered_users_only

from unittest_helpers import StreetSignTestCase
from requests import session

class TestLogin(StreetSignTestCase):
    ''' test for valid HTML & JSON of the main views. '''

    def test_login_good_pw_not_admin(self):
        u = models.User(loginname='test', emailaddress='test@test.com', is_admin=False)
        u.set_password('123')
        u.save()

        # confirm not logged in:

        self.validate('/users/' + str(u.id), code=403)

        # log in:

        resp = self.login('test', '123')

        self.assertEqual(resp.status_code, 200)

        self.validate('/users/' + str(u.id))

    def test_login_bad_pw_not_admin(self):
        u = models.User(loginname='test', emailaddress='test@test.com', is_admin=False)
        u.set_password('123')
        u.save()

        # confirm not logged in:

        self.validate('/users/' + str(u.id), code=403)

        # log in:

        resp = self.login('test', 'BAD')

        assert b'Invalid' in resp.data

        self.validate('/users/' + str(u.id), code=403)

    def test_login_good_pw_admin(self):
        u = models.User(loginname='test', emailaddress='test@test.com', is_admin=True)
        u.set_password('123')
        u.save()

        # confirm not logged in:

        self.validate('/users/' + str(u.id), code=403)

        # log in:

        resp = self.login('test', '123')

        self.assertEqual(resp.status_code, 200)

        self.validate('/users/' + str(u.id))

    def test_login_bad_pw_admin(self):
        u = models.User(loginname='test', emailaddress='test@test.com', is_admin=True)
        u.set_password('123')
        u.save()

        # confirm not logged in:

        self.validate('/users/' + str(u.id), code=403)

        # log in:

        resp = self.login('test', 'BAD')

        assert b'Invalid' in resp.data

        self.validate('/users/' + str(u.id), code=403)
