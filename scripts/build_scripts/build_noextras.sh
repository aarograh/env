#!/bin/bash
SCRIPT="$1"
shift

command="build_noscale.sh build_noctf.sh build_notrilinos.sh $SCRIPT $@"
echo $command
$command
