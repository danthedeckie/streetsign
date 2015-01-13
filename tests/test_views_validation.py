'''
    First file on the noble epic tast of unit testing.
'''

import sys
import os

sys.path.append(os.path.dirname(__file__) + '/..')

import streetsign_server
import streetsign_server.models as models
from streetsign_server.models import Post, Feed

from unittest_helpers import StreetSignTestCase

class TestBasicViewValid(StreetSignTestCase):
    ''' test for valid HTML & JSON of the main views. '''

    def test_non_logged_in_pages(self):
        ''' test HTML validity of all non-logged-in pages '''

        self.validate('/')
        self.validate('/index.html')
        self.validate('/posts/')
        self.validate('/feeds/')

    def test_empty_not_logged_in(self):
        # not logged in, all of these should permission-deny:

        self.validate('/screens/', code=403)
        self.validate('/screens-edit/0', code=403)
        self.validate('/user_files/', code=403)
        self.validate('/user_files/thing.jpg', code=403)
        self.validate('/users', code=403)
        self.validate('/users/0', code=403)
        self.validate('/groups', code=403)
        self.validate('/group/0', code=403)
        self.validate('/aliases', code=403)

    def test_user_info_not_logged_in(self):

        self.validate('/users/0', code=403)

        u = models.User(loginname='test', emailaddress='test@test.org')
        u.set_password('123')
        u.save()

        self.validate('/users/' + str(u.id), code=403)

    def test_new_screen_not_logged_in(self):
        m = models.Screen()
        m.urlname = 'Default'
        m.save()

        self.validate('/screens/basic/Default')
        self.validate('/screens-edit/0', code=403) # permision denied

    def test_screen_json(self):
        ''' test screen_json is valid '''
        self.validate('/screens/json/0', lang='json')
