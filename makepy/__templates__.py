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

commands = makepy install {{posargs:lint test}}
whitelist_externals = makepy
"""

templates['Makefile'] = Makefile = """
MAIN        := {MAIN}
SCRIPT_TEST := {MAIN} -h

# include make/makepy.mk

test: my-test
my-test:
\t# write your own tests here

build-something: $(SRC_FILES)
\t# use makepys make variables to define make dependencies to the source code
"""

makefile_comment = """
# Selection of Included Targets
# =============================
# make vars         # see most important makepy make vars
# make test         # run tests directly without tox and also run script tests
# make publish      # sign and upload to PyPi
# make docker-test  # pip install and test the PyPi version of your package in docker
#
# All make targets are subject to change and may be converted to makepy commands in the
# future. If possible the targets will then just call `makepy` to reproduce the targets
# build logic.
"""

templates['__init__.py'] = __init___py = """
# {flake_rules}
__version__ = '0.0.1'
__tag__     = 'py3'

def main(argv=None):
    import logging
    from makepy import argparse
    log = logging.getLogger(__name__)
    p = argparse.ArgumentParser().with_logging().with_debug()
    args = p.parse_args(argv)
    log.info('main called with %s', args)
""".format(flake_rules = 'flake8: noqa: F401')

templates['__main__.py'] = __main___py = """
# {flake_rules}
from __future__ import absolute_import
from {{MAIN}} import main
main()
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

# supported versions
versions        = 2 2.6 2.7 3 3.3 3.4 3.5 3.6
python_requires = >=2.6
"""

templates['LICENSE_txt'] = LICENSE_txt = """
Copyright (c) {YEAR} {NAME} {GITHUB_NAME}

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
