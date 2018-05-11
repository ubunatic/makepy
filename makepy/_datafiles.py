# flake8:noqa=W191
from __future__ import unicode_literals
files = {}
dirs  = set()

files['setup.cfg'] = setup_cfg = """
[bdist_wheel]
universal=0

[metadata]
license_file = LICENSE.txt

[flake8]
ignore = E402,E301,E302,E501,E305,E221,W391,E401,E241,E701,E231,E704,E251,E271,E272,E702,E226,E306,E201,E902,E722,E741
exclude = ./backport .tox build
"""

files['setup.py'] = setup_py = """
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
.vol
"""
