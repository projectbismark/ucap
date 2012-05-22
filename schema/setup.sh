#!/usr/bin/env bash
DB=$1

VER=8.4
CONTRIB_DIR=/usr/share/postgresql/$VER/contrib

createlang plpgsql $DB

#contrib="pgcrypto.sql"
for f in $contrib;
do
	psql -f $CONTRIB_DIR/$f $DB
done

FILES="functions.sql tables.sql"

for f in $FILES;
do
	psql -f $f $DB
done
