#!/bin/sh

xset s off # no screensaver
xset -dpms # no display power saving
xset s noblank # no screensaver blanking
unclutter & # hide the mousepointer

chromium-browser --start-fullscreen --bwsi --disable-extensions --disable-default-apps --app='http://localhost:8080/'
