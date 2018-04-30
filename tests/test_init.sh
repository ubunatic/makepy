#!/usr/bin/env bash

set -o errexit
set -o verbose

PRJ=test_project
WORKDIR=$PWD/$PRJ
mkdir -p $WORKDIR
cd $WORKDIR

makepy init --debug --trg .
ls -la . $PRJ

makepy help
makepy test -P 2
makepy test -P 3
makepy lint
makepy dist
makepy backport
makepy -e py2
makepy -e py3

if test -z "$USER"; then
	echo "testing installation"
	makepy install
	makepy install -P 2

	cd /tmp
	python2 -m $PRJ
	python3 -m $PRJ
	$PRJ

	cd $WORKDIR
	makepy uninstall
else
	echo "skipping installation"
fi

rm -rf $WORKDIR

