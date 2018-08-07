#!/usr/bin/env bash

source `dirname $0`/install.rc

set -o errexit
set -o verbose

if test -n "$USER"
then PIP_ARGS=--user
else PIP_ARGS=
fi

test -n "$PY" || PY=3
PIP=pip$PY
PYTHON=python$PY
TAG=py`echo "$PY" | cut -d . -f 1`

install_makepy

PRJ=$1
test -n "$PRJ" || PRJ=test_project
WORKDIR=$PWD/$PRJ
mkdir -p $WORKDIR
cd $WORKDIR

mp(){ makepy $@ -P 3; }

mp init --debug --trg .
mp
mp dist
mp backport

cleanup(){
	err=$?
	cd $WORKDIR &&
	# makepy uninstall 2>/dev/null 1>/dev/null &&
	# rm -rf $WORKDIR
	if test $err -eq 0
	then echo "$0 $PRJ: OK"
	else echo "$0 $PRJ: FAILED (Err: $err, see logs)"
	fi
	return $err
}

trap cleanup EXIT
echo "testing installation"
mp dists
version=`mp version`
echo "PIP_ARGS=$PIP_ARGS"
$PIP install -I --force-reinstall $PIP_ARGS dist/$PRJ-$version-$TAG-none-any.whl
which $PRJ | xargs cat
cd /tmp
$PRJ
