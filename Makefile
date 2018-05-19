.PHONY: all clean datafiles test docker gcf

all: clean test         # define default target before anything else
include make/makepy.mk  # include all makepy vars and targets
clean: pyclean-all      # clean up anything

# re-build the in-line datafiles if changed using makepy:datafiles target
PY_DATAFILE := makepy/_datafiles.py
PY_MAKEFILE := makepy/_makefiles.py
DATAFILES   := setup.py .gitignore
MAKEFILES   := $(wildcard ./make/*)
datafiles: $(PY_DATAFILE) $(PY_MAKEFILE)
$(PY_DATAFILE): Makefile $(DATAFILES) ; $(MAKEPY) embed --debug -f -i $(DATAFILES) -o $@
$(PY_MAKEFILE): Makefile $(MAKEFILES) ; $(MAKEPY) embed --debug -f -i $(MAKEFILES) -o $@

# ensure datafiles are updated before running makepy or tests
$(MAKEPY_COMMANDS) test: $(SRC_FILES) datafiles

# setup makepy script-test
SCRIPT_TEST = tests/test_examples.sh && tests/test_makepy.sh
test: script-test

# define the docker image for gcr.io
IMG = gcr.io/ubunatic/makepy
docker: ; docker build -t $(IMG) .
docker-makepy:
	docker run --rm $(VOLUMES) -it $(IMG) "/tests/test_examples.sh && /tests/test_versions.sh"

# use gcr.io image for tests
TEST_IMG     = $(IMG)
TEST_VOLUMES = -v $(CURDIR)/tests:/tests -v $(CURDIR)/examples:/examples
docker-pypi:
	$(MAKE) docker-test PY=2
	$(MAKE) docker-test PY=3
docker-all: docker docker-pypi docker-makepy

# setup build status processors
GCF_BUCKET = ubunatic-functions
gcf-deploy:
	gcloud beta functions deploy subscribe --trigger-topic cloud-builds \
		--stage-bucket $(GCF_BUCKET) --source cloudbuild
gcf-call: ; gcloud beta functions call subscribe --data '{}'
gcf-logs: ;	gcloud beta functions logs read subscribe
gcf: gcf-deploy
	sleep 30; $(MAKE) gcf-call
	sleep 5;  $(MAKE) gcf-logs
gcs-upload:
	gsutil cp images/makepy-cli.gif gs://ubunatic-public/makepy/makepy-cli.gif

DEMO = docker run -it $(TEST_VOLUMES) -v $(CURDIR)/.vol:/tmp/prj $(IMG)
CMD  = 'bash -i'
.vol: ; mkdir .vol
docker-demo:  .vol; $(DEMO) 'cd /tmp/prj && rm -rf myapp && /tests/test_project.sh myapp'
docker-login: .vol; $(DEMO) $(CMD)

