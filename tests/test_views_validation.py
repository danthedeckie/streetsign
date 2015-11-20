'''
    Check that views return either valid HTML, or JSON, with the expected
    HTTP codes (depending on if we're logged in or not.)
'''
#pylint: disable=import-error, too-many-public-methods, invalid-name

import sys
import os

sys.path.append(os.path.dirname(__file__) + '/..')

import streetsign_server.models as models

from unittest_helpers import StreetSignTestCase

class TestBasicViewValid(StreetSignTestCase):
    ''' test for valid HTML & JSON of the main views. '''

    def test_non_logged_in_pages(self):
        ''' test HTML validity of all non-logged-in pages '''

        self.validate('/')
        self.validate('/index.html')

    def test_not_logged_in_permission_denied(self):
        ''' not logged in, all of these should permission-deny '''

        self.validate('/screens/', code=403)
        self.validate('/screens-edit/0', code=403)
        self.validate('/user_files/', code=403)
        self.validate('/user_files/thing.jpg', code=403)
        self.validate('/users_and_groups', code=403)
        self.validate('/users/0', code=403)
        self.validate('/group/0', code=403)
        self.validate('/aliases', code=403)
        self.validate('/posts/', code=403)
        self.validate('/feeds/', code=403)

    def test_screen_doesnt_change(self):
        ''' javascript in the screen pulls the screen itself down every
            minute or so to check if any screen layout data has changed,
            and if it does, it refreshes the page.  When I (daftly) added
            a server_time attribute to the screen page, it meant it was always
            different, and so always refreshed every minute.'''

        s = models.Screen()
        s.urlname='TestScreen'
        s.save()

        self.validate('/screens/basic/TestScreen')
        a = self.client.get('/screens/basic/TestScreen')
        b = self.client.get('/screens/basic/TestScreen')

        self.assertEqual(a.data, b.data)

    def test_logged_in_valid(self):
        u = models.User(loginname='test', emailaddress='test@test.org')
        u.set_password('123')
        u.save()

        self.login('test', '123')

        with self.ctx():
            self.validate('/screens/')
            self.validate('/screens-edit/0', follow_redirects=True)
            self.validate('/user_files/')
            self.validate('/user_files/thing.jpg')
            self.validate('/users_and_groups')
            self.validate('/users/' + str(u.id))
            self.validate('/group/0', follow_redirects=True)
            self.validate('/aliases', lang='json')
            self.validate('/posts/')
            self.validate('/feeds/')

    def test_admin_logged_in_valid(self):
        u = models.User(loginname='test',
                        emailaddress='test@test.org',
                        is_admin=True)
        u.set_password('123')
        u.save()

        self.login('test', '123')

        with self.ctx():
            self.validate('/screens/')
            self.validate('/user_files/')
            self.validate('/user_files/thing.jpg')
            self.validate('/users_and_groups')
            self.validate('/users/' + str(u.id))
            self.validate('/group/0', follow_redirects=True)
            self.validate('/aliases', lang='json')
            self.validate('/posts/')
            self.validate('/feeds/')


    def test_user_info_not_logged_in(self):
        ''' user info should be private! '''

        self.validate('/users/0', code=403)

        u = models.User(loginname='test', emailaddress='test@test.org')
        u.set_password('123')
        u.save()

        self.validate('/users/' + str(u.id), code=403)

    def test_new_screen_not_logged_in(self):
        ''' only admins can create screens. '''

        m = models.Screen()
        m.urlname = 'Default'
        m.save()

        self.validate('/screens/basic/Default')
        self.validate('/screens-edit/0', code=403) # permision denied

    def test_screen_json(self):
        ''' test screen_json is valid '''
        self.validate('/screens/json/0', lang='json')
