'''
    First file on the noble epic tast of unit testing.
'''

import sys
import os
import tempfile
import unittest
import html5lib
from datetime import datetime
from peewee import SqliteDatabase, create_model_tables
from flask import json, url_for

sys.path.append(os.path.dirname(__file__) + '/..')

import streetsign_server
import streetsign_server.models as models
from streetsign_server.models import Post, Feed

from unittest_helpers import StreetSignTestCase

class TestHTML(StreetSignTestCase):
    ''' test for valid HTML '''

    def test_non_logged_in_pages(self):
        ''' test HTML validity of all non-logged-in pages '''

        self.validate('/')
        self.validate('/index.html')
        self.validate('/posts/')
        self.validate('/feeds/')

    def test_new_screen_not_logged_in(self):
        self.validate('/screens/', code=403)
        self.validate('/user_files/', code=403)
        self.validate('/users', code=403)
        self.validate('/groups', code=403)
        self.validate('/aliases', code=403)

        m = models.Screen()
        m.urlname = 'Default'
        m.save()

        self.validate('/screens/basic/Default')
        self.validate('/screens-edit/0', code=403) # permision denied

class TestJSON(StreetSignTestCase):
    ''' test various JSON views return valid JSON '''

    def validate(self, url):
        ''' test that a url returns valid JSON '''

        request = self.client.get(url)
        json.loads(request.data)

    def test_screen_json(self):
        ''' test screen_json is valid '''
        self.validate('/screens/json/0')
