#!/usr/bin/env bash

test_makepy=`dirname $0`/test_makepy.sh

set -o errexit
set -o verbose

PY=2 $test_makepy demo_two
# PY=2 $test_makepy demo.two  # namespaces not supported by Python 2 makepy

PY=3 $test_makepy demo_three
PY=3 $test_makepy demo.three

rm -rf demo*
