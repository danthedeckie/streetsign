'''
    Test Posts actually show up at the times they're supposed to,
    with the right time zones, etc.
'''

#pylint: disable=import-error, too-many-public-methods, too-few-public-methods

import sys
import os
from datetime import timedelta
from flask import json, url_for

sys.path.append(os.path.dirname(__file__) + '/..')

import streetsign_server.models as models
from streetsign_server.models import Post

from unittest_helpers import StreetSignTestCase

USERNAME = 'testuser'
USERPASS = '12345'


class TestLifetimes(StreetSignTestCase):
    ''' check posts actually show up during the right lifetime(s) '''

    def setUp(self):
        super(TestLifetimes, self).setUp()

        # Make some useful bits:

        self.feed = models.Feed.create(name='first feed')
        self.feed.save()

        self.user = models.User.create(name='test user', loginname=USERNAME,
                                       emailaddress='test@example.com',
                                       passwordhash='')
        self.user.set_password(USERPASS)
        self.user.save()

        self.feed.grant('Write', user=self.user)
        self.feed.grant('Publish', user=self.user)
        self.feed.save()

        self.posts = []

    def create_post(self, **kwargs):
        ''' create a post, return it '''
        p = models.Post.create(feed=self.feed, type='html',
                               content='{"content":"text"}', author=self.user,
                               **kwargs)

        p.save()

        self.posts.append(p)

        return p

    def get_posts(self, feeds):
        ''' request (via the view) all current posts in <feeds> '''

        feeds = ','.join([str(i) for i in feeds])
        url = '/screens/posts_from_feeds/%5B' + feeds + '%5D'
        return json.loads(self.client.get(url).data)['posts']

    def get_posts_ids(self, feeds):
        ''' return the ids as a list of all posts returned by the
            posts_from_feeds view. '''

        return [x['id'] for x in self.get_posts(feeds)]

    def test_empty(self):
        ''' no posts in database '''

        self.assertEqual(models.Post.select().count(), 0)

        self.assertEqual(self.get_posts([self.feed.id]), [])

    def test_default_post(self):
        ''' check that the create_post helper creates a valid post, and
            that when we ask it to be published, it does show up '''

        self.create_post()
        self.assertEqual(self.get_posts_ids([self.feed.id]), [])

        p = self.create_post(published=True)
        self.assertEqual(self.get_posts_ids([self.feed.id]), [p.id])

    def test_post_past(self):
        ''' check that posts in the past don't show up in the list '''

        self.create_post(published=True,
                         active_start=models.now() - timedelta(hours=2),
                         active_end=models.now() - timedelta(minutes=1))

        self.assertEqual(self.get_posts_ids([self.feed.id]), [])

    def test_post_future(self):
        ''' test that posts in the future don't appear '''

        self.create_post(published=True,
                         active_start=models.now() + timedelta(hours=2),
                         active_end=models.now() + timedelta(days=2))

        self.assertEqual(self.get_posts_ids([self.feed.id]), [])

    def test_future_timezone_live(self):
        ''' test that posts in a future do show up when the TIME_OFFSET
            sets the server to be in that future time. '''

        models.app.config['TIME_OFFSET'] = 0

        p = self.create_post(published=True,
                             active_start=models.now() + timedelta(hours=1),
                             active_end=models.now() + timedelta(days=2))

        self.assertEqual(self.get_posts_ids([self.feed.id]), [])

        models.app.config['TIME_OFFSET'] = 60

        self.assertEqual(self.get_posts_ids([self.feed.id]), [p.id])

        models.app.config['TIME_OFFSET'] = 0

    def test_future_timezone_future(self):
        ''' test that even though the TIME_OFFSET config var sets the
            server into the future, if we're not *enough* in the future
            to see a post, it still doesn't appear. '''

        models.app.config['TIME_OFFSET'] = 0

        self.create_post(published=True,
                         active_start=models.now() + timedelta(hours=1),
                         active_end=models.now() + timedelta(days=2))

        self.assertEqual(self.get_posts_ids([self.feed.id]), [])

        models.app.config['TIME_OFFSET'] = 30

        self.assertEqual(self.get_posts_ids([self.feed.id]), [])

        models.app.config['TIME_OFFSET'] = 0

    def test_future_timezone_past(self):
        ''' test that if the TIME_OFFSET config var puts the server
            into the future, but a post is not in the future enough
            for the timezone to match, it doesn't show up. '''

        models.app.config['TIME_OFFSET'] = 0

        p = self.create_post(published=True,
                             active_start=models.now() - timedelta(hours=9),
                             active_end=models.now() - timedelta(hours=1))

        self.assertEqual(self.get_posts_ids([self.feed.id]), [])

        models.app.config['TIME_OFFSET'] = -30

        self.assertEqual(self.get_posts_ids([self.feed.id]), [])

        models.app.config['TIME_OFFSET'] = -120

        self.assertEqual(self.get_posts_ids([self.feed.id]), [p.id])

        models.app.config['TIME_OFFSET'] = 0


class TestLifetimesPostedWithOffsets(TestLifetimes):
    ''' Testing that when the TIME_OFFSET config var is set, new
        posts do actually show up when we expect them to. '''

    def post_new_post_now(self):
        ''' check that things are cool now, whatever now is '''

        self.login(USERNAME, USERPASS)

        with self.ctx():
            resp = self.client.get(url_for('feedpage', feedid=self.feed.id))

            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.feed.name, resp.data)

            resp = self.client.post(url_for('post_new', feed_id=self.feed.id),
                                    data={"post_type":"html",
                                          "content": "{'content':'test'}",
                                          "active_start": models.now(),
                                          "active_end": models.now() + \
                                                        timedelta(minutes=1),
                                         },
                                    follow_redirects=True)

        post = Post.get()
        post.publish(self.user)
        post.save()

        return post

    def test_post_zero_offset(self):
        ''' test that with TIME_OFFSET of 0, things work as we expect '''

        models.app.config['TIME_OFFSET'] = 0

        p = self.post_new_post_now()

        self.assertEqual(self.get_posts_ids([self.feed.id]), [p.id])

        models.app.config['TIME_OFFSET'] = 60

        self.assertEqual(self.get_posts_ids([self.feed.id]), [])

        models.app.config['TIME_OFFSET'] = -60

        self.assertEqual(self.get_posts_ids([self.feed.id]), [])

    def test_post_1h_offset(self):
        ''' test that with TIME_OFFSET of 1 hour, things work as we expect '''

        models.app.config['TIME_OFFSET'] = 60

        p = self.post_new_post_now()

        self.assertEqual(self.get_posts_ids([self.feed.id]), [p.id])

        models.app.config['TIME_OFFSET'] = 0

        self.assertEqual(self.get_posts_ids([self.feed.id]), [])

        models.app.config['TIME_OFFSET'] = -60

        self.assertEqual(self.get_posts_ids([self.feed.id]), [])

    def test_post_neg_1h_offset(self):
        ''' check that one hour in the past works '''

        models.app.config['TIME_OFFSET'] = -60

        p = self.post_new_post_now()

        self.assertEqual(self.get_posts_ids([self.feed.id]), [p.id])

        models.app.config['TIME_OFFSET'] = 0

        self.assertEqual(self.get_posts_ids([self.feed.id]), [])

        models.app.config['TIME_OFFSET'] = 60

        self.assertEqual(self.get_posts_ids([self.feed.id]), [])


