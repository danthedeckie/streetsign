'''
    First file on the noble epic tast of unit testing.
'''

import sys
import os
import tempfile
import unittest
import html5lib

sys.path.append(os.path.dirname(__file__) + '/..')

import streetsign_server

# pylint: disable=too-many-public-methods

class StreetSignTestCase(unittest.TestCase):
    ''' Base Class, initialises and tears down a streetsign_server context. '''

    def setUp(self):
        ''' initialise temporary new database. '''

        self.db_fd, streetsign_server.app.config['DATABASE_FILE'] = \
            tempfile.mkstemp()

        streetsign_server.app.config['TESTING'] = True
        self.app = streetsign_server.app.test_client()
        streetsign_server.models.create_all()

    def tearDown(self):
        ''' delete temporary database '''

        os.close(self.db_fd)
        os.unlink(streetsign_server.app.config['DATABASE_FILE'])

class TestSetup(StreetSignTestCase):
    ''' First basic sanity checks '''

    def test_empty_db(self):
        ''' test that with the new database, there are no posts. '''

        request = self.app.get('/')
        assert 'Dashboard' in request.data # it is the front page
        assert 'Login' in request.data # not logged in

        request = self.app.get('/posts/')
        print request.data
        assert '<span class="post_count">No Posts at all!' in request.data

class TestHTML(StreetSignTestCase):
    ''' test for valid HTML '''

    def validate(self, url):
        ''' test that a URL is actually HTML5 compliant '''

        request = self.app.get(url)
        parser = html5lib.HTMLParser(strict=True)
        doc = parser.parse(request.data)

    def test_non_logged_in_pages(self):
        ''' test HTML validity of all non-logged-in pages '''

        self.validate('/')
        self.validate('/posts/')

if __name__ == '__main__':
    unittest.main()
