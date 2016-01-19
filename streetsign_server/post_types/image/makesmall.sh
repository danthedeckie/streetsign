#!/bin/bash

convert "$1" -resize 1280x\> "$1"

exit $?
