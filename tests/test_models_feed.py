'''
    Tests for the User (and Group) peewee ORM models
'''

import sys
import os

sys.path.append(os.path.dirname(__file__) + '/..')

from streetsign_server.models import Post, Feed, User, Group

from unittest_helpers import StreetSignTestCase

#pylint: disable=too-many-public-methods, missing-docstring, too-few-public-methods

class TestFeedModel(StreetSignTestCase):

    ''' test the by_id helper function '''

    def test_users_none(self):
        self.assertEqual(Feed.select().count(), 0)

    def test_repr(self):
        f = Feed(name='123')
        self.assertEqual(str(f), '<Feed:123>')

    def test_post_count_empty(self):
        f = Feed(name='123')
        f.save()

        self.assertEqual(f.post_count(), 0)
        self.assertEqual(f.post_count(published=True), 0)
        self.assertEqual(f.post_count(expired=True), 0)
        self.assertEqual(f.post_count(published=True, expired=True), 0)

    def test_no_users(self):
        f = Feed(name='123')
        f.save()

        self.assertEqual(f.authors(), [])
        self.assertEqual(f.publishers(), [])
        self.assertEqual(f.author_groups(), [])
        self.assertEqual(f.publisher_groups(), [])

    def test_one_user_read_only(self):
        f = Feed(name='123')
        f.save()

        u = User(passwordhash='123')
        u.save()

        f.grant('Read', user=u)

        self.assertEqual(f.authors(), [])
        self.assertEqual(f.publishers(), [])
        self.assertEqual(f.author_groups(), [])
        self.assertEqual(f.publisher_groups(), [])

        self.assertFalse(f.user_can_write(u))
        self.assertFalse(f.user_can_publish(u))

    def test_one_user_write_only(self):
        f = Feed(name='123')
        f.save()

        u = User(passwordhash='123')
        u.save()

        f.grant('Write', user=u)

        self.assertEqual(f.authors(), [u])
        self.assertEqual(f.publishers(), [])
        self.assertEqual(f.author_groups(), [])
        self.assertEqual(f.publisher_groups(), [])

        self.assertTrue(f.user_can_write(u))
        self.assertFalse(f.user_can_publish(u))

    def test_one_user_publish(self):
        f = Feed(name='123')
        f.save()

        u = User(passwordhash='123')
        u.save()

        f.grant('Publish', user=u)

        self.assertEqual(f.authors(), [])
        self.assertEqual(f.publishers(), [u])
        self.assertEqual(f.author_groups(), [])
        self.assertEqual(f.publisher_groups(), [])

        self.assertFalse(f.user_can_write(u))
        self.assertTrue(f.user_can_publish(u))

    def test_one_user_write_and_publish(self):
        f = Feed(name='123')
        f.save()

        u = User(passwordhash='123')
        u.save()

        f.grant('Write', user=u)
        f.grant('Publish', user=u)

        self.assertEqual(f.authors(), [u])
        self.assertEqual(f.publishers(), [u])
        self.assertEqual(f.author_groups(), [])
        self.assertEqual(f.publisher_groups(), [])

        self.assertTrue(f.user_can_write(u))
        self.assertTrue(f.user_can_publish(u))


    def test_one_user_group_read_only(self):
        f = Feed(name='123')
        f.save()

        u = User(passwordhash='123')
        u.save()

        g = Group(name='usergroup')
        g.set_users([u.id])
        g.save()

        self.assertEqual(f.authors(), [])
        self.assertEqual(f.publishers(), [])
        self.assertEqual(f.author_groups(), [])
        self.assertEqual(f.publisher_groups(), [])

        self.assertFalse(f.user_can_write(u))
        self.assertFalse(f.user_can_publish(u))

        f.grant('Read', group=g)

        self.assertEqual(f.authors(), [])
        self.assertEqual(f.publishers(), [])
        self.assertEqual(f.author_groups(), [])
        self.assertEqual(f.publisher_groups(), [])

        self.assertFalse(f.user_can_write(u))
        self.assertFalse(f.user_can_publish(u))

    def test_one_user_group_write_only(self):
        f = Feed(name='123')
        f.save()

        u = User(passwordhash='123')
        u.save()

        g = Group(name='usergroup')
        g.save()
        g.set_users([u.id])

        self.assertEqual(f.authors(), [])
        self.assertEqual(f.publishers(), [])
        self.assertEqual(f.author_groups(), [])
        self.assertEqual(f.publisher_groups(), [])

        self.assertFalse(f.user_can_write(u))
        self.assertFalse(f.user_can_publish(u))

        f.grant('Write', group=g)

        self.assertEqual(f.authors(), [])
        self.assertEqual(f.publishers(), [])
        self.assertEqual(f.author_groups(), [g])
        self.assertEqual(f.publisher_groups(), [])

        self.assertTrue(f.user_can_write(u))
        self.assertFalse(f.user_can_publish(u))

    def test_one_user_group_publish_only(self):
        f = Feed(name='123')
        f.save()

        u = User(passwordhash='123')
        u.save()

        g = Group(name='usergroup')
        g.save()
        g.set_users([u.id])

        self.assertEqual(f.authors(), [])
        self.assertEqual(f.publishers(), [])
        self.assertEqual(f.author_groups(), [])
        self.assertEqual(f.publisher_groups(), [])

        self.assertFalse(f.user_can_write(u))
        self.assertFalse(f.user_can_publish(u))

        f.grant('Publish', group=g)

        f = Feed.get(id=f.id)

        self.assertEqual(f.authors(), [])
        self.assertEqual(f.publishers(), [])
        self.assertEqual(f.author_groups(), [])
        self.assertEqual(f.publisher_groups(), [g])

        self.assertFalse(f.user_can_write(u))
        self.assertTrue(f.user_can_publish(u))

    def test_one_user_group_write_and_publish(self):
        f = Feed(name='123')
        f.save()

        u = User(passwordhash='123')
        u.save()

        g = Group(name='usergroup')
        g.save()
        g.set_users([u.id])

        self.assertEqual(f.authors(), [])
        self.assertEqual(f.publishers(), [])
        self.assertEqual(f.author_groups(), [])
        self.assertEqual(f.publisher_groups(), [])

        self.assertFalse(f.user_can_write(u))
        self.assertFalse(f.user_can_publish(u))

        f.grant('Write', group=g)
        f.grant('Publish', group=g)

        f = Feed.get(id=f.id)

        self.assertEqual(f.authors(), [])
        self.assertEqual(f.publishers(), [])
        self.assertEqual(f.author_groups(), [g])
        self.assertEqual(f.publisher_groups(), [g])

        self.assertTrue(f.user_can_write(u))
        self.assertTrue(f.user_can_publish(u))
