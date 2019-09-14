PYTHON='./.virtualenv/bin/python3'
PIP='./.virtualenv/bin/pip'

ALL: .virtualenv deps

.virtualenv:
	python3 -m venv .virtualenv

deps: requirements.txt
	$(PIP) install -Ur requirements.txt

test:
	$(PYTHON) streetsign/manage.py test
