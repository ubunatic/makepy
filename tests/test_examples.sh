#!/usr/bin/env bash

source `dirname $0`/install.rc

set -o errexit
set -o verbose

install_makepy

project=`readlink -f "$PWD"`

for f in `find $project/examples -name '*.py'`; do
	cmd="python $f --help"
	echo -n "testing '$cmd':"
	PYTHONPATH=$PYTHONPATH:$project $cmd >/dev/null
	echo -e "OK"
done 1>&2

