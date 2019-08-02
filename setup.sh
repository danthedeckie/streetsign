#!/bin/bash

command -v make >/dev/null 2>&1 || { echo >&2 "I need 'make' to be installed."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo >&2 "I need 'python3' to be installed."; exit 1; }

make all
