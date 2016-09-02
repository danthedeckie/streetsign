'''
    helpers/database.py - Various 'helper' functions, classes, etc for the
    database models.

    This module should NOT contain 'business logic'.  Only stuff that makes
    the logic in the models or controllers cleaner/saner/DRYer/better.

'''

from datetime import datetime, timedelta
from time import time, mktime

from peewee import *

from streetsign_server import app

DB = SqliteDatabase(None, threadlocals=True)

'''
--------------------------------------------------------------------------------
Useful functions
--------------------------------------------------------------------------------

'''

def now(timestamp=False):
    if timestamp:
         return mktime(now(False).timetuple())
    else:
        return datetime.now() + \
               timedelta(minutes=app.config.get('TIME_OFFSET', 0))

def safe_json_load(text, default):
    ''' either parse a string from JSON into python or else return default. '''
    try:
        return json.loads(text)
    except:  # pylint: disable=bare-except
        return default

def eval_datetime_formula(string):
    ''' evaluate a simple date/time formula, returning a unix datetime stamp '''

    replacements = [('WEEKS', '* 604800'),
                    ('WEEK', '* 604800'),
                    ('DAYS', '* 86400'),
                    ('DAY', '* 86400'),
                    ('MONTHS', '* 2592000'),  # 30 day month...
                    ('MONTH', '* 2592000'),
                   ]

    for rep_str, out_str in replacements:
        string = string.replace(rep_str, out_str)

    return simple_eval(string, names={'NOW': time()})


def by_id(model, ids):
    ''' returns a list of objects, selected by id (list) '''
    return [x for x in model.select().where(model.id << [int(i) for i in ids])]

'''
--------------------------------------------------------------------------------
Custom Exceptions
--------------------------------------------------------------------------------
'''

class InvalidValue(Exception):
    ''' for invalid values trying to be set by update_from '''
    pass

class PermissionDenied(Exception):
    ''' for when an unauthorized user tries to do something. '''
    pass

class InvalidPassword(Exception):
    ''' Oh no! Invalid password! '''

    def __init__(self, value):
        super(InvalidPassword, self).__init__(value)
        self.value = value
    def __str__(self):
        return repr(self.value)

'''
--------------------------------------------------------------------------------
Other
--------------------------------------------------------------------------------
'''

class DBModel(Model):
    ''' base class for other database models '''
    # pylint: disable=too-few-public-methods

    validation_regexp = {}

    def update_from(self, form, field, formfield=None, cb=False):
        ''' convenience method for updating fields in objects from a
            submitted form. allows for a callback on failure.
            each class has a validation_regexp dict '''
        formfield = formfield if formfield else field

        try:
            value = form[formfield]
            if value == re.match(self.validation_regexp.get(field, '.*'),
                                 value).group():
                fieldtype = type(getattr(self, field))
                if fieldtype == BooleanType and type(value) == UnicodeType:
                    setattr(self, field, value.lower() in ('true', 'yes', 'on'))
                else:
                    setattr(self, field, value)
            else:
                raise AttributeError('Does not match regexp!')
        except KeyError:
            # not in form
            pass
        except AttributeError:
            # fails regexp!
            err = '"%s" is not a valid %s' % (value, field)
            if cb:
                cb(err)
            else:
                raise InvalidValue(err)

    class Meta(object):
        ''' store DB info '''
        database = DB

def init(dbfile=False):
    ''' initialize the database connection '''
    if dbfile:
        DB.init(dbfile)
    else:
        DB.init(app.config.get('DATABASE_FILE'))


