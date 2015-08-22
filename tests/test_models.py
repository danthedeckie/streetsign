'''
    Unit Tests for basic stuff in the models.py file.  Not *all*
    the tests for all ORM models, but helper functions, etc.
'''

import sys
import os
import unittest
from peewee import CharField

sys.path.append(os.path.dirname(__file__) + '/..')

import streetsign_server.models as models

from unittest_helpers import StreetSignTestCase
from datetime import datetime, timedelta

#pylint: disable=too-few-public-methods, invalid-name, no-member, missing-docstring, too-many-public-methods, no-init

class Test_safe_json_load(unittest.TestCase):
    ''' test the safe_json_load helper function '''

    def test_good(self):
        result = {"things": 241}
        self.assertEqual(models.safe_json_load('{"things":241}', None),
                         result)

    def test_bad(self):
        self.assertEqual(models.safe_json_load('oh dear', 42), 42)


class Test_by_id(StreetSignTestCase):
    ''' test the by_id helper function '''

    def test_users_none(self):
        self.assertEqual(models.by_id(models.User, []), [])

    def test_users_none_but_some_exist(self):
        models.User(loginname='test', passwordhash='1234').save()
        models.User(loginname='test2', passwordhash='1234').save()

        self.assertEqual(models.by_id(models.User, []), [])

    def test_users_one(self):
        u = models.User(loginname='test', passwordhash='1234')
        u.save()

        self.assertEqual(models.by_id(models.User, [u.id]), [u])

    def test_users_one_many_exist(self):
        models.User(loginname='test', passwordhash='1234').save()
        models.User(loginname='test2', passwordhash='1234').save()
        u = models.User(loginname='test3', passwordhash='1234')
        models.User(loginname='test4', passwordhash='1234').save()
        models.User(loginname='test5', passwordhash='1234').save()
        u.save()

        self.assertEqual(models.by_id(models.User, [u.id]), [u])

    def test_users_many_many_exist(self):
        models.User(loginname='test', passwordhash='1234').save()
        models.User(loginname='test2', passwordhash='1234').save()
        u = models.User(loginname='test3', passwordhash='1234')
        u2 = models.User(loginname='bono', passwordhash='1234')
        models.User(loginname='test5', passwordhash='1234').save()

        u.save()
        u2.save()

        self.assertEqual(models.by_id(models.User, [u.id, u2.id]), [u, u2])

    def test_users_invalid_ids(self):
        models.User(loginname='test', passwordhash='1234').save()
        models.User(loginname='test2', passwordhash='1234').save()
        u = models.User(loginname='test3', passwordhash='1234')
        u2 = models.User(loginname='bono', passwordhash='1234')
        models.User(loginname='test5', passwordhash='1234').save()

        u.save()
        u2.save()

        with self.assertRaises(models.User.DoesNotExist):
            models.User.get(id=42)

        with self.assertRaises(models.User.DoesNotExist):
            models.User.get(id=314)

        self.assertEqual(models.by_id(models.User, [42, 314]), [])

    def test_users_some_invalid_ids(self):
        models.User(loginname='test', passwordhash='1234').save()
        models.User(loginname='test2', passwordhash='1234').save()
        u = models.User(loginname='test3', passwordhash='1234')
        u2 = models.User(loginname='bono', passwordhash='1234')
        models.User(loginname='test5', passwordhash='1234').save()

        u.save()
        u2.save()

        with self.assertRaises(models.User.DoesNotExist):
            models.User.get(id=42)

        with self.assertRaises(models.User.DoesNotExist):
            models.User.get(id=314)

        self.assertEqual(models.by_id(models.User, [42, u.id, 314]), [u])

    def test_users_strid(self):
        u2 = models.User(loginname='bono', passwordhash='1234')
        models.User(loginname='test5', passwordhash='1234').save()

        u2.save()

        self.assertEqual(models.by_id(models.User, [str(u2.id)]), [u2])


class TestInvalidPassword(unittest.TestCase):
    def test_raises_ok(self):
        with self.assertRaises(models.InvalidPassword):
            raise models.InvalidPassword('this is the value!')

    def test_raises_value_set(self):
        with self.assertRaises(models.InvalidPassword) as em:
            raise models.InvalidPassword('this is the value!')

        self.assertEqual(em.exception.value, 'this is the value!')
        self.assertIn(str(em.exception),
                      ["'this is the value!'", '"this is the value!"'])

class Test_update_from(StreetSignTestCase):
    def test_no_regexps(self):
        class Thing(models.DBModel):
            text = CharField(default='stuff')

        t = Thing()

        f = {'text': 'set now'}

        t.update_from(f, 'text')

        self.assertEqual(t.text, 'set now')

    def test_not_in_form(self):
        class Thing(models.DBModel):
            text = CharField(default='stuff')

        t = Thing()

        f = {'text2': 'set now'}

        t.update_from(f, 'text')

        self.assertEqual(t.text, 'stuff')

    def test_regexp_matches(self):
        class Thing(models.DBModel):
            validation_regexp = {
                'text': r'.{1,10}'
            }
            text = CharField(default='stuff')

        t = Thing()

        f = {'text': 'set now'}

        t.update_from(f, 'text')

        self.assertEqual(t.text, 'set now')

    def test_regexp_fails(self):
        class Thing(models.DBModel):
            validation_regexp = {
                'text': r'.{1,10}'
            }
            text = CharField(default='stuff')

        t = Thing()

        f = {'text': 'this text is faaaaar too long for this simple'
                     ' regexp to match. oh dear'}

        with self.assertRaises(models.InvalidValue):
            t.update_from(f, 'text')

        self.assertEqual(t.text, 'stuff')

    def test_cb(self):
        ''' test using a callback to do stuff with errors '''
        class Thing(models.DBModel):
            validation_regexp = {
                'text': r'.{1,10}'
            }
            text = CharField(default='stuff')

        msgs = []

        def callback(problem):
            msgs.append(problem)

        t = Thing()

        f = {'text': 'this text is faaaaar too long for this simple'
                     ' regexp to match. oh dear'}

        t.update_from(f, 'text', cb=callback)

        self.assertEqual(t.text, 'stuff')
        self.assertEqual(len(msgs), 1)
        self.assertIn('oh dear', msgs[0])

    def test_different_formfield_name(self):
        class Thing(models.DBModel):
            text = CharField(default='stuff')

        t = Thing()

        f = {'text2': 'set now'}

        t.update_from(f, 'text', formfield='text2')

        self.assertEqual(t.text, 'set now')

class Test_models_now(unittest.TestCase):
    def test_zero_offset(self):
        models.app.config['TIME_OFFSET'] = 0

        before = datetime.now()
        now = models.now()
        after = datetime.now()

        self.assertLess(before, now)
        self.assertGreater(after, now)

    def test_30_mins_offset(self):
        models.app.config['TIME_OFFSET'] = 30

        before = datetime.now()
        now = models.now()
        after = datetime.now()
        after_plus_hour = datetime.now() + timedelta(hours=1)

        self.assertLess(before, now)
        self.assertLess(after, now)
        self.assertGreater(after_plus_hour, now)

    def test_neg_30_mins_offset(self):
        models.app.config['TIME_OFFSET'] = -30

        before = datetime.now()
        now = models.now()
        after = datetime.now()
        before_minus_hour = datetime.now() - timedelta(hours=1)

        self.assertGreater(before, now)
        self.assertGreater(after, now)
        self.assertLess(before_minus_hour, now)
