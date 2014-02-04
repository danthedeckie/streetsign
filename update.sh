#!/bin/bash

BU="$(date +%Y-%h-%d-%H-%S)"

if [[ -f "database.$BU" ]]; then
    echo "there is already a database.backup file..."
    exit 1
fi

cp database.db database.$BU

sqlite3 database.db ".schema externalsource" |grep 'display_time' > /dev/null

if [[ $? -ne 0 ]]; then
    echo "adding 'display_time' column to externalsource table."
    sqlite3 database.db "alter table externalsource add column display_time integer not null"
fi

echo "Done."
