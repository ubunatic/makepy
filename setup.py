#!/usr/bin/env python
# NOTE: This is a generated, generic setup.py, produced by `makepy init`.
#       Try to customize the [makepy] section in setup.cfg first, before editing this file.

from __future__ import absolute_import

from setuptools import setup, find_packages
from makepy.project import read_setup_args

def run_setup():
    kwargs = read_setup_args()
    ns = kwargs.get('ns', '.')
    packages = find_packages(ns, exclude=['contrib', 'docs', 'tests', 'backport', 'vendor'])
    if ns != '.': packages = ['{}.{}'.format(ns, p) for p in packages]
    kwargs['packages'] = packages
    setup(**kwargs)

if __name__ == '__main__': run_setup()
