#!/usr/bin/env python
# NOTE: This is a generated, generic setup.py, produced by `makepy init`.
#       Try to customize the [makepy] section in setup.cfg first, before editing this file.

from __future__ import absolute_import

import os, sys
from setuptools import setup, find_packages

try: from makepy.project import read_setup_args  # Try to use makepy module from current env.
except ImportError:
    sys.path.append(os.environ['MAKEPYPATH'])    # Fallback to first available system makepy.
    from makepy.project import read_setup_args   # Usage: MAKEPYPATH=`makepy path` python ...

def run_setup():
    kwargs = read_setup_args()
    kwargs['packages'] = find_packages(exclude=['contrib', 'docs', 'tests', 'backport'])
    setup(**kwargs)

if __name__ == '__main__': run_setup()
