#!/usr/bin/env bash

set -o errexit

self=`readlink -f $0`
here=`dirname $self`
project=`dirname $here`
examples="$project/examples"


for f in `find $examples -name '*.py'`; do
	cmd="python $f --help"
	echo -n "testing '$cmd':"
	PYTHONPATH=$PYTHONPATH:$project $cmd >/dev/null
	echo -e "OK"
done 1>&2
