_INSTRUCTIONS:
	echo 'make all, or make clean.'

clean:
	rm -rf .v/
	rm config.py

all: requirements.txt .virtualenv config.py database.db

.virtualenv: requirements.txt
	python3 -m venv .virtualenv
	./.virtualenv/bin/pip install -r requirements.txt

config.py:
	python3 .setup/make_initial_config_file.py > config.py

database.db:
	echo 'make()' | ./.virtualenv/bin/python3 -i db.py

requirements.txt: requirements_raw.txt
	echo '# This file is generated from requirements_raw.txt.' > requirements.txt
	./.virtualenv/bin/pip freeze -r requirements_raw.txt >> requirements.txt

