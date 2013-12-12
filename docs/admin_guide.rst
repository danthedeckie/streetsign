StreetSign Admin's guide
========================

This is where the information goes about how to run a streetsign system.

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

Deployment
----------

You can use the built in ``waitress`` web server::

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

- `The official flask deployment docs <http://flask.pocoo.org/docs/deploying/>`
- `The waitress server docs<https://pylons.readthedocs.org/projects/waitress/en/latest/>`


Users
-----

When you first install, the ``setup.sh`` script will create some default users
for you.  The admin user has the default password ``password``.  You should
change this as soon as possible.

Since some things display differently for admins compared to 'normal' users,
it's probably a good idea if you are supporting other users, to create a 'normal'
user for yourself as well.  Then if someone is finding something confusing, you
can check from that non-admin user quickly.


