# -*- coding: utf-8 -*-
"""  Concertino Digital Signage Project
     (C) Copyright 2013 Daniel Fairhead

    Concertino is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Concertino is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Concertino.  If not, see <http://www.gnu.org/licenses/>.

    -------------------------------

    peewee ORM database models.

"""



from flask import json
from peewee import *
import sqlite3 # for catching an integrity error
from passlib.hash import bcrypt # for passwords
from uuid import uuid4 # for unique session ids
from datetime import datetime
import app.post_types
from app import app

SECRET_KEY = app.config.get('SECRET_KEY')

DB = SqliteDatabase(app.config.get('DATABASE_FILE'))

__all__ = [ 'DB', 'user_login', 'user_logout', 'get_logged_in_user',
            'User', 'Group', 'Post', 'Feed', 'FeedPermission', 'UserGroup',
            'ConfigVar', 'Screen',
            'create_all', 'by_id' ]


class DBModel(Model):
    class Meta:
        database = DB

##############################################################################
#
# Users & Groups:
#

class User(DBModel):
    loginname = CharField(unique=True)
    displayname = CharField(null=True)
    emailaddress = CharField()

    passwordhash = CharField()

    is_admin = BooleanField(default=False)
    is_locked_out = BooleanField(default=False)

    last_login_attempt = DateTimeField(default=datetime.now)
    failed_logins = IntegerField(default=0)

    def set_password(self, password):
        self.passwordhash = bcrypt.encrypt(password + SECRET_KEY)

    def confirm_password(self, password):
        return bcrypt.verify(password + SECRET_KEY, self.passwordhash)

    def __repr__(self):
        return '<User:' + self.displayname + '>'

    def writeable_feeds(self):
        if self.is_admin:
            return Feed.select()
        return [f for f in Feed.select() if f.user_can_write(self)]

    def publishable_feeds(self):
        if self.is_admin:
            return Feed.select()
        # TODO: make this a SQL select query, rather than this silly
        #       slow way.
        return [f for f in Feed.select() if f.user_can_publish(self)]

    def groups(self):
        return [g for g in Group.select().join(UserGroup)
                                .where(UserGroup.user==self)]

    def set_groups(self, groupidlist):
        # clear old groups:
        UserGroup.delete().where(UserGroup.user==self).execute()

        #set new ones:
        for gid in groupidlist:
            try:
                g = Group.get(id=gid)
                ug = UserGroup(user=self, group=g).save()
            except:
                return False, 'Invalid user, or groupid'

        return True, self.groups()

##########
# login stuff:

class UserSession(DBModel):
    id = CharField(primary_key=True)
    username = CharField()

    user = ForeignKeyField(User)
    login_time = DateTimeField(default=datetime.now)


