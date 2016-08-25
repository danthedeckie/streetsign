'''
    Testing posting a new image. WIP
'''

# pylint: disable=too-many-public-methods, missing-docstring, invalid-name

import sys
import os
from os.path import join as pathjoin

sys.path.append(os.path.dirname(__file__) + '/..')

from uuid import uuid4
from flask import url_for

import streetsign_server
from streetsign_server.models import User

#from streetsign_server.views.users_and_auth import *

from unittest_helpers import StreetSignTestCase
from test_views_users_and_auth import BasicUsersTestCase

USERNAME = 'test'
USERPASS = '123'

ADMINNAME = 'admin'
ADMINPASS = '42'

USER_DIR = streetsign_server.config.SITE_VARS['user_dir']

class ImageUploadTestCase(BasicUsersTestCase):
    def setUp(self):
        super(ImageUploadTestCase, self).setUp()

        self.uuid = str(uuid4())
        self.tmp_path = pathjoin('/tmp', self.uuid)
        self._old_path = streetsign_server.config.SITE_VARS['user_dir']
        streetsign_server.config.SITE_VARS['user_dir'] = self.tmp_path

    def tearDown(self, *vargs, **kwargs): # pylint: disable=unused-argument
        streetsign_server.config.SITE_VARS['user_dir'] = self._old_path

class ImageUrlUpload(ImageUploadTestCase):
    ''' Uploading images '''
    def test_non_existant_feed_not_logged_in(self):
        with self.ctx():
            c = self.client.post(url_for('post_new', feed_id=0))
            self.assertEqual(c.status_code, 403)

            c = self.client.post(url_for('post_new', feed_id=0),
                                 follow_redirects=True)
            self.assertEqual(c.status_code, 403)
