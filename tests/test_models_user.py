'''
    Tests for the User (and Group) peewee ORM models
'''

import sys
import os

sys.path.append(os.path.dirname(__file__) + '/..')

from streetsign_server.models import Feed, User, Group

from unittest_helpers import StreetSignTestCase

#pylint: disable=missing-docstring, invalid-name, too-many-public-methods

class TestUserModel(StreetSignTestCase):

    ''' test the by_id helper function '''

    def test_users_none(self):
        self.assertEqual(User.select().count(), 0)


class TestUserModel_writable_feeds(StreetSignTestCase):

    def test_user_with_no_perms(self):
        u = User(passwordhash='123')
        f = Feed()

        u.save()
        f.save()

        self.assertEqual(u.writeable_feeds(), [])

    def test_user_with_one_feed(self):
        u = User(passwordhash='123')
        f = Feed()

        u.save()
        f.save()

        f.grant('Write', user=u)

        self.assertEqual(u.writeable_feeds(), [f])

    def test_user_with_one_feed_via_group(self):
        u = User(passwordhash='123')
        g = Group(name='group_with_a_name')
        f = Feed()

        u.save()
        f.save()
        g.save()

        g.set_users([u.id])

        f.grant('Write', group=g)

        self.assertEqual(u.writeable_feeds(), [f])

