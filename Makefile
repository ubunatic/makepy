.PHONY: default clean dist backport install uninstall tox shell-test

include make/vars.mk

default: clean test

clean: pyclean; rm -rf .pytest_cache .cache dist build backport
	
# setup dependecies
install tox: dist
dist dev-install test: py-data
test: shell-test

# include generic targets
include make/project.mk
include make/tests.mk

# call makepy for project setup tasks
dist backport install tox: ; $(MAKEPY) $@

uninstall:
	$(MAKEPY) uninstall
	rm -rf *.egg-info

# add some CLI tests
shell-test:
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

IMG     = gcr.io/ubunatic/makepy
VOLUMES = -v $(CURDIR)/tests:/tests -v $(CURDIR)/examples:/examples
docker:
	docker build -t $(IMG) .
	docker run --rm $(VOLUMES) -it $(IMG) "/tests/test_examples.sh && /tests/test_init.sh"

GCF_BUCKET = ubunatic-functions
gcf-deploy:
	gcloud beta functions deploy subscribe --trigger-topic cloud-builds \
		--stage-bucket $(GCF_BUCKET) --source cloudbuild

gcf-call: ; gcloud beta functions call subscribe --data '{}'
gcf-logs: ;	gcloud beta functions logs read subscribe
gcf: gcf-deploy
	sleep 30; $(MAKE) gcf-call
	sleep 5;  $(MAKE) gcf-logs

include make/twine.mk
