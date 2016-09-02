# -*- coding: utf-8 -*-
"""  StreetSign Digital Signage Project
     (C) Copyright 2016 Daniel Fairhead

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
from flask.json import JSONEncoder

import flask

try:
    import config
except:
    print("Config file missing!!!")
    import config_default

app = Flask(__name__) # pylint: disable=invalid-name
app.config.from_object('config')

import models
import streetsign_server.views as views
from models import User, Group, Post, Feed, FeedPermission

class StreetSignEncoder(JSONEncoder):
    '''
        "Custom" JSON Encoder that works nicely with any model with a
        dict_repr() function. (IE, all our DBModels, hopefully.)
    '''
    def default(self, o):
        if hasattr(o, 'dict_repr'):
            return self.default(o.dict_repr())
        elif hasattr(o, 'keys'):
            return o
        elif hasattr(o, '__iter__'):
            return [self.default(i) for i in o]
        else:
            return JSONEncoder.default(self, o)

app.json_encoder = StreetSignEncoder
