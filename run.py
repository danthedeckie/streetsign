#!.virtualenv/bin/python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from streetsign_server import app
app.run(host="0.0.0.0", debug = True)