class InvalidPassword(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def user_login(name, password):
    ''' preferred way to get a user object, which checks the password,
        and either returns a User object, or raises an exception '''

    user = User.select().where(User.loginname == name).get()
    # on error, raises: User.DoesNotExist

    if bcrypt.verify(password + SECRET_KEY, user.passwordhash):
        session = UserSession(id=str(uuid4()), username=user.loginname, user=user)
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


#########################################

class Group(DBModel):
    name = CharField()
    display = BooleanField(default=True)

    def __repr__(self):
        return '<Group:' + self.name + \
            ('(hidden)>' if not self.display else '>')

    def users(self):
        return [u for u in User.select().join(UserGroup)
                                .where(UserGroup.group==self)]

    def set_users(self, useridlist):
        # clear old groups:
        UserGroup.delete().where(UserGroup.group==self).execute()

        #set new ones:
        for uid in useridlist:
            try:
                u = User.get(id=uid)
                ug = UserGroup(group=self, user=u).save()
            except:
                return False, 'Invalid user'

        return True, self.users()


class UserGroup(DBModel):
    # XREF
    user = ForeignKeyField(User)
    group = ForeignKeyField(Group)

#############################################################################
#
# Posts & Feeds:
#
class Feed(DBModel):
    name = CharField(default='New Feed')

    def __repr__(self):
        return '<Feed:' + self.name + '>'

    # Yes, I like comprehensions.
    def authors(self):
        return [p.user for p in self.permissions if p.write == True and p.user]

    def publishers(self):
        return [p.user for p in self.permissions if p.publish == True and p.user]

    def author_groups(self):
        return [p.group for p in self.permissions if p.write == True and p.group]

    def publisher_groups(self):
        return [p.group for p in self.permissions if p.publish == True and p.group]

    def user_can_read(self, user):
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
        if not user:
            return False

        if user.is_admin:
            return True

        if user.is_locked_out:
            return False

        # check for user-level read permission:
        if self.permissions.where((FeedPermission.user==user) &
                                  (FeedPermission.write==True)).exists():
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
        if not user:
            return False

        if user.is_admin:
            return True

        if user.is_locked_out:
            return False

        # check for user-level read permission:
        if self.permissions.where((FeedPermission.user==user) &
                                  (FeedPermission.publish==True)).exists():
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
        # one of them *must* be selected...
        assert (user,group) != (None,None)
        assert (user and group) == None
        # first get previous permission, if there is one.

        if permission == 'Read':
            p = FeedPermission.read
        elif permission == 'Write':
            p = FeedPermission.write
        elif permission == 'Publish':
            p = FeedPermission.publish

        try:
            if user:
                perm = FeedPermission.get((FeedPermission.feed==self)
                                         &(FeedPermission.user==user)
                                         &(p==True))
            elif group:
                perm = FeedPermission.get((FeedPermission.feed==self)
                                         &(FeedPermission.group==group)
                                         &(p==True))
            else:
                raise Exception('You must specify either a user or a group!')
        except FeedPermission.DoesNotExist as e:
            perm = FeedPermission(feed=self, user=user, group=group)

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
        FeedPermission.delete().where((FeedPermission.feed==self)
                                     &(FeedPermission.write==True)
                                     &(FeedPermission.user)).execute()
        for a in authorlist:
            assert(isinstance(a, User))
            self.grant('Write', user=a)

    def set_publishers(self, publisherlist):
        ''' set the complete publisherlist. deletes previous set '''
        # delete old permissions first.
        FeedPermission.delete().where((FeedPermission.feed==self)
                                     &(FeedPermission.publish==True)
                                     &(FeedPermission.user)).execute()

        for p in publisherlist:
            assert(isinstance(p, User))
            self.grant('Publish', user=p)

    def set_author_groups(self, authorlist):
        ''' set the complete author_groups list. deletes previous set '''

        # delete old permissions first.
        FeedPermission.delete().where((FeedPermission.feed==self)
                                     &(FeedPermission.publish==True)
                                     &(FeedPermission.group)).execute()
        for a in authorlist:
            assert(isinstance(a, Group))
            self.grant('Write', group=a)

    def set_publisher_groups(self, publisherlist):
        ''' set the complete publisher_groups list. deletes previous set '''
        # delete old permissions first.
        FeedPermission.delete().where((FeedPermission.feed==self)
                                     &(FeedPermission.publish==True)
                                     &(FeedPermission.group)).execute()

        for p in publisherlist:
            assert(isinstance(p, Group))
            self.grant('Publish', group=p)


def writeable_feeds(user):
    if user.is_admin:
        return Feed.select()
    # TODO - re-write this as a SQL query, rather than this silly slow method.
    return [f for f in Feed.select() if f.user_can_write(user)]

class FeedPermission(DBModel):
    feed = ForeignKeyField(Feed, related_name='permissions')

    user = ForeignKeyField(User, null=True)
    # OR...
    group = ForeignKeyField(Group, null=True)

    read = BooleanField(default=True)
    write = BooleanField(default=False)
    publish = BooleanField(default=False)

class Post(DBModel):
    type = TextField()
    content = TextField()
    feed = ForeignKeyField(Feed, related_name='posts')

    author = ForeignKeyField(User)

    write_date = DateTimeField(default=datetime.now)

    #publisher info:
    published = BooleanField(default=False)
    publish_date = DateTimeField(null=True)
    publisher = ForeignKeyField(User, null=True)

    # Should it actually be displayed?
    status = IntegerField(default=0)
    status_options = {
        0: 'active',
        1: 'finished',
        2: 'archived'
        }

    # When should the feed actually be shown:
    active_start = DateTimeField(null=True)
    active_end = DateTimeField(null=True)

    # Time restrictions don't need to be cross queried, and honestly
    # are easier just left in javascript/JSON land:
    # are these restrictions "Only show during these times" or
    #                        "Do not show during these times" ?
    time_restrictions_show = BooleanField(default=False)

    # and the actual restrictions:
    time_restrictions = TextField(default='[]')
    # {"start_time", "end_time", "note"}

    # For how long should it be displayed?
    display_time = IntegerField(default=8)

    def __repr__(self):
        return '<Post:{0}:{1}>'.format(self.type, self.content[0:22])

    def repr(self):
        return json.loads(self.content)['content'][0:12] + '...(' + self.type + ')'

    def dict_repr(self):
        ''' must give all info, for use on screens, etc. '''
        return (
            { 'id': self.id,
              'type': self.type,
              'content': json.loads(self.content),
              'time_restrictions': json.loads(self.time_restrictions),
              'time_restrictions_show': self.time_restrictions_show,
              'display_time': self.display_time * 1000 # in milliseconds
            })
    def active_status(self):
        time_now = datetime.now()
        if not (self.active_start and self.active_end):
            return 'future'
        if (self.active_start > time_now):
            return 'future'
        elif (self.active_end < time_now):
            return 'past'
        else:
            return 'now'






##############################################################################

class ConfigVar(DBModel):
    ''' place to store site-wide front-end-editable settings. '''
    id = CharField(primary_key=True)
    value = CharField(null=True)
    description = CharField(default="Setting")

class Screen(DBModel):
    # Since most of the settings here are made with a JS interface,
    # and sent as json packets to another JS interface for display,
    # and don't need to be queried against, just leave 'em as JSON.

    urlname = CharField(unique=True, null=False)
    background = CharField(null=True)
    # JSON:
    settings = TextField(default={})
    defaults = TextField(default={})
    zones = TextField(default={})

##############################################################################

def create_all():
    ''' initialises the database, creates all needed tables. '''
    [t.create_table(True) for t in
        (User, UserSession, Group, UserGroup, Post, Feed,
         FeedPermission, ConfigVar, Screen)]

def by_id(model, ids):
    ''' returns a list of objects, selected by id (list) '''
    return [x for x in model.select().where(model.id << [int(i) for i in ids])]
