#!/usr/bin/env bash

set -o errexit

# create a test project and run main makepy commands
PRJ="$1"
test -n "$PRJ"  # ensure PRJ is set

ccat(){ pygmentize $@ | head -n 20; }

set -o verbose

# asciinema: START
# lets create a new project
mkdir $PRJ
cd $PRJ
makepy init  # creates all common config and setup files
ls -la
ls -la $PRJ
ccat $PRJ/__init__.py
ccat $PRJ/__main__.py
ccat setup.cfg
ccat setup.py
ccat tox.ini
makepy backport  # backport project to Python 2
makepy dev-install  # install current source locally (no sudo required)
# lets see if the project's command is available
$PRJ -h
$PRJ --debug
makepy lint  # runs flake8
tox -e py36,py27  # tox runs tests for common envs (default: py36,py27,pypy)
makepy  # runs tox -e <current-env>
makepy dist  # creates a Python wheel in dist dir
ls -la dist
makepy dist -P 3
ls -la dist
makepy dists  # or just create all dists at once
ls -la dist
makepy uninstall  # get rid of all installations
pip3 install --user dist/$PRJ*py3*.whl
$PRJ -h
$PRJ --debug

# And now! Combine makepy with make!
makepy init --mkfiles  # create make/*.mk files with extra make features
ls -la make
ccat Makefile
ccat make/vars.mk
ccat make/project.mk
ccat make/tests.mk
sed -i 's/^# include/include/g' Makefile  # enable the mk-file include

make vars
make backport  # included mk files provide targets to wrap makepy commands
make dist my-test  # this allows to use them together with other make targets
# asciinema: END
