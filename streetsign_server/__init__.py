# -*- coding: utf-8 -*-
"""  StreetSign Digital Signage Project
     (C) Copyright 2013 Daniel Fairhead

    StreetSign is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    StreetSign is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with StreetSign.  If not, see <http://www.gnu.org/licenses/>.

"""

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from flask import Flask
import flask
#from flask_peewee.admin import Admin
#from flask_peewee.auth import Auth
try:
    import config
except:
    print("Config file missing!!!")
    import config_default

app = Flask(__name__) # pylint: disable=invalid-name
app.config.from_object('config')

import models
import streetsign_server.views as views
from models import DB, User, Group, Post, Feed, FeedPermission

#auth = Auth(app, db)
#admin = Admin(app, auth)

#[admin.register(x) for x in (User,Group,Post,Feed,FeedPermission)]
#admin.setup()

