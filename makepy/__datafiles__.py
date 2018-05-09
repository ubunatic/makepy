# flake8:noqa=W191
from __future__ import unicode_literals
datafiles = {}
datadirs = set()
datafiles['setup.cfg'] = setup_cfg = """
[bdist_wheel]
universal=0

[metadata]
license_file = LICENSE.txt

[flake8]
ignore = E402,E301,E302,E501,E305,E221,W391,E401,E241,E701,E231,E704,E251,E271,E272,E702,E226,E306,E201,E902,E722,E741
exclude = ./backport .tox build
"""
datafiles['setup.py'] = setup_py = """
#!/usr/bin/env python
# NOTE: This is a generated, generic setup.py, produced by `makepy init`.
#       Try to customize project.cfg first, before editing this file.

from __future__ import absolute_import

import os, sys
from setuptools import setup, find_packages

try: from makepy.project import load_project   # Try to use makepy module from current env.
except ImportError:
    sys.path.append(os.environ['MAKEPYPATH'])  # Fallback to first available system makepy.
    from makepy.project import load_project    # Usage: MAKEPYPATH=`makepy path` python ...

def run_setup():
    kwargs = load_project('project.cfg')
    kwargs['packages'] = find_packages(exclude=['contrib', 'docs', 'tests'])
    setup(**kwargs)

if __name__ == '__main__': run_setup()
"""
datafiles['.gitignore'] = _gitignore = """
.cache
build
dist
*.egg-info
.asc
transpiled
backport
.pytest_cache
.tox
__pycache__
*.pyc
*.pyo
"""
datadirs.add('make')
datafiles['make/vars.mk'] = make_vars_mk = """
# Generic Python Project Make-Include File
# ========================================
# Copy these mk-files to your python project for easy testing, building, and publishing.
#
# (c) Uwe Jugel, @ubunatic, License: MIT
#
# Integration and Usage
# ---------------------
# Simply `include make/makepy.mk` to include all mk files in your `Makefile`.
# Now you can use `make vars`, `make pyclean`, and `make dev-install`.

# This mk file defines the most common vars for building Python projects.
# Run `make PY=2` or `make PY=3` to setup vars for either Python 2 or 3.

# Using PYTHONPATH leads to unpredicted behavior.
unexport PYTHONPATH

# The default project name is the name of the current dir. All code usually
# resides in another subdir (package) with the same name as the project.
PKG  = $(notdir $(basename $(CURDIR)))
MAIN = $(PKG)

# main python vars, defining python and pip binaries
_GET_MAJOR = 'import sys; sys.stdout.write(str(sys.version_info.major) + "\n")'
_GET_MINOR = 'import sys; sys.stdout.write(str(sys.version_info.minor) + "\n")'
PY     := $(shell python -c $(_GET_MAJOR)).$(shell python -c $(_GET_MINOR))
PYTHON = python$(PY)
PIP    = $(PYTHON) -m pip
MAKEPY = $(PYTHON) -m makepy

# export and define setup vars, used for dist building
export WHEELTAG := py$(shell $(PYTHON) -c $(_GET_MAJOR))
ifeq ($(WHEELTAG), py2)
SETUP_DIR = backport
else
SETUP_DIR = $(CURDIR)
endif

# The default tests dir is 'tests'.
# Use PRJ_TESTS = other1 other2 in your Makefile to override.
PRJ_TESTS = $(wildcard ./tests)
# We use regard project files as source files to trigger rebuilds, etc.
PRJ_FILES = tox.ini setup.py setup.cfg project.cfg Makefile LICENSE.txt README.md
SRC_FILES = $(PKG) $(PRJ_TESTS) $(PRJ_FILES)

# utils and help vars
NOL       = 1>/dev/null  # mute stdout
NEL       = 2>/dev/null  # mute stderr
FILE2VAR  = sed 's/[^A-Za-z0-9_]\+/_/g'

"""
datadirs.add('make')
datafiles['make/tests.mk'] = make_tests_mk = """
# Generic Python Project Make-Include File
# ========================================
# Copy these mk-files to your python project for easy testing, building, and publishing.
#
# (c) Uwe Jugel, @ubunatic, License: MIT
#
# Integration and Usage
# ---------------------
# Simply `include make/makepy.mk` to include all mk files in your `Makefile`.
# Now you can use `make vars`, `make pyclean`, and `make dev-install`.

.PHONY: test lint base-test script-test dist-test docker-test

# The main module of the project is usually the same as the main package of the project.
# Make sure the setup the __init__.py correctly. We can then use the module to setup
# generic import and cli tests. Override the following vars as needed.
CLI_TEST     = $(PYTHON) -m $(MAIN) -h $(NOL)
IMPORT_TEST  = $(PYTHON) -c "import $(MAIN) as m; print(\"version:\",m.__version__,\"tag:\",m.__tag__)"
DIST_TEST    = $(IMPORT_TEST); $(CLI_TEST)
BASH         = bash -it -o errexit -c

# The `test` target depends on `base-test` to trigger import tests, cli tests, and linting.
# To setup yor own linting and tests, please override the `test` and `lint` targets.
test: lint base-test
lint: vars ; $(MAKEPY) lint

# Generic tests included when running `make test`.
base-test: $(SRC_FILES) pyclean vars lint
	$(IMPORT_TEST)
	$(MAKEPY) test --tests $(PRJ_TESTS)
	$(CLI_TEST)

# Test the installed package scripts (CLI tools of the package)
SCRIPT_TEST = echo "please set SCRIPT_TEST = <shell-script-code> to run script tests"
script-test:
	$(BASH) '$(SCRIPT_TEST)' $(NOL)

# run tests using default pip and python outside of the project
dist-test:
	cd tests && python -m pytest -x .
	cd /tmp && $(BASH) '$(DIST_TEST)' $(NOL)

# After pushing to PyPi, you want to check if you can pull and run
# your package in a clean environment. Safest bet is to use docker!
TEST_IMG     = python:$(PY)
TEST_VOLUMES = -v $(CURDIR)/tests:/tests
docker-test:
	docker run -it $(TEST_VOLUMES) $(TEST_IMG) $(BASH) 'pip install $(PKG); $(DIST_TEST)'

"""
datadirs.add('make')
datafiles['make/project.mk'] = make_project_mk = """
# Generic Python Project Make-Include File
# ========================================
# Copy these mk-files to your python project for easy testing, building, and publishing.
#
# (c) Uwe Jugel, @ubunatic, License: MIT
#
# Integration and Usage
# ---------------------
# Simply `include make/makepy.mk` to include all mk files in your `Makefile`.
# Now you can use `make vars`, `make pyclean`, and `make dev-install`.

# Targets
# -------
# vars:    print all relevant vars
# pyclean: remove pyc and other cached files
# copy:    copy all mk files to a new project

.PHONY: vars pyclean pyclean-all copy datafile

# Printing make vars can be helpful when testing multiple Python versions.
vars:
	# Make Variables
	# --------------
	# CURDIR    $(CURDIR)
	# PKG       $(PKG)
	# MAIN      $(MAIN)
	#
	# PY        $(PY)
	# PYTHON    $(PYTHON)
	# PIP       $(PIP)
	# MAKEPY    $(MAKEPY)
	# WHEELTAG  $(WHEELTAG)
	#
	# SETUP_DIR $(SETUP_DIR)
	# SRC_FILES $(SRC_FILES)
	# PRJ_TESTS $(PRJ_TESTS)
	#
	# Python/Pip Versions
	# ---------------
	# python: $(shell python    --version 2>&1)
	# PYTHON: $(shell $(PYTHON) --version 2>&1)
	# pip:    $(shell pip       --version 2>&1)
	# PIP:    $(shell $(PIP)    --version 2>&1)

pyclean:
	pyclean . || true  # try to use system pyclean if available
	find . -name '*.py[co]'    -delete
	find . -name '__pycache__' -delete

pyclean-all: pyclean
	rm -rf .pytest_cache .cache dist build backport

copy:
	test -n "$(TRG)"           # ensure the copy target TRG is set
	mkdir -p $(TRG)/make       # create TRG/make dir in target dir
	cp make/*.mk $(TRG)/make/  # copy all mk files to TRG/make

# TODO: move datafile generation to makepy
# use the datafile target to concat plain text files into
# a python file (useful for templating, etc.)
PY_DATAFILE = $(PKG)/__datafiles__.py
DATA_FILES  = $(wildcard ./datafiles)
datafile: $(PY_DATAFILE)
$(PY_DATAFILE): $(DATA_FILES) Makefile make/project.mk
	test -n "$(PY_DATAFILE)"  # ensure the target PY_DATAFILE is set
	test -n "$(DATA_FILES)"   # ensure some DATA_FILES are defined
	echo "# flake8:noqa=W191"                      >  $@
	echo "from __future__ import unicode_literals" >> $@
	echo "datafiles = {}"                          >> $@
	echo "datadirs = set()"                        >> $@
	for f in $(DATA_FILES); do \
		dir=`dirname $$f`; dir=`basename $$dir` \
		base=`basename $$f`; \
		if test "$$dir" = "." -o -z "$$dir"; \
		then dir="";      psep="";  vsep=""; \
		else dir="$$dir"; psep="/"; vsep="_"; echo "datadirs.add('$$dir')"; \
		fi; \
		var=`echo "$$dir$$vsep$$base" | $(FILE2VAR)`; \
		echo "datafiles['$$dir$$psep$$base'] = $$var =" '\"\"\"'; \
		cat $$f | sed 's#\"\"\"#\\"\\"\\"#g'; \
		echo '\"\"\"'; \
	done                                           >> $@
"""
datadirs.add('make')
datafiles['make/twine.mk'] = make_twine_mk = """
# Generic Python Project Make-Include File
# ========================================
# Copy these mk-files to your python project for easy testing, building, and publishing.
#
# (c) Uwe Jugel, @ubunatic, License: MIT
#
# Integration and Usage
# ---------------------
# Simply `include make/makepy.mk` to include all mk files in your `Makefile`.
# Now you can use `make vars`, `make pyclean`, and `make dev-install`.

# This file includes twine targets for publishing a package to PyPi.

.PHONY: sign test-publish tag publish

sign:
	# sign the dist with your gpg key
	gpg --detach-sign -a dist/*.whl

test-publish:
	# upload to testpypi (needs valid ~/.pypirc)
	twine upload --repository testpypi dist/*

# TODO: add release note support
tag: bumpversion clean dists
	git add $(PKG)/__init__.py
	git commit -m "bump version"
	git tag v$(shell $(MAKEPY) version)

# TODO: add support for universal wheels
PY2_WHEEL = $(shell find dist -name '$(PKG)*py2-none-any*.whl')
PY3_WHEEL = $(shell find dist -name '$(PKG)*py3-none-any*.whl')
publish: sign
	# upload to pypi (requires pypi account)
	# p3-wheel: $(PY3_WHEEL)
	# p2-wheel: $(PY2_WHEEL)
	@read -p "start upload (y/N)? " key && test "$$key" = "y"
	twine upload --repository pypi $(PY3_WHEEL) $(PY2_WHEEL)

"""
datadirs.add('make')
datafiles['make/makepy.mk'] = make_makepy_mk = """
# Generic Python Project Make-Include File
# ========================================
# Copy these mk-files to your python project for easy testing, building, and publishing.
#
# (c) Uwe Jugel, @ubunatic, License: MIT
#
# Integration and Usage
# ---------------------
# Simply `include make/makepy.mk` to include all mk files in your `Makefile`.
# Now you can use `make vars`, `make pyclean`, and `make dev-install`.

# This file provides targets that wrap the most common makepy commands, so that you
# can call makepy commands and custom targets together: `make <makepy-command> <custom-target>`.
# It also includes all other mk files so that you only need to `include make/makepy.mk`

.PHONY: dists install dev-install tox bumpversion version

include make/vars.mk

ifeq ($(WHEELTAG), py2)
TEST_DEP=backport
endif
test: $(TEST_DEP)

include make/project.mk
include make/tests.mk
include make/twine.mk

# passthrough makepy commands
MAKEPY_COMMANDS = dist backport dists install dev-install tox bumpversion version
$(MAKEPY_COMMANDS): ; $(MAKEPY) $@

# TODO: handle egg removal in makepy
uninstall: ; $(MAKEPY) uninstall && rm -rf *.egg-info


"""
