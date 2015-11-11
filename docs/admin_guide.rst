StreetSign Admin's guide
========================

Here's first a guide on how to set up streetsign to play with.  For full proper
deployment (for real live production usage) check the :doc:`deployment` page.

Instalation
-----------

StreetSign requires python 2.7, imagemagick (to generate thumbnails).  If you
are installing on a fresh server, you may need to install ``python-headers``
or ``python27-dev`` or whatever your distribution calls it.

(On a stock OSX computer, it doesn't need anything.)

Once you've cloned or otherwise downloaded StreetSign and put it where you
want it to be, you need to run the setup script::

    ./setup.sh

which will create a python virtualenv in ``.virtualenv``, and install all the
libraries and other requirements into there.

Running it.
-----------

To run the server in 'production mode' you can use the built in ``waitress`` web server::

    ./run.py waitress

Which will spin up a version which should be totally capable for small
deployments (up to a hundred screens or so, I guess).  If you are going to be
on a public network, then it's advised that you run streetsign - either with
waitress or another WSGI server of your choice - behind nginx or another
reverse proxy, which should keep things a bit saner.  If you're on a public
network, also remember to set up your reverse proxy to use SSL, so that you
aren't sending log-in credentials around in plaintext.

If you want to run anther WSGI server, remember the virtualenv that streetsign
is using, so any scripts you write need to use the python found in there
(``.virtualenv/bin/python``).  You can use pip from in there to install any
pypi packages you need too (``.virtualenv/bin/pip install gunicorn``, say).

Some links:
~~~~~~~~~~~

- `The official flask deployment docs <http://flask.pocoo.org/docs/deploying/>`_
- `The waitress server docs <https://pylons.readthedocs.org/projects/waitress/en/latest/>`_


Users
-----

When you first install, the ``setup.sh`` script will create some default users
for you.  The admin user has the default password ``password``.  You should
change this as soon as possible.

Since some things display differently for admins compared to 'normal' users,
it's probably a good idea if you are supporting other users, to create a 'normal'
user for yourself as well.  Then if someone is finding something confusing, you
can check from that non-admin user quickly.

Password hashes and moving the database
---------------------------------------

The user passwords are stored in the database hashed using two salts - an
individual salt per password (stored in standard passlib style in the password
field) and also with the site-wide "secret".  This "secret" is generated
automatically when you run the setup script, and is stored in the ``config.py``
file.  (It's also used by flask for encrypting session data, and so should
NEVER be stored in a repository, or shared outside deployment.)

What this means is that if you move a database.db file from one installation
to anonther, you will also need to bring the same config.py (or, at least, copy
the SECRET from there.)

Housekeeping & removing old content
-----------------------------------

By default, streetsign will tag content that has a lifetime which ended over a week
ago as "archived".  This means it no longer shows up on the interface for anyone
except admin users.  After a month, it will be deleted, including any uploaded images.

This "housekeeping" should take milliseconds to run as long as it's run regularly,
so each screen view will fire a request to the server to do it once an hour or so.
It and can also be triggered through the interface by hitting the "housekeeping"
button on the "All Posts" page, or on the front page (Dashboard).

If you want to ensure that this runs every hour or so, you can use standard unix
cron, or any other task scheduling program.

- ``HTTP POST`` to ``/posts/housekeeping``

so if you're using cron::

    0 * * * * nobody curl -d "" 'http://streetsign_url/posts/housekeeping' > /dev/null

should do it.

For automatically updating content from external feeds, again, screen views will
automatically do this once a minute, but you can also trigger it manually
(or via cron) with a

- ``HTTP POST`` to ``/external_data_sources/``

If you are on a public network, and worry about DOS issues, then realistically,
you should be running behind a revese proxy such as nginx.  With nginx you can
add restrictions on what URLS are accessble by any IP address, so you can limit
these addresses to only be accessed by the machine with cron, for instance.

Server Time
-----------

You may well have your main server running in one timezone (say GMT), but actually
be using the signs in another time zone.  By default, clients will all use their
own local time zone, and the server uses the server time.  There is a configuration
option you can set in ``config.py``::

    TIME_OFFSET=60

for example, which will offset post lifetimes, etc, by an hour.  (Minutes are used
so that half-hour-off timezones are supported).

