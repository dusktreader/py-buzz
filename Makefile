.ONESHELL:
.DEFAULT_GOAL:=help
SHELL:=/bin/bash
PACKAGE_NAME:=buzz

.PHONY: install
install:
	poetry install

.PHONY: test
test: install
	poetry run pytest

.PHONY: mypy
mypy: install
	poetry run mypy ${PACKAGE_NAME} --pretty

.PHONY: lint
lint: install
	poetry run black --check ${PACKAGE_NAME}
	poetry run isort --check ${PACKAGE_NAME}
	poetry run flake8 ${PACKAGE_NAME}

.PHONY: qa
qa: test lint mypy
	echo "All quality checks pass!"

.PHONY: format
format: install
	poetry run black ${PACKAGE_NAME}
	poetry run isort ${PACKAGE_NAME}

.PHONY: clean
clean:
	@find . -iname '*.pyc' -delete
	@find . -iname '*.pyo' -delete
	@find . -iname '*~' -delete
	@find . -iname '*.swp' -delete
	@find . -iname '__pycache__' -delete
	@rm -r .mypy_cache
	@rm -r .pytest_cache
	@find . -name '*.egg' -print0|xargs -0 rm -rf --
	@rm -rf .eggs/
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info
