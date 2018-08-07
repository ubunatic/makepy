#!/usr/bin/env bash

source `dirname $0`/install.rc

set -o errexit
set -o verbose

test -n "$PY" || PY=3
PIP=pip$PY
PYTHON=python$PY
TAG=py`echo "$PY" | cut -d . -f 1`

install_makepy

PKG=$1
test -n "$PKG" || PKG=demo1

PRJ=`echo "$PKG" | sed 's#[\./\/]\+#-#g'`
WHL=`echo "$PKG" | sed 's#[\./\/-]\+#_#g'`
echo "creating test project: $PRJ for package: $PKG in PWD: $PWD"
WORKDIR=`readlink -f "$PWD/$PRJ"`

mkdir -p $WORKDIR
cd $WORKDIR

mp(){ makepy $@ -P $PY; }

mp init --debug -p $PKG
mp lint
mp test
mp dist
mp backport
mp dists
version=`mp version`

cleanup(){
	err=$?
	if cd $WORKDIR &&
		makepy uninstall 2>/dev/null 1>/dev/null &&
		rm -rf $WORKDIR
	then echo "cleanup: OK"
	else echo "cleanup: FAILED (Please remove $WORKDIR manually and uninstall $PRJ)"
	fi
	if test $err -eq 0
	then echo "$0 $PRJ: OK"
	else echo "$0 $PRJ: FAILED (Err: $err, see logs)"
	fi
	return $err
}

trap "cleanup" EXIT
echo "testing installation using: $PIP install $PIP_ARGS"
$PIP install -I --force-reinstall $PIP_ARGS dist/$WHL-$version-$TAG-none-any.whl
which $PRJ | xargs cat
cd /tmp
$PRJ
