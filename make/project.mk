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
		echo "datafiles['$$dir$$psep$$base'] = $$var =" '"""'; \
		cat $$f | sed 's#"""#\\"\\"\\"#g'; \
		echo '"""'; \
	done                                           >> $@
