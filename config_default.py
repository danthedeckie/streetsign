'''
    config_default.py:

    This file contains the configuration DEFAULTS for a streetsign installation.
    These values should NOT be changed, except as part of streetsign development.

    You should put values you want to use instead of these in config.py, which
    will include all of these values first, and then over-ride them as needed.

    Instead of changing anything here, copy it into config.py, and change it
    there.

'''

from os.path import dirname
CSRF_ENABLED = True
DATABASE_FILE = 'database.db'

# Refuse to accept file uploads bigger than this:

MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 megabytes. reasonable.

# should change some logging settings, etc.  Currently changes very little:

MODE = 'production'

# in minutes.  Usually you'll want to change this by a multiple of 60,
#              so TIME_OFFSET=60 means server time +1 hour,
#                 TIME_OFFSET=-120 means server time -2 hours, etc.

TIME_OFFSET = 0

# These are available in all templates, so useful for storing configuration
# strings, etc.

SITE_VARS = {
    'site_title': 'StreetSign',
    'site_dir': dirname(__file__),
    'user_dir': dirname(__file__)+'/streetsign_server/static/user_files/',
    'user_url': '/static/user_files',
    }
