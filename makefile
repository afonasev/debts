CODE = server tests alembic
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

new_migration:
ifeq ($(m),)
	@echo 'Message (m) argument is missing!'
else
	$(DOCKER_RUN) alembic revision --autogenerate --message "$(m)"
endif

_test:
	pytest --verbosity=2 --showlocals --strict --cov=$(CODE) $(args)

_lint:
	flake8 --jobs 4 --statistics --show-source $(CODE)
	pylint --jobs 4 --rcfile=setup.cfg $(CODE)
	mypy $(CODE)
	black --target-version=py37 --skip-string-normalization --line-length=79 --check $(CODE)
	pytest --dead-fixtures --dup-fixtures

_pretty:
	isort --apply --recursive $(CODE)
	black --target-version=py37 --skip-string-normalization --line-length=79 $(CODE)
	unify --in-place --recursive $(CODE)

precommit_install:
	git init
	echo '#!/bin/sh\nmake lint test\n' > .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
