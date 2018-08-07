#!/usr/bin/env bash

set -o errexit
set -o verbose

bash `dirname $0`/test_makepy.sh namespaced.project
