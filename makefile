CODE = server
DOCKER_RUN = docker-compose run --rm server

init:
	python3 -m venv .venv
	poetry install

up:
	docker-compose up

test:
	$(DOCKER_RUN) make _test args="$(args)"

lint:
	$(DOCKER_RUN) make _lint

pretty:
	$(DOCKER_RUN) make _pretty

repl:
	$(DOCKER_RUN) ipython

_test:
	pytest --verbosity=2 --showlocals --strict --cov=$(CODE) $(args)

_lint:
	flake8 --jobs 4 --statistics --show-source $(CODE) tests
	pylint --jobs 4 --rcfile=setup.cfg $(CODE)
	mypy $(CODE) tests
	black --target-version=py37 --skip-string-normalization --line-length=79 --check $(CODE) tests
	pytest --dead-fixtures --dup-fixtures

_pretty:
	isort --apply --recursive $(CODE) tests
	black --target-version=py37 --skip-string-normalization --line-length=79 $(CODE) tests
	unify --in-place --recursive $(CODE) tests

precommit_install:
	git init
	echo '#!/bin/sh\nmake lint test\n' > .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
