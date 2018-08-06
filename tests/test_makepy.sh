#!/usr/bin/env bash

# installs makepy if needed
install_makepy() {
	if which makepy; then
		echo "using installed makepy"
	elif test "`basename "$PWD"`" = makepy; then
		echo "running in makepy dir, using local makepy dist"
		pip install --no-cache-dir -e "$PWD"
	else
		echo "running outside makepy dir, using pypi dist"
		# pip install --no-cache-dir makepy
	fi
}

set -o errexit
set -o verbose

PRJ=$1
test -n "$PRJ" || PRJ=test_project
WORKDIR=$PWD/$PRJ
mkdir -p $WORKDIR
cd $WORKDIR

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

