# Generic Python Project Make-Include File
# ========================================
# Copy these mk-files to your python project for
# easy testing, building, and publishing.
#
# (c) Uwe Jugel, @ubunatic, License: MIT
#
# Integration and Usage
# ---------------------
# Simply `include make/vars.mk` and ´include make/project.mk´ in your `Makefile`.
# Now you can use `make vars`, `make pyclean`, and `make dev-install`.

# Targets
# -------
# vars:        print all relevant vars
# pyclean:     remove pyc and other cached files
# dev-install: directly use the current source as installation

.PHONY: vars pyclean dev-install

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
	# WHEELTAG  $(WHEELTAG)
	#
	# SETUP_DIR $(SETUP_DIR)
	# SRC_FILES $(SRC_FILES)
	# PRJ_TESTS $(PRJ_TESTS)
	#
	# Python Versions
	# ---------------
	# python: $(shell python    --version 2>&1)
	# PYTHON: $(shell $(PYTHON) --version 2>&1)

pyclean:
	pyclean . || true  # try to use system pyclean if available
	find . -name '*.py[co]'    -delete
	find . -name '__pycache__' -delete

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

