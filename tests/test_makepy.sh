#!/usr/bin/env bash

set -o errexit
set -o verbose

PRJ=$1
test -n "$PRJ" || PRJ=test_project
WORKDIR=$PWD/$PRJ
mkdir -p $WORKDIR
cd $WORKDIR

# install makepy if needed
which makepy || pip install --no-cache-dir makepy

makepy init --debug --trg .
makepy
makepy dist
makepy backport

if test -z "$USER"; then
	echo "testing installation"
	makepy install
	cd /tmp
	python -m $PRJ
	$PRJ
	cd $WORKDIR
	makepy uninstall
else
	echo "skipping installation"
fi

rm -rf $WORKDIR

