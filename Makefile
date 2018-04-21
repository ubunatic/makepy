MAIN := pimpy

include project.mk

test dist all: py-data

PY_DATA_FILE  := pimpy/__datafiles__.py
DATA_FILES    := project.mk setup.cfg .gitignore LICENSE.txt
py-data: $(PY_DATA_FILE)
$(PY_DATA_FILE): $(DATA_FILES) Makefile
	echo "# flake8:noqa=W191" > $@
	echo "from __future__ import unicode_literals" >> $@
	echo "data_files = {}"    >> $@
	for f in $(DATA_FILES); do \
		var=`echo $$f | $(FILE2VAR)`; \
		echo "data_files['$$f'] = $$var =" '"""'; \
		cat $$f; \
		echo '"""'; \
	done >> $@

