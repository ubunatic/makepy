#!/usr/bin/env bash

here=`dirname $0`
project=`dirname $here`
examples="$project/examples"

set -o errexit

for f in `find $examples -name '*.py'`; do
	cmd="python $f --help"
	echo -n "testing '$cmd':"
	PYTHONPATH=$PYTHONPATH:$project $cmd >/dev/null
	echo -e "OK"
done 1>&2
