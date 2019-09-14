from django.test import TestCase, SimpleTestCase
from django.utils.translation import gettext as _
from django.db.utils import IntegrityError

from .models import Feed, Post


class TestFeed(SimpleTestCase):
    def test_construct(self):
        f = Feed()


class TestPost(SimpleTestCase):
    def test_construct(self):
        p = Post()


class TestPostDB(TestCase):
    def test_cannot_save_without_feed(self):
        p = Post()

        with self.assertRaises(IntegrityError):
            p.save()

    def test_can_save_with_feed(self):
        f = Feed()
        f.save()
        p = Post(feed=f)
        p.save()


class TestFeedDB(TestCase):
    def test_empty_feed(self):
        f = Feed()
        f.save()

        self.assertEqual(0, f.posts_all.all().count())

    def test_single_post(self):
        f = Feed()
        f.save()

        p = Post(feed=f)
        p.save()

        self.assertEqual(1, f.posts_all.all().count())
        self.assertEqual(p, f.posts_all.all().first())


class TestFeedsView(TestCase):
    def test_empty(self):
        req = self.client.get('/feeds/')
        self.assertContains(req, _('No Feeds'))

    def test_contains_form(self):
        req = self.client.get('/feeds/')
        self.assertContains(req, _('Feed Name'))

    def test_submit_new_form(self):
        req = self.client.post('/feeds/', data={"name":'testfeed'})
        self.assertRedirects(req, '/feeds/testfeed')

        req = self.client.get('/feeds/testfeed')
        self.assertContains(req, 'testfeed')

    def test_single_feed(self):
        f = Feed(name="BLAH", slug="blah")
        f.save()

        req = self.client.get('/feeds/')
        self.assertContains(req, "BLAH")
        self.assertContains(req, "/feeds/blah")
