#!/bin/bash

source .virtualenv/bin/activate

gunicorn -w 4 streetsign_server:app
