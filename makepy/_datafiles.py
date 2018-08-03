# flake8:noqa=W191
from __future__ import unicode_literals
files = {}
dirs  = set()

files['setup.py'] = setup_py = """
#!/usr/bin/env python
from __future__ import absolute_import

# NOTE: This is a generated, generic setup.py, produced by `makepy init`.
#       Try to customize the [makepy] section in setup.cfg first, before editing this file.
from setuptools import setup
from makepy.project import read_setup_args
if __name__ == '__main__': setup(**read_setup_args())
"""

files['.gitignore'] = _gitignore = """
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
*.pyd
*.py-e
.vol
"""
