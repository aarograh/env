#!/bin/bash
SCRIPT="$1"
shift

command="$SCRIPT $@ -DMPACT_ENABLE_MAMBA=OFF -DMPACT_ENABLE_mongoose=OFF"
echo $command
$command
