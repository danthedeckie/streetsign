# -*- coding: utf-8 -*-
#  StreetSign Digital Signage Project
#     (C) Copyright 2013-2015 Daniel Fairhead
#
#    StreetSign is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    StreetSign is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with StreetSign.  If not, see <http://www.gnu.org/licenses/>.
#
#    -------------------------------
'''
========================
streetsign_server.models
========================

peewee ORM database models.

'''

# There's quite a bit of 'magic' / meta stuff going on in peewee, which totally
# confuses the heck out of pylint.  Also, some formatting stuff which makes
# sense for queries doesn't fit in exactly with PEP8 (eg:
#      Thing.select()
#           .where(items=things)
#           .join(more=options)
#
# Thus, the following awful looking pylint tweaking string:
#
# pylint: disable=invalid-name, too-many-public-methods, missing-docstring, pointless-string-statement, no-value-for-parameter, no-member, bad-continuation, unexpected-keyword-arg

from flask import json, url_for, Markup
from peewee import * # pylint: disable=wildcard-import,unused-wildcard-import
import sqlite3 # for catching an integrity error
from passlib.hash import bcrypt # pylint: disable=no-name-in-module
from uuid import uuid4 # for unique session ids
from datetime import datetime, timedelta
from time import time, mktime
import bleach # html stripping.
from hashlib import md5
from playhouse.migrate import *

try:
    import re2 as re # pylint: disable=import-error
except ImportError:
    import re

from simpleeval import simple_eval

from streetsign_server import app

SECRET_KEY = app.config.get('SECRET_KEY')

DB = SqliteDatabase(None)
MIGRATOR = SqliteMigrator(DB)

__all__ = ['DB', 'user_login', 'user_logout', 'get_logged_in_user',
           'User', 'Group', 'Post', 'Feed', 'FeedPermission', 'UserGroup',
           'ConfigVar', 'Screen', 'config_var', 'UserSession', 'ExternalSource',
           'init', 'create_all', 'by_id', 'migrations']


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

def init(dbfile=False):
    ''' initialize the database connection '''
    if dbfile:
        DB.init(dbfile)
    else:
        DB.init(app.config.get('DATABASE_FILE'))

def create_all(dbfile=False):
    ''' initialises the database, creates all needed tables. '''

    init(dbfile)

    for t in (User, UserSession, Group, UserGroup, Post, Feed,
              FeedPermission, ConfigVar, ExternalSource, Screen):
        t.create_table(True)

def by_id(model, ids):
    ''' returns a list of objects, selected by id (list) '''
    return [x for x in model.select().where(model.id << [int(i) for i in ids])]


'''
--------------------------------------------------------------------------------
Migrations
--------------------------------------------------------------------------------
'''


def migrations(dbfile=False):
    # http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#migrate
    init(dbfile)

    # Migration 1: add post title
    post_fields = DB.get_columns('Post')
    post_field_names = [x[0] for x in post_fields]  # 0: name of column

    if 'title' not in post_field_names:
        post_title = TextField(default='')
        migrate(
            MIGRATOR.add_column('Post', 'title', post_title)
        )


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
                if fieldtype is bool and type(value) is str:
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


'''
--------------------------------------------------------------------------------
Users & Groups
--------------------------------------------------------------------------------
'''

class User(DBModel):
    ''' Back-end user. '''

    validation_regexp = {
        'loginname': r'.{1,100}',
        'emailaddress': r'.*@.*\..*'
    }

    #: the unique name user to log in
    loginname = CharField(unique=True, default='new_user')
    #: how the user would like to be displayed
    displayname = CharField(null=True, default="New User")
    #: how to contact the user:
    emailaddress = CharField(default='')

    #: bcrypt'd, salted, etc password hash
    passwordhash = CharField()

    #: is the user an admin?
    is_admin = BooleanField(default=False)

    #: you can lock out users, so they cannot log in for a while.
    is_locked_out = BooleanField(default=False)

    #: when was the last attempt to log in?
    last_login_attempt = DateTimeField(default=now)
    #: how many times has the user failed to log in?
    failed_logins = IntegerField(default=0)

    def set_password(self, password):
        ''' Encrypts password, and sets the password hash.
            Not stored until you save! '''

        self.passwordhash = bcrypt.encrypt(password + SECRET_KEY)

    def confirm_password(self, password):
        ''' Check that password does verify against the stored hash '''

        return bcrypt.verify(password + SECRET_KEY, self.passwordhash)

    def __repr__(self):
        return '<User:' + self.displayname + '>'

    def writeable_feeds(self):
        ''' Returns a list of all Feeds this user can write to. '''

        if self.is_admin:
            return Feed.select()
        return [f for f in Feed.select() if f.user_can_write(self)]

    def publishable_feeds(self):
        ''' Returns all the Feeds that this user can publish to. '''

        if self.is_admin:
            return Feed.select()
        # TODO: make this a SQL select query, rather than this silly
        #       slow way.
        return [f for f in Feed.select() if f.user_can_publish(self)]

    def groups(self):
        ''' Returns all the Groups that this user is part of. '''

        return [g for g in Group.select()
                                .join(UserGroup)
                                .where(UserGroup.user == self)]

    def set_groups(self, groupidlist):
        ''' Set the grouplist for this user (and remove old groups) '''

        # clear old groups:
        UserGroup.delete().where(UserGroup.user == self).execute()

        #set new ones:
        for gid in groupidlist:
            try:
                UserGroup(user=self,
                          group=Group.get(id=gid)).save()
            except:
                return False, 'Invalid user, or groupid'

        return True, self.groups()


