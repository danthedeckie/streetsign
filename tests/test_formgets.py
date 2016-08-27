'''
    tests/test_formgets.py
    Tests for the various getstr/getint/getbool helper functions.
    Part of streetsign.
'''

import sys
import os

import unittest

sys.path.append(os.path.dirname(__file__) + '/..')

from streetsign_server.views.utils import getstr, getint, getbool, \
                                          DATESTR, STRIPSTR

# pylint: disable=too-many-public-methods, too-few-public-methods
# pylint: disable=missing-docstring, invalid-name

class FakeResp(object):
    ' Mock the Response global object, for testing form stuff. '
    def __init__(self):
        self.form = {}

class FakeRespCase(unittest.TestCase):
    '''
    Testcase which hides the real request global, and replaces it with
    a fake one
    '''

    def setUp(self):
        self.resp = FakeResp()
        self.realresp = getstr.func_globals['request']
        getstr.func_globals['request'] = self.resp
        getint.func_globals['request'] = self.resp
        getbool.func_globals['request'] = self.resp

    def tearDown(self, *vargs): # pylint: disable=unused-argument
        del getstr.func_globals['request']
        getstr.func_globals['request'] = self.realresp
        getint.func_globals['request'] = self.realresp
        getbool.func_globals['request'] = self.realresp

class TestGetStr(FakeRespCase):
    ' tests for the getstr helper method '

    def test_not_there(self):
        self.assertFalse('GETME' in self.resp.form)
        self.assertEquals(getstr('GETME', 'default_value'), 'default_value')

    def test_there(self):
        self.resp.form['GETME'] = 'set thing'
        self.assertEquals(getstr('GETME', 'default_value'), 'set thing')

    def test_empty(self):
        self.resp.form['GETME'] = ''
        self.assertEquals(getstr('GETME', 'default'), '')

    def test_validates(self):
        self.resp.form['GETME'] = 'blah'
        self.assertEquals(getstr('GETME', 'none', validate='.*@.*'), 'none')

    def test_validates_date(self):
        self.resp.form['GETME'] = 'blah'
        dateformat = r'(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)'
        date = '2016-10-12 16:02:19'

        self.assertEquals(getstr('GETME', 'none', validate=dateformat), 'none')

        self.resp.form['GETME'] = date
        self.assertEquals(getstr('GETME', 'none', validate=dateformat), date)

    def test_validate_fails(self):
        fallback = 42
        self.resp.form['GETME'] = 'Not a valid date.'
        self.assertEquals(getstr('GETME', fallback, validate=DATESTR), fallback)

    def test_validates_DATESTR_valid(self):
        date = '2016-10-12 16:02:19'
        self.resp.form['GETME'] = date
        self.assertEquals(getstr('GETME', 'none', validate=DATESTR), date)

    def test_validates_DATESTR_strip(self):
        date = '2016-10-12 16:02:19'
        self.resp.form['GETME'] = '   ' + date + '.00 stuff'
        self.assertEquals(getstr('GETME', 'none', validate=DATESTR), date)

    def test_validates_STRIPSTR_all(self):
        text = 'this is some text'
        self.resp.form['GETME'] = text
        self.assertEquals(getstr('GETME', 'none', validate=STRIPSTR), text)

    def test_validates_STRIPSTR_lstrip(self):
        text = 'this is some text'
        self.resp.form['GETME'] = ' ' + text
        self.assertEquals(getstr('GETME', 'none', validate=STRIPSTR), text)

    def test_validates_STRIPSTR_rstrip(self):
        text = 'this is some text'
        self.resp.form['GETME'] = ' ' + text + '\t'
        self.assertEquals(getstr('GETME', 'none', validate=STRIPSTR), text)

    def test_validates_STRIPSTR_stripboth(self):
        text = 'this is some text'
        self.resp.form['GETME'] = ' ' + text + '\t '
        self.assertEquals(getstr('GETME', 'none', validate=STRIPSTR), text)

    def test_validates_STRIPSTR_number(self):
        text = '2019'
        self.resp.form['GETME'] = ' ' + text + '\t '
        self.assertEquals(getstr('GETME', 'none', validate=STRIPSTR), text)

    def test_empty_string(self):
        self.resp.form['GETME'] = ''
        self.assertEquals(getstr('GETME', 'none'), '')

