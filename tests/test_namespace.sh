#!/usr/bin/env bash

set -o errexit
set -o verbose

bash `dirname $0`/test_makepy.sh test_namespace.project