class Group(DBModel):
    ''' User groups (for permissions.) Groups can be given permission to
        publish/write/etc for certain Feeds, so this simplifies admin. '''

    name = CharField()
    display = BooleanField(default=True)

    def __repr__(self):
        return '<Group:' + self.name + \
            ('(hidden)>' if not self.display else '>')

    def users(self):
        return [u for u in User.select().join(UserGroup)
                                .where(UserGroup.group == self)]

    def set_users(self, useridlist):
        # clear old groups:
        UserGroup.delete().where(UserGroup.group == self).execute()

        #set new ones:
        for uid in useridlist:
            try:
                UserGroup(group=self,
                          user=User.get(id=uid)).save()
            except:
                return False, 'Invalid user'

        return True, self.users()


class UserGroup(DBModel):
    ''' Cross-Reference table '''
    # XREF
    user = ForeignKeyField(User)
    group = ForeignKeyField(Group)


'''
--------------------------------------------------------------------------------
Login Stuff
--------------------------------------------------------------------------------

Most of the time, these shouldn't be used directly, but instead use the
functions in :ref:`streetsign_server.user_session`.

'''

class UserSession(DBModel):
    ''' Track user logged in sessions in the database. '''

    id = CharField(primary_key=True) #: unique id
    username = CharField() #: which username?

    user = ForeignKeyField(User, related_name='sessions') #: the user
    login_time = DateTimeField(default=now) #: when did they log in?

def user_login(name, password):
    ''' preferred way to get a user object, which checks the password,
        and either returns a User object, or raises an exception '''

    user = User.select().where(User.loginname == name).get()
    # on error, raises: User.DoesNotExist

    if bcrypt.verify(password + SECRET_KEY, user.passwordhash):
        session = UserSession(id=str(uuid4()), username=user.loginname,
                                               user=user)
        session.save(force_insert=True)

        return user, session.id
    else:
        raise InvalidPassword('Invalid Password!')

def get_logged_in_user(name, uuid):
    ''' either returns a logged in user, or raises an error '''
    session = UserSession.get(id=uuid, username=name)
    return session.user

def user_logout(name, uuid):
    ''' removes a session '''
    UserSession.get(id=uuid, username=name).delete_instance()
    return True

'''
--------------------------------------------------------------------------------
Posts & Feeds:
--------------------------------------------------------------------------------
'''