class TestGetInt(FakeRespCase):
    ' tests for the getint helper '
    def test_not_there(self):
        self.assertFalse('GETME' in self.resp.form)
        self.assertEquals(getint('GETME', 42), 42)

    def test_there(self):
        self.resp.form['GETME'] = 999
        self.assertEquals(getint('GETME', 42), 999)

    def test_empty(self):
        self.resp.form['GETME'] = ''
        self.assertEquals(getint('GETME', 42), 42)

    def test_validate_min(self):
        # input is big enough
        self.resp.form['GETME'] = 120
        self.assertEquals(getint('GETME', 42, minimum=99), 120)

        # end up on default
        del self.resp.form['GETME']
        self.assertEquals(getint('GETME', 100, minimum=99), 100)

        # fallback to minimum
        self.resp.form['GETME'] = 80
        self.assertEquals(getint('GETME', 42, minimum=99), 99)

    def test_validate_max(self):
        # input is small enough
        self.resp.form['GETME'] = 80
        self.assertEquals(getint('GETME', 42, maximum=99), 80)

        # end up on default
        del self.resp.form['GETME']
        self.assertEquals(getint('GETME', 100, maximum=200), 100)

        # fallback to maximum
        self.resp.form['GETME'] = 80
        self.assertEquals(getint('GETME', 42, maximum=25), 25)


    def test_validate_minmax(self):
        # input is small enough
        self.resp.form['GETME'] = 80
        self.assertEquals(getint('GETME', 42, minimum=20, maximum=99), 80)

        # end up on default
        del self.resp.form['GETME']
        self.assertEquals(getint('GETME', 75, minimum=20, maximum=99), 75)

        # fallback to maximum
        self.resp.form['GETME'] = 9000
        self.assertEquals(getint('GETME', 42, minimum=20, maximum=99), 99)

        # fallback to minimum
        self.resp.form['GETME'] = 9
        self.assertEquals(getint('GETME', 42, minimum=20, maximum=99), 20)

class TestGetBool(FakeRespCase):
    ' tests for the getbool helper function '
    def test_getbool_not_there(self):
        self.assertFalse('GETME' in self.resp.form)
        self.assertFalse(getbool('GETME', False))
        self.assertTrue(getbool('GETME', True))

    def test_getbool_True(self):
        self.resp.form['GETME'] = True
        self.assertTrue(getbool('GETME', True))

    def test_getbool_TrueStr(self):
        self.resp.form['GETME'] = 'True'
        self.assertTrue(getbool('GETME', True))

    def test_getbool_trueStr(self):
        self.resp.form['GETME'] = 'true'
        self.assertTrue(getbool('GETME', True))

    def test_getbool_TRUEStr(self):
        self.resp.form['GETME'] = 'TRUE'
        self.assertTrue(getbool('GETME', True))

    def test_getbool_1(self):
        self.resp.form['GETME'] = 1
        self.assertTrue(getbool('GETME', True))

    def test_getbool_1Str(self):
        self.resp.form['GETME'] = '1'
        self.assertTrue(getbool('GETME', True))

    def test_getbool_yesStr(self):
        self.resp.form['GETME'] = 'yes'
        self.assertTrue(getbool('GETME', True))

    def test_getbool_YesStr(self):
        self.resp.form['GETME'] = 'Yes'
        self.assertTrue(getbool('GETME', True))

    def test_getbool_YESStr(self):
        self.resp.form['GETME'] = 'YES'
        self.assertTrue(getbool('GETME', True))

    def test_getbool_checkedStr(self):
        self.resp.form['GETME'] = 'checked'
        self.assertTrue(getbool('GETME', True))

    def test_getbool_CheckedStr(self):
        self.resp.form['GETME'] = 'Checked'
        self.assertTrue(getbool('GETME', True))

    def test_getbool_CHECKEDStr(self):
        self.resp.form['GETME'] = 'CHECKED'
        self.assertTrue(getbool('GETME', True))


