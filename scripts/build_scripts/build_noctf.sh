#!/bin/bash
SCRIPT="$1"
shift

command="$SCRIPT $@ -DMPACT_ENABLE_COBRA_TF=OFF"
echo $command
$command
