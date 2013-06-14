# Flask Bootstrap
An incredibly simple flask 'initial application' which has basic stuff set up
so it's ready to go.

## Including:

- setup.sh (run this, and sets up everything). Can be run as often as you wish.
- autogenerates a basic SECRET KEY in the config.
- virtualenv 1.9.1 (in it's own .virtualenv folder, out of the way)
- pylint pre-commit hook (from Sebastian Dahlgren)

## Usage:

clone this into the directory you want to use for the project, and type

    ./setup.sh

and you're going!

To run the app with the flask autoreloading magic use

    ./run.py

for production deployment, look at the flask documentation.

## More info:

A lot of the ideas here were inspired by the [Flask Mega Tutorial by Miguel Grinberg.](http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world).

The virtual env is kept in .virtualenv, and usually shouldn't need to be touched.  I don't like the entering and exiting a virtualenv business, so went with the 'virtualenv stuff happens transparently when you use run.py, you shouldn't have to care about it'.  If you want to run python for the virtualenv, use .virtualenv/bin/python

The setup.sh script is to allow you to get up an running on a new machine in seconds. (On an old machine, minutes, while it downloads and installs flask...)  I like the github idea of 'all a new developper needs to do is run one command, and they have a whole system ready to go'.

## pre-commit hook
There is the [pre-commit script by Sebastian Dahlgren](https://github.com/sebdah/git-pylint-commit-hook) in the .setup/hooks/ folder, which will run pylint on python scripts to check they are valid before you commit them. The setup.sh script will copy this into your .git/hooks by default.

To run a git commit *without* using this, use:

    git commit --no-verify
