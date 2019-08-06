ALL: .virtualenv deps

.virtualenv:
	python3 -m venv .virtualenv

deps: requirements.txt
	. .virtualenv/bin/activate; pip install -Ur requirements.txt