class Feed(DBModel):
    ''' A Feed is kind of like a collection, or category of posts.
        Different 'zones' on screen outputs will subscribe to these Feeds. '''

    #: the name of the feed.
    name = CharField(default='New Feed')

    #: which types of posts are allowed in this feed (comma,separated)?
    post_types = CharField(default='text,html,image')

    def __repr__(self):
        return '<Feed:' + self.name + '>'

    def post_count(self, published=True, expired=False):
        ''' how many posts in this feed? '''
        q = self.posts
        if published:
            q = q.where(Post.published == True)
        if not expired:
            q = q.where(Post.active_end > now())
        return q.count()

    def post_types_as_list(self):
        ''' return a list of post types, from the single field '''
        return [i.strip() for i in self.post_types.split(',')]

    # Yes, I like comprehensions.
    def authors(self):
        ''' return all users with write permission '''
        return [p.user for p in self.permissions
                if p.write == True and p.user]

    def publishers(self):
        ''' return all users with publishing permission '''
        return [p.user for p in self.permissions
                if p.publish == True and p.user]

    def author_groups(self):
        ''' return all groups with write permission '''
        return [p.group for p in self.permissions
                if p.write == True and p.group]

    def publisher_groups(self):
        ''' return all groups with publishing permission '''
        return [p.group for p in self.permissions
                if p.publish == True and p.group]

    def user_can_read(self, user):
        ''' Checks read permission for a feed.  Not really used, as yet. '''
        if user.is_admin:
            return True

        if user.is_locked_out:
            return False

        # check for user-level read permission:
        if self.permissions.where((FeedPermission.user == User)
                                 &((FeedPermission.read == True))).exists():
            return True

        # check for group-level read permission:
        if (self.permissions.join(Group)
                            .join(UserGroup)
                            .where((UserGroup.user == user)
                                  &(FeedPermission.read == True)).exists()):
            return True

        # oh well! no permission!
        return False

    def user_can_write(self, user):
        ''' Checks write permission.  (Admins get automatically) '''
        if not user:
            return False

        if user.is_admin:
            return True

        if user.is_locked_out:
            return False

        # check for user-level read permission:
        if self.permissions.where((FeedPermission.user == user) &
                                  (FeedPermission.write == True)).exists():
            return True

        # check for group-level read permission:
        if (self.permissions.join(Group)
                            .join(UserGroup)
                            .where((UserGroup.user == user) &
                                   (FeedPermission.write == True)).exists()):
            return True

        # oh well! no permission!
        return False

    def user_can_publish(self, user):
        ''' Checks publish permission. (Admins get automatically) '''
        if not user:
            return False

        if user.is_admin:
            return True

        if user.is_locked_out:
            return False

        # check for user-level read permission:
        if self.permissions.where((FeedPermission.user == user) &
                                  (FeedPermission.publish == True)).exists():
            return True

        # check for group-level read permission:
        if (self.permissions.join(Group)
                            .join(UserGroup)
                            .where((UserGroup.user == user) &
                                   (FeedPermission.publish == True)).exists()):
            return True

        # oh well! no permission!
        return False

    def grant(self, permission, user=None, group=None):
        ''' Give either a user or group permission
            (either 'Read','Write' or 'Publish') on this Feed. '''

        # one of them *must* be selected...
        assert (user, group) != (None, None)
        assert (user and group) == None
        assert permission in ('Read', 'Write', 'Publish')
        # first get previous permission, if there is one.

        if permission == 'Read':
            p = FeedPermission.read
        elif permission == 'Write':
            p = FeedPermission.write
        elif permission == 'Publish':
            p = FeedPermission.publish
        else:
            raise Exception('Invalid permission.'
                            ' Must be Read,Write, or Publish')

        try:
            if user:
                perm = FeedPermission.get((FeedPermission.feed == self)
                                         &(FeedPermission.user == user)
                                         &(p == True))
            elif group:
                perm = FeedPermission.get((FeedPermission.feed == self)
                                         &(FeedPermission.group == group)
                                         &(p == True))
            else:
                raise Exception('You must specify either a user or a group!')
        except FeedPermission.DoesNotExist:
            perm = FeedPermission(feed=self, user=user, group=group)

        assert perm.user or perm.group

        perm.read = (permission == 'Read')
        perm.write = (permission == 'Write')
        perm.publish = (permission == 'Publish')

        # if we try and grant permission *before* this is saved, it will
        # fail. So cascade the saves!
        try:
            perm.save()
        except sqlite3.IntegrityError:
            self.save()
            perm.feed = self
            perm.save()

    # and some convenience functions:
    def set_authors(self, authorlist):
        ''' set the complete authorlist. deletes previous set '''

        # delete old permissions first.
        FeedPermission.delete().where((FeedPermission.feed == self)
                                     &(FeedPermission.write == True)
                                     &(FeedPermission.user)).execute()
        for a in authorlist:
            assert isinstance(a, User)
            self.grant('Write', user=a)

    def set_publishers(self, publisherlist):
        ''' set the complete publisherlist. deletes previous set '''
        # delete old permissions first.
        FeedPermission.delete().where((FeedPermission.feed == self)
                                     &(FeedPermission.publish == True)
                                     &(FeedPermission.user)).execute()

        for p in publisherlist:
            assert isinstance(p, User)
            self.grant('Publish', user=p)

    def set_author_groups(self, authorlist):
        ''' set the complete author_groups list. deletes previous set '''

        # delete old permissions first.
        FeedPermission.delete().where((FeedPermission.feed == self)
                                     &(FeedPermission.publish == True)
                                     &(FeedPermission.group)).execute()
        for a in authorlist:
            assert isinstance(a, Group)
            self.grant('Write', group=a)

    def set_publisher_groups(self, publisherlist):
        ''' set the complete publisher_groups list. deletes previous set '''
        # delete old permissions first.
        FeedPermission.delete().where((FeedPermission.feed == self)
                                     &(FeedPermission.publish == True)
                                     &(FeedPermission.group)).execute()

        for p in publisherlist:
            assert isinstance(p, Group)
            self.grant('Publish', group=p)

