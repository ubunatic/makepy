# Generic Python Project Makefile
# ===============================
# Copy this file to each of python project to be able to test,
# build, and publish it easily.
#
# (c) Uwe Jugel, @ubunatic, License: MIT
#
# Integration and Usage
# ---------------------
# Simply `include project.mk` in your `Makefile`.
# Then add your common targets, such as `test`, `docker-test`, etc.
# Now you can use `make`, `make test`, `make install`, etc.
# See each target for more details.
#
# Notes
# -----
# - All `_lower_case` vars are internal vars not supposed to be overwritten.
# - Try not to change this file to fit it your project's needs. Try to handle
#   all custom building in your main `Makefile`.
#

.PHONY: defaul all test base-test clean install publish test-publish sign \
	docker-test docker-base-test clone build dist

# The default project name is the name of the current dir. All code usually
# resides in another subdir (package) with the same name as the project.
PKG       ?= $(shell basename $(CURDIR))
# The default tests dir is 'tests'.
# Use PRJ_TEST = other1 other2 in your Makefile to override.
PRJ_TESTS ?= $(shell if test -e tests; then echo tests; fi)
# We use regard project files as source files to trigger rebuilds, etc.
PRJ_FILES := tox.ini setup.py project.mk setup.cfg project.cfg Makefile LICENSE.txt README.md
SRC_FILES := $(PKG) $(PRJ_TESTS) $(PRJ_FILES)

# main python vars, defining python and pip binaries
_GET_MAJOR = 'import sys; sys.stdout.write(str(sys.version_info.major) + "\n")'
_GET_MINOR = 'import sys; sys.stdout.write(str(sys.version_info.minor) + "\n")'
PY     := $(shell python -c $(_GET_MAJOR)).$(shell python -c $(_GET_MINOR))
PYTHON := python$(PY)
PIP    := $(PYTHON) -m pip
NOL    := 1>/dev/null  # mute stdout
NEL    := 2>/dev/null  # mute stderr

# export an define setup vars, used for dist building
export PY_TAG := py$(shell $(PYTHON) -c $(_GET_MAJOR))
WHEEL  := `find dist -name '$(PKG)*$(PY_TAG)*.whl'`
ifeq ($(PY_TAG), py2)
SETUP_DIR := backport
else
SETUP_DIR := $(CURDIR)
endif

# The main module of the project is usually the same as the main package of the project.
# Make sure the setup the __init__.py correctly. We can then use the module to setup
# generic import and cli tests. Override the following vars as needed.
MAIN        = $(PKG)
CLI_TEST    = $(PYTHON) -m $(MAIN) -h $(NOL)
IMPORT_TEST = $(PYTHON) -c "import $(MAIN) as m; print(\"version:\",m.__version__,\"tag:\",m.__tag__)"
DIST_TEST   = $(IMPORT_TEST); $(CLI_TEST); $(TEST_SCRIPTS)
DOCKER_CLI_TEST = pip install $(PKG); $(DIST_TEST)
BASH_INIT   = set -o errexit; export TERM=xterm;
PIMPY      := python -m pimpy
FILE2VAR    = sed 's/[^A-Za-z0-9_]\+/_/g'

# The default target runs a clean tests in the default environment.
# Use PY=3 or PY=2 to switch environments.
default: clean tox

# The `test` target depends on `base-test` to trigger import tests, cli tests, and linting.
# To setup yor own linting and tests,  please override the `test` and `lint` targets.
test: lint base-test
lint: vars ; $(PYTHON) -m flake8 $(SETUP_DIR)

# As a quick tox test, we run tox using the current environment.
tox: ; $(PIMPY) -e $(PY_TAG)

# Printing make vars can be helpful when testing multiple Python versions.
vars:
	# Make Variables
	# --------------
	# CURDIR    $(CURDIR)
	# PKG       $(PKG)
	# PY        $(PY)
	# PY_TAG    $(PY_TAG)
	# PYTHON    $(PYTHON)
	# PIP       $(PIP)
	# SETUP_DIR $(SETUP_DIR)
	#
	# Python
	# ------
	# python: $(shell python    --version 2>&1)
	# PYTHON: $(shell $(PYTHON) --version 2>&1)

# Generic tests are included when running `make test`.
base-test: $(SRC_FILES) vars lint
	# lint and test the project (PYTHONPATH = $(PYTHONPATH))
	pyclean .
	$(IMPORT_TEST)
	$(PYTHON) -m pytest -xv $(PRJ_TESTS)
	$(CLI_TEST)

script-test:
	bash -it -c '$(BASH_INIT) $(TEST_SCRIPTS)' $(NOL)

clean:
	pyclean . || true
	$(PIMPY) clean
	rm -rf .pytest_cache .cache dist build backport *.egg-info

dev-install: $(SETUP_DIR)
	# Directly install $(PKG) in the local system. This will link your installation
	# to the code in this repo for quick and easy local development.
	cd $(SETUP_DIR) && $(PIP) install --user -e .
	#
	# source installation
	# -------------------
	$(PIP) show $(PKG)
	@test $(SETUP_DIR) != backport || echo '### Attention ###' \
		'\nInstalled $(PKG) backport!' \
		'\nYou must run `make backport` to update the installation' \
		'\n### Attention ###'

backport: $(SRC_FILES)
	$(PIMPY) backport -p $(PKG) -s $(SRC_FILES) -m $(MAIN)

dist: $(SETUP_DIR) $(SRC_FILES)
	# build dist and backport dist
	cd $(SETUP_DIR) && $(PYTHON) setup.py bdist_wheel -q -d $(CURDIR)/dist
	test -f "$(WHEEL)"

# use default pip and python to safely install the project in the system
dist-install: dist; pip install $(WHEEL)
dist-uninstall:   ; pip uninstall -y $(PKG) || true
dist-reinstall: dist-uninstall dist-install
# override dist-test to add your own dist tests (used for tox testing)
dist-test: dist-base-test
dist-base-test:
	cd tests && python -m pytest -x .
	cd /tmp && bash -it -c '$(BASH_INIT) $(DIST_TEST)' $(NOL)

install: dist-reinstall
uninstall: ; $(PIMPY) uninstall --pkg $(PKG)

dists:
	rm -rf dist; mkdir -p dist
	$(MAKE) dist PY=2
	$(MAKE) dist

sign: dist
	# sign the dist with your gpg key
	gpg --detach-sign -a dist/*.whl

test-publish: test dist
	# upload to testpypi (needs valid ~/.pypirc)
	twine upload --repository testpypi dist/*

publish: test dist sign
	# upload to pypi (requires pypi account)
	twine upload --repository pypi dist/*

docker-base-test:
	# after pushing to pypi you want to check if you can pull and run
	# in a clean environment. Safest bet is to use docker!
	docker run -it python:$(PY) bash -it -c '$(BASH_INIT) $(DOCKER_CLI_TEST)'

# This default `docker-test` target runs basic import and script tests.
# Please override this target as needed.
docker-test: docker-base-test
