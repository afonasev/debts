CODE = server tests alembic
DOCKER = docker-compose run --rm server

init:
	python3 -m venv .venv
	poetry install

up:
	docker-compose up

test:
	$(DOCKER) make _test args="$(args)"

lint:
	$(DOCKER) make _lint

pretty:
	$(DOCKER) make _pretty

repl:
	$(DOCKER) ipython

new_migration:
ifeq ($(m),)
	@echo 'Message (m) argument is missing!'
else
	$(DOCKER_RUN) alembic revision --autogenerate --message "$(m)"
endif

_test:
	pytest --verbosity=2 --showlocals --strict --log-level=DEBUG --cov=$(CODE) $(args)

_lint:
	flake8 --jobs=4 --statistics --show-source $(CODE)
	pylint --rcfile=setup.cfg $(CODE)
	mypy $(CODE)
	black --skip-string-normalization --check $(CODE)
	pytest --dead-fixtures --dup-fixtures

_pretty:
	isort --apply --recursive $(CODE)
	black --skip-string-normalization $(CODE)
	unify --in-place --recursive $(CODE)

precommit_install:
	git init
	echo '#!/bin/sh\nmake lint test\n' > .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
