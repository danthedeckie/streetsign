# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from flask import Flask
#from flask_peewee.admin import Admin
#from flask_peewee.auth import Auth

app = Flask(__name__)
app.config.from_object('config')

from app import models
from app import views
from app.models import db, User, Group, Post, Feed, FeedPermission

#auth = Auth(app, db)
#admin = Admin(app, auth)

#[admin.register(x) for x in (User,Group,Post,Feed,FeedPermission)]
#admin.setup()