class FeedPermission(DBModel):
    ''' Essentially a cross-reference table, but with specified permissions. '''

    feed = ForeignKeyField(Feed, related_name='permissions')

    user = ForeignKeyField(User, null=True)
    # OR...
    group = ForeignKeyField(Group, null=True)

    read = BooleanField(default=True)
    write = BooleanField(default=False)
    publish = BooleanField(default=False)

class Post(DBModel):
    ''' The actual main point of this whole thing.  The contents that get
        displayed.  This object/row/thing hands off all the actual editing
        of, displaying of, and validating of the contents to a post type
        module.  It's stored in the database as JSON.  This means new types
        of post can be added quite easily later, without changing the
        schema. '''

    title = TextField()  #: used to easily identify the post
    type = TextField() #: used to load the content-type module for this post
    content = TextField() #: JSON data sent to the content-type module
    feed = ForeignKeyField(Feed, related_name='posts') #: which feed

    author = ForeignKeyField(User, related_name='posts') #: who wrote it?

    write_date = DateTimeField(default=now) #: when was it written?

    #publisher info:
    published = BooleanField(default=False) #: is this post published?
    publish_date = DateTimeField(null=True) #: when was it published?
    #: who published it?
    publisher = ForeignKeyField(User, related_name='published_posts', null=True)

    # Should it actually be displayed?
    status = IntegerField(default=0) #: can be 0:active/1:finished/2:archived.
    status_options = {
        0: 'active',
        1: 'finished',
        2: 'archived'
        }

    # When should the feed actually be shown:
    active_start = DateTimeField(default=now) #: lifetime start
    active_end = DateTimeField(default=lambda: now() + \
                                               timedelta(weeks=1)) #: end

    #: Time restrictions don't need to be cross queried, and honestly
    #: are easier just left in javascript/JSON land:
    #: are these restrictions "Only show during these times" or
    #: "Do not show during these times" ?
    time_restrictions_show = BooleanField(default=False)

    #: and the actual restrictions:
    time_restrictions = TextField(default='[]')
    # {"start_time", "end_time", "note"}

    #: For how long should it be displayed?
    display_time = IntegerField(default=8)

    def __repr__(self):
        return '<Post:{0}:{1}>'.format(self.type, self.content[0:22])

    def repr(self):
        ''' This is actually used by the back-end to display different
            'thumbnails' of posts.  If you want to show HTML (careful!!!!!!!!)
            then wrap it in Markup(), so jinja2 doesn't escape it. '''

        # TODO: split this out to the various post_type modules, and cache it.
        try:
            content = safe_json_load(self.content, {'content':'None'})['content']
        except KeyError:
            content = "N/A"

        if self.type == 'image':
            return Markup('<img src="{0}" alt="{1}" />'.format(
                          url_for('thumbnail', filename='post_images/'+content),
                          content))
        else:
            return bleach.clean(content, tags=[], strip=True)[0:15] + '...(' + \
                    self.type + ')'

    def dict_repr(self):
        ''' must give all info, for use on screens, etc. '''
        return (
            {'id': self.id,
             'title': self.title,
             'type': self.type,
             'content': safe_json_load(self.content, {}),
             'time_restrictions': safe_json_load(self.time_restrictions, []),
             'time_restrictions_show': self.time_restrictions_show,
             'display_time': self.display_time * 1000, # in milliseconds
             'changed': self.write_date
            })

    def active_status(self):
        ''' is this post active now, in the future, or the past?
            (returns a string 'now'/'future'/'past') '''

        time_now = now()
        try:
            if not (self.active_start and self.active_end):
                return 'future'
            if self.active_start > time_now:
                return 'future'
            elif self.active_end < time_now:
                return 'past'
            else:
                return 'now'
        except TypeError:
            # SQLite doesn't really do types, so this can happen.
            return 'now'

    def publish(self, user, state=True):
        ''' set the published status, published & date of this post.
            use state=False to unpublish '''
        if self.feed.user_can_publish(user):
            self.published = state
            self.publisher = user if state else None
            self.publish_date = now() if state else None
            self.save()
            return True
        else:
            raise PermissionDenied("You don't have permission to publish"
                                   " posts on this feed.")

    def save(self, *vargs, **kwargs):
        ''' Save the state of the object to the database, updating
            the 'write_date' time along the way. '''

        self.write_date = now()
        return super(Post, self).save(*vargs, **kwargs)



