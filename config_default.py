from os.path import dirname
CSRF_ENABLED = True
DATABASE_FILE = 'database.db'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 megabytes. reasonable.

SITE_VARS = {
    'site_title': 'StreetSign',
    'site_dir': dirname(__file__),
    'user_dir': dirname(__file__)+'/app/static/user_files/',
    'user_url': '/static/user_files'
    }
