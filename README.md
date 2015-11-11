# StreetSign (Server)

[![Coverage Status](https://coveralls.io/repos/danthedeckie/streetsign/badge.png)](https://coveralls.io/r/danthedeckie/streetsign)

A digital signage system, inspired by Concerto, however written in Flask/Peewee/Python,
with a simpler basis.  This project was originally written for Teenstreet 2013 in Germany
(http://www.teenstreet.de).

Although this has been used at a large conference, it's still very much work in progress,
so if you do use it, expect changes in the future, and some features missing.

There is a full documentation in progress at [streetsign.readthedocs.org](http://streetsign.readthedocs.org/en/latest/)

## Usage:

clone this into the directory you want to use for the project, and type

    ./setup.sh

and you're going!

To run the app with the flask autoreloading magic use

    ./run.py

for production deployment, you can run:

    ./run.py waitress

to run the server using the waitress WSGI server, or you can use any other WSGI server of your choice.  It is recommended for 'big' deployments that you use nginx or a similar reverse proxy in front of the WSGI server, and also that you serve the static folder (javascript, css, pictures, etc) statically.

## Requirements:

Most packages will be installed by the ./setup.sh script into a folder called .virtualenv.

You you will need Python 2.6/2.7 or so, and the Python headers package (python-dev on Debian, python-devel on CentOS),
with a  functioning gcc for compiling the various requirements.

For the thumbnail generation, and image-resizing, you'll need 'ImageMagick' installed (the 'convert' command).

So on CentOS:

    yum install python-devel ImageMagick

or on Debian/Ubuntu:

    apt-get install python-pip python-dev imagemagick

## More info:

The virtual env is kept in .virtualenv, and usually shouldn't need to be touched.  I don't like the entering and exiting a virtualenv business, so went with the 'virtualenv stuff happens transparently when you use run.py, you shouldn't have to care about it' approach.  If you want to run python for the virtualenv, use .virtualenv/bin/python

The `setup.sh` script is to allow you to get up an running on a new machine in seconds. (On an old machine, minutes, while it downloads and installs flask...)  I like the github idea of 'all a new developper needs to do is run one command, and they have a whole system ready to go'.

When first installed, the initial login credentials are:

user: `admin`
password: `password`

There are also some other basic users created.  You should change the admin password, and delete those users before deployment.

## pre-commit hook
There is the [pre-commit script by Sebastian Dahlgren](https://github.com/sebdah/git-pylint-commit-hook) in the .setup/hooks/ folder, which will run pylint on python scripts to check they are valid before you commit them. The setup.sh script will copy this into your .git/hooks by default.

To run a git commit *without* using this, use:

    git commit --no-verify

(or `git commit -an` also works...) 


## Other notes

See the [main documentation](http://streetsign.readthedocs.org/en/latest)

### Magic Vars in posts:

You can use 2 magic variables in html or text posts:

    %%TIME%%

and

    %%DATE%%

these will be replaced by the current time, or date, respectively, and are kept
up to date by the system.

### Why isn't my post showing up?!

- Does it have time restrictions which are in the way?
- Is it published?
- Does the output screen have the correct feeds selected?
- Try refreshing the output screen (this shouldn't need to happen, but hey, it's currently work in progress)
