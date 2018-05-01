include make/vars.mk

default: clean test

clean: pyclean; rm -rf .pytest_cache .cache dist build backport
	
# setup dependecies
install tox: dist
dist dev-install test: py-data
test: manual-tests

# include generic targets
include make/project.mk
include make/tests.mk

# call makepy for project setup tasks
dist backport install tox: ; $(MAKEPY) $@

uninstall:
	$(MAKEPY) uninstall
	rm -rf *.egg-info

# add some CLI tests
manual-tests:
	tests/test_examples.sh
	tests/test_init.sh

# re-build the in-line data files if changed
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

docker:
	docker build -t gcr.io/ubunatic/makepy .
	docker run --rm -it gcr.io/ubunatic/makepy /workspace/makepy/tests/test_examples.sh
	docker run --rm -it gcr.io/ubunatic/makepy /workspace/makepy/tests/test_init.sh

GCF_BUCKET = ubunatic-functions
gcf-deploy:
	gcloud beta functions deploy subscribe --trigger-topic cloud-builds \
		--stage-bucket $(GCF_BUCKET) --source cloudbuild
		
