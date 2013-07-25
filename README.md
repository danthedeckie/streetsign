# Concertino
A digital signage system, inspired by Concerto, however written in Flask/Peewee/Python,
with a simpler basis.  The name is subject to change, probably in the near future, to
make it easier not to tread on the toes of the Concerto project.  Concertino is just
my working title.

Work in Progress! Do not consider production ready yet!

## Usage:

clone this into the directory you want to use for the project, and type

    ./setup.sh

and you're going!

To run the app with the flask autoreloading magic use

    ./run.py

for production deployment, look at the flask documentation.

## Requirements:

Most packages will be installed by the ./setup.sh script into a folder called .virtualenv,
but you will need Python 2.6/2.7 or so, and the Python headers package (python-dev on debian),
probably also a functioning gcc is needed, for compiling the various requirements.  But
python-dev should handle that (I hope!)

## More info:

The virtual env is kept in .virtualenv, and usually shouldn't need to be touched.  I don't like the entering and exiting a virtualenv business, so went with the 'virtualenv stuff happens transparently when you use run.py, you shouldn't have to care about it'.  If you want to run python for the virtualenv, use .virtualenv/bin/python

The setup.sh script is to allow you to get up an running on a new machine in seconds. (On an old machine, minutes, while it downloads and installs flask...)  I like the github idea of 'all a new developper needs to do is run one command, and they have a whole system ready to go'.

There is also an initial gunicorn running shell script.

Initial login credentials: `admin:password`

## pre-commit hook
There is the [pre-commit script by Sebastian Dahlgren](https://github.com/sebdah/git-pylint-commit-hook) in the .setup/hooks/ folder, which will run pylint on python scripts to check they are valid before you commit them. The setup.sh script will copy this into your .git/hooks by default.

To run a git commit *without* using this, use:

    git commit --no-verify


## Other notes

_(to be part of full documentation, later on)_

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
- Try refreshing the output screen...
