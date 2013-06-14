# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from flask import Flask

app = Flask(__name__)
app.config.from_object('config')

from app import views
