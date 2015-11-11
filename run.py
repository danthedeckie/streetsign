#!.virtualenv/bin/python
# -*- coding: utf-8 -*-
'''
    Simple run script for streetsign_server.

    Usage:

    ./run.sh
        (starts the development internal flask server.  FOR DEVELOPMENT ONLY!)

    ./run.sh waitress
        (starts the server running with the waitress production server)
'''

from __future__ import print_function

# Configuration Options:

__HOST__ = u'0.0.0.0'
__PORT__ = 5000
__THREADS__ = 8 # (for waitress, only)

# Initialise unicode:

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# Load the app:

from streetsign_server import app

# And start the correct server

if __name__ == '__main__':
    if len(sys.argv) == 2:
        if sys.argv[1] == 'waitress':
            print("'Production' Server with Waitress.")
            print("Press <Ctrl-C> to stop")
            from waitress import serve
            serve(app, host=__HOST__, port=__PORT__, threads=__THREADS__)
        elif sys.argv[1] == 'profiler':
            print("Loading dev server with profiling on.")
            print("Press <Ctrl-C> to stop")
            from werkzeug.contrib.profiler import ProfilerMiddleware
            app.config['PROFILE'] = True
            app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[20])
            app.run(debug=True)
    else:
        print("Starting Development Server...")
        print("Press <Ctrl-C> to stop")
        app.run(host=__HOST__, port=__PORT__, debug = True)

