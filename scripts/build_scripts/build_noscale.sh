#!/bin/bash
SCRIPT="$1"
shift

command="$SCRIPT $@ -DMPACT_ENABLE_Origen=OFF -DMPACT_ENABLE_Nemesis=OFF"
echo $command
$command
