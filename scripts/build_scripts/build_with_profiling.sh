#!/bin/bash

command="$@ -DMPACT_GPROF=ON"
echo $command
$command
