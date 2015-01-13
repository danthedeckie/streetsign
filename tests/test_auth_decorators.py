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

class TestDecorators(StreetSignTestCase):
    ''' test for valid HTML & JSON of the main views. '''

    def test_new_only_admins_get_only(self):

        @streetsign_server.app.route('/tests/admin_only_get')
        @admin_only('GET')
        def admin_only_get():
            return jsonify({'test':'success'})

        # without logging in:

        self.validate('/tests/admin_only_get', code=403)

        # create a user:

        u = models.User(loginname='test', emailaddress='test@test.com', is_admin=False)
        u.set_password('123')
        u.save()

        # log in:

        a = self.login('test', '123')

        # should still fail:

        self.validate('/tests/admin_only_get', code=403)

        # now upgrade to admin level:

        u.is_admin = True
        u.save()

        self.validate('/tests/admin_only_get', lang='json')


    def test_admin_post_only_must_be_logged_in_to_get(self):
        route = '/tests/admin_only_post_all_get'

        @streetsign_server.app.route(route, methods=['GET','POST'])
        @admin_only('POST')
        @registered_users_only('GET')
        def admin_only_post_all_get():
            return jsonify({'test':'success'})

        # without logging in:

        self.validate(route, code=403)
        self.validate(route, req='POST', code=403)

        # create a user:

        u = models.User(loginname='test', emailaddress='test@test.com', is_admin=False)
        u.set_password('123')
        u.save()

        # log in:

        a = self.login('test', '123')

        self.validate(route, lang='json')
        self.validate(route, req='POST', code=403)

        # now upgrade to admin level:

        u.is_admin = True
        u.save()

        self.validate(route, lang='json')
        self.validate(route, req='POST', lang='json')

    def test_new_route(self):
        @streetsign_server.app.route('/tests/blah')
        def blah():
            return jsonify({'test':'success'})

        self.validate('/tests/blah', lang='json')
