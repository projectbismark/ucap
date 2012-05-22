DB:=$(USER)

all: create

create:
	createdb $(DB)
	./setup.sh $(DB)

createall: clean create test
    
tables:

indexes:

functions:
	psql -f functions.sql $(DB)

export:

import:

verify:
	psql -f dummy-mine.sql $(DB)

clean:
	dropdb $(DB)
