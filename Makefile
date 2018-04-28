MAIN := makepy

include make/$(shell python -m makepy include)

test dist all: py-data

test: test-examples
test-examples: ; tests/test_examples.sh

PY_DATA_FILE  := makepy/__datafiles__.py
DATA_FILES    := setup.cfg setup.py .gitignore LICENSE.txt
py-data: $(PY_DATA_FILE)
$(PY_DATA_FILE): $(DATA_FILES) Makefile
	echo "# flake8:noqa=W191" > $@
	echo "from __future__ import unicode_literals" >> $@
	echo "data_files = {}"    >> $@
	for f in $(DATA_FILES); do \
		base=`basename $$f`; \
		var=`echo $$base | $(FILE2VAR)`; \
		echo "data_files['$$base'] = $$var =" '"""'; \
		cat $$f | sed 's#"""#\\"\\"\\"#g'; \
		echo '"""'; \
	done >> $@

