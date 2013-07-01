from peewee import *
import sqlite3 # for catching an integrity error
from passlib.hash import bcrypt # for passwords
from uuid import uuid4 # for unique session ids
from datetime import datetime
from app import app

SECRET_KEY = app.config.get('SECRET_KEY')

DB = SqliteDatabase(app.config.get('DATABASE_FILE'))

__all__ = [ 'DB', 'User', 'user_login', 'user_logout', 'get_logged_in_user',
            'Group', 'Post', 'PostType', 'Feed', 'FeedPermission', 'create_db' ]

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

class PostType(DBModel):
    name = CharField(default='Post Data Type...')
    description = TextField(default='Type of data for posts.')
    handler = CharField(default='text')


class Post(DBModel):
    type = ForeignKeyField(PostType)
    content = TextField()
    author = ForeignKeyField(User)

    write_date = DateTimeField(default=datetime.now)

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
        if (self.permissions.join(Group)
                            .join(UserGroup)
                            .where(UserGroup.user == user,
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

class FeedPost(DBModel):
    feed = ForeignKeyField(Feed, related_name='postsxref')
    post = ForeignKeyField(Post, related_name='feedsxref')

    published = BooleanField(default=False)
    publish_date = DateTimeField(null=True)
    publisher = ForeignKeyField(User, null=True)

##############################################################################

def create_all():
    ''' initialises the database, creates all needed tables. '''
    [t.create_table(True) for t in
        (User, UserSession, Group, Post, Feed, FeedPost, PostType, FeedPermission)]

