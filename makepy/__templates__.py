from __future__ import unicode_literals

templates = {}

templates['tox.ini'] = tox_ini = """
[tox]
{envline}
skipsdist = True

[testenv]
deps =
    pytest
    flake8
    future

commands = make dist-install {{posargs:lint dist-test}}
whitelist_externals = make
"""

templates['Makefile'] = Makefile = """
MAIN         := {MAIN}
TEST_SCRIPTS := {MAIN} -h
include project.mk
"""

templates['__init__.py'] = __init___py = """
# {flake_rules}
__version__ = '0.0.1'
__tag__     = 'py3'
""".format(flake_rules = 'flake8: noqa: F401')

templates['README.md'] = README_md = """
{NEW_PRJ}
=========

Install via `pip install {NEW_PRJ}`. Then run the program:

    {NEW_PRJ} --help       # show help
    {NEW_PRJ}              # run with defaults

{COPY_INFO}
"""

templates['project.cfg'] = project_cfg = """
# project.cfg contains all custom parameters required by setup.py
# to install the package and to build the dist files

[author]
name        = {NAME}
email       = {EMAIL}
github_name = {GITHUB_NAME}

[project]
license     = MIT  # if changed, also update the classifiers
description = {PROJECT}: My pimped project
name        = {PROJECT}
main        = {PROJECT}

# 3 - Alpha, 4 - Beta, 5 - Production/Stable
status = Development Status :: 3 - Alpha

# see: https://packaging.python.org/en/latest/requirements.html
requires = typing future
keywords = application cli

# see: https://pypi.python.org/pypi?%3Aaction=list_classifiers
classifiers =
\tTopic :: Software Development :: Libraries
\tIntended Audience :: Developers
\tLicense :: OSI Approved :: MIT License

[scripts]
{PROJECT} = {PROJECT}:main

[python]
# used as additional `requires`
# backport_deps =
# default_deps  =

# used to generate Python classifiers
default           = 3 3.3 3.4 3.5 3.6
backport          = 2 2.6 2.7

# used as python_requires
backport_requires = >=2.6, <3
default_requires  = >=3.3'
"""
