'''
    First file on the noble epic tast of unit testing.
'''

import sys
import os
import tempfile
import unittest

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

        request = self.app.get('/posts')
        assert '<span class="post_count">No Posts at all!' in request.data

if __name__ == '__main__':
    unittest.main()
