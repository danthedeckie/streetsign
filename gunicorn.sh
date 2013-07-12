#!/bin/bash

source .virtualenv/bin/activate

gunicorn -w 4 app:app
