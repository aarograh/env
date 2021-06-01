#!/bin/bash
command="$@ -DCTEST_DO_MEMORY_TESTING=TRUE -DMPACT_SCALE_TEST_TIMEOUT:STRING=20.0 #-DCTEST_MEMORYCHECK_COMMAND:STRING=\"/usr/bin/valgrind\"" #-DCTEST_MEMORYCHECK_COMMAND_OPTIONS:STRING="--trace-children=yes --tool=memcheck --leak-check=full --show-reachable=no"
echo $command
$command