class ExternalSource(DBModel):
    ''' How do we pull data in from external sources? '''

    #: name, displayed in the interface
    name = CharField()

    #: source types are loaded in later, the same as post types.
    type = CharField()

    #: how often to check for new data at the source...
    frequency = IntegerField(default=60)
    #: when was it last checked?
    last_checked = DateTimeField(null=True)

    #: Which feed should posts from this source show up in?
    feed = ForeignKeyField(Feed, related_name='external_sources')

    #: Where the actual per-type-specific settings are saved:
    settings = CharField(default='{}')

    #: Should new posts from this source start off published?
    publish = BooleanField(default=False)

    #: Which user should be set as the owner / author of these?
    post_as_user = ForeignKeyField(User, related_name='external_sources')

    #: initial post settings. (TODO)
    post_template = CharField(default='{}')

    #: Lifetime start of new posts (formula)
    lifetime_start = CharField(default="NOW")
    #: Lifetime end of new posts (formula)
    lifetime_end = CharField(default="NOW + 1 WEEK")

    #: how long should each post be displayed for?
    display_time = IntegerField(default=8)

    def current_lifetime_start(self):
        ''' given the equation in the lifetime_start field, what should
            the time be of a new post start time? '''
        return datetime.fromtimestamp(eval_datetime_formula(self.lifetime_start))

    def current_lifetime_end(self):
        ''' given the equation in the lifetime_end field, what time
            should the end of a new post lifetime be? '''
        return datetime.fromtimestamp(eval_datetime_formula(self.lifetime_end))


'''
--------------------------------------------------------------------------------
Screens & Other Output Spec
--------------------------------------------------------------------------------
'''

class Screen(DBModel):
    ''' Each URL for output is known as a screen. (You can point a web-browser
        with a physical screen at it.)  This stores the info needed to display
        them.

        Since most of the settings here are made with a JS interface,
        and sent as json packets to another JS interface for display,
        and don't need to be queried against, just leave 'em as JSON.

        '''

    # TODO: have JSON list Field types here, for validation, rather than
    #       in the view/logic code...

    #: the url where this will be available ``/screens/<urlname``
    urlname = CharField(unique=True, null=False)

    #: the background image
    background = CharField(null=True)

    #: screen settings (JSON)
    settings = TextField(default='{}')
    #: general CSS settings for the whole page. Can contain selectors, etc.
    css = TextField(default='')
    #: default post settings (JSON)
    defaults = TextField(default='{}')
    #: spec all the zones (JSON)
    zones = TextField(default='[]')

    def to_dict(self):
        ''' returns a dict, ready for transmission as JSON '''

        return {
            "id":self.id,
            "urlname": self.urlname,
            "background": self.background if self.background else '',
            "settings": safe_json_load(self.settings, {}),
            "defaults": safe_json_load(self.defaults, {}),
            "css": self.css if self.css else '',
            "zones": safe_json_load(self.zones, []),
            }
    def md5(self):
        return md5(json.dumps(self.to_dict()).encode()).hexdigest()


'''
--------------------------------------------------------------------------------
Misc
--------------------------------------------------------------------------------
'''

class ConfigVar(DBModel):
    ''' place to store site-wide front-end-editable settings. '''
    id = CharField(primary_key=True)
    value = CharField(null=True) # as JSON!
    description = CharField(default="Setting")

def config_var(key, default_value):
    ''' a 'get_or_create' type function for retrieving database ConfigVar
        values, or the default value it it hasn't been set.
        NOTE: returns the *value*, and NOT the database record!
        '''
    try:
        return json.loads(ConfigVar.get(ConfigVar.id == key).value)
    except ConfigVar.DoesNotExist:
        try:
            return default_value
        except sqlite3.IntegrityError:
            # ha! we have a race! and you lose...
            return json.loads(ConfigVar.get(ConfigVar.id == key).value)
