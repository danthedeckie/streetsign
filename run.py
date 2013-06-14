#!.virtualenv/bin/python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from app import app
app.run(debug = True)

