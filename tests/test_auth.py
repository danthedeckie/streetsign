'''
    Test Login / Logout
'''

#pylint: disable=missing-docstring,too-many-public-methods

import sys
import os

sys.path.append(os.path.dirname(__file__) + '/..')

import streetsign_server.models as models

from unittest_helpers import StreetSignTestCase

class TestLogin(StreetSignTestCase):
    ''' test for valid HTML & JSON of the main views. '''

    def setUp(self):
        super(TestLogin, self).setUp()

        self.user = models.User(loginname='test',
                                emailaddress='test@test.com',
                                is_admin=False)
        self.user.set_password('123')
        self.user.save()

    def test_login_good_pw_not_admin(self):
        # confirm not logged in:

        self.validate('/users/' + str(self.user.id), code=403)

        # log in:

        resp = self.login('test', '123')

        self.assertEqual(resp.status_code, 200)

        self.validate('/users/' + str(self.user.id))

    def test_login_bad_pw_not_admin(self):
        # confirm not logged in:

        self.validate('/users/' + str(self.user.id), code=403)

        # log in:

        resp = self.login('test', 'BAD')

        assert b'Invalid' in resp.data

        self.validate('/users/' + str(self.user.id), code=403)

    def test_login_good_pw_admin(self):
        self.user.is_admin = True
        self.user.save()

        # confirm not logged in:

        self.validate('/users/' + str(self.user.id), code=403)

        # log in:

        resp = self.login('test', '123')

        self.assertEqual(resp.status_code, 200)

        self.validate('/users/' + str(self.user.id))

    def test_login_bad_pw_admin(self):
        self.user.is_admin = True
        self.user.save()

        # confirm not logged in:

        self.validate('/users/' + str(self.user.id), code=403)

        # log in:

        resp = self.login('test', 'BAD')

        assert b'Invalid' in resp.data

        self.validate('/users/' + str(self.user.id), code=403)

    def test_login_bad_username(self):
        self.validate('/users/' + str(self.user.id), code=403)
        resp = self.login('test_user', 'BAD')

        assert b'Invalid' in resp.data

        self.validate('/users/' + str(self.user.id), code=403)
