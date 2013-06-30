from peewee import *
import sqlite3
from passlib.hash import bcrypt # for passwords
from datetime import datetime
from app import app

SECRET_KEY=app.config.get('SECRET_KEY')

db = SqliteDatabase(app.config.get('DATABASE_FILE'))

__all__ = [ 'db', 'User', 'user_login', 'Group',
            'Post', 'Feed', 'FeedPermission',
            'create_db' ]



class DBModel(Model):
    class Meta:
        database = db

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

    last_login_attempt = DateTimeField(datetime.now)
    failed_logins = IntegerField(default=0)

    def set_password(self, password):
        self.passwordhash = bcrypt.encrypt(password + SECRET_KEY)


def user_login(name, password):
    ''' preferred way to get a user object, which checks the password,
        and either returns a User object, or False '''
    try:
        user = User.select().where(User.name == name).get()
    except User.DoesNotExist as e:
        return False

    if user.passwordhash == bcrypt.encrypt(password + SECRET_KEY):
        return user
    else:
        return False

class Group(DBModel):
    name = CharField()
    display = BooleanField(default=True)

class UserGroup(DBModel):
    # XREF
    user = ForeignKeyField(User)
    group = ForeignKeyField(Group)

#############################################################################
#
# Posts & Feeds:
#



class Post(DBModel):
    author = ForeignKeyField(User)
    publisher = ForeignKeyField(User, null=True)

    write_date = DateTimeField(datetime.now)
    publish_date = DateTimeField(null=True)

    # Should it actually be displayed?
    active = BooleanField(default=True)

class Feed(DBModel):
    name = CharField(default='New Feed')

    def user_can_read(self, user):
        if user.is_admin:
            return True

        if user.is_locked_out:
            return False

        # check for user-level read permission:
        if self.permissions.where((Permissions.user == User)
                                 &((Permissions.read == True))).exists():
            return True

        # check for group-level read permission:
        if (self.permissions.join(Group)
                            .join(UserGroup)
                            .where((UserGroup.user == user)
                                  &(Permissions.read == True)).exists()):
            return True

        # oh well! no permission!
        return False

    def user_can_write(self, user):
        if user.is_admin:
            return True

        if user.is_locked_out:
            return False

        # check for user-level read permission:
        if self.permissions.where(user==User, write==True).exists():
            return True

        # check for group-level read permission:
        if (self.permissions.join(Group).join(UserGroup).
                                       where(UserGroup.user == user,
                                            Permissions.write == True).exists()):
            return True

        # oh well! no permission!
        return False

    def grant(self, permission, user=None, group=None):
        # one of them *must* be selected...
        assert (user,group) != (None,None)
        assert (user and group) == None
        # first get previous permission, if there is one.
        try:
            perm = FeedPermission.select((FeedPermission.feed==self)
                                        &(FeedPermission.user==user)
                                        &(FeedPermission.group==group)).get()
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

class FeedPermission(DBModel):
    feed = ForeignKeyField(Feed, related_name='permissions')

    user = ForeignKeyField(User, null=True)
    # OR...
    group = ForeignKeyField(Group, null=True)

    read = BooleanField(default=True)
    write = BooleanField(default=False)
    publish = BooleanField(default=False)



##############################################################################

def create_all():
    ''' initialises the database, creates all needed tables. '''
    [t.create_table(True) for t in
        (User, Group, Post, Feed, FeedPermission)]

