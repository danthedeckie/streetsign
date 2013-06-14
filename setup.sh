#!/bin/bash
# setup.sh - useful script for getting a virtualenv etc all set up.
#
####################################################
# Config:

VDIR=.virtualenv
SDIR=.setup
PYTHON=$VDIR/bin/python
PIP=$VDIR/bin/pip

# You shouldn't need to change these...
VIRTUALENV_VERSION=1.9.1

VIRTUALENV="$VDIR/virtualenv-$VIRTUALENV_VERSION/virtualenv.py"

####################################################
# Actually start doing stuff:

# with clean command, remove old virtualenv
if [[ "$1" == "clean" ]]; then
    echo "Removing Old VirtualEnv"
    rm -rf "$VDIR"
    # if "./setup.sh clean only", quit after cleaning.
    [[ "$2" == "only" ]] && exit 0
fi

# if the .virtualenv folder doesn't exist, make it
if [[ ! -d "$VDIR" ]]; then
    echo "Making new folder ($VDIR) for virtualenv to live in."
    mkdir "$VDIR"
fi

# extract virtualenv.py if we need it
if [[ ! -f "$VIRTUALENV" ]]; then
    PACKAGE="virtualenv-1.9.1.tar.gz"
    echo "Downloading VirtualEnv ($VIRTUALENV_VERSION)"
    curl "https://pypi.python.org/packages/source/v/virtualenv/$PACKAGE" -o "$VDIR/$PACKAGE"
    if [[ $? -ne 0 ]]; then
        echo 'Download Failed!'
        exit 1
    fi
    echo "Extracting VirtualEnv..."
    tar -zxC "$VDIR" -f "$VDIR/$PACKAGE"
fi

# if there's no python in virtualenv, make one:
[[ -f "$PYTHON" ]] || python "$VIRTUALENV" "$VDIR"

# get required python modules:
echo "Checking requirements (python modules)"
$PIP install -r "requirements.txt"
if [[ $? -ne 0 ]]; then
    echo 'Something went wrong trying to install the required python modules...'
    exit 2
fi

# If no config.py, auto generate one:
if [[ ! -f 'config.py' ]]; then
    python .setup/make_initial_config_file.py > 'config.py'
fi

# setup standard hooks.
if [[ ! -e ".git/hooks/pre-commit" ]]; then
    cp .setup/hooks/pre-commit .git/hooks/pre-commit
fi
echo
echo "--------------------------------------------------------"
echo "Everything is done! You should be able to use ./run.sh to run the development server."
