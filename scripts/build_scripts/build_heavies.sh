#!/bin/bash
SCRIPT="$1"
shift

$SCRIPT $@ -DMPACT_TEST_CATEGORIES=HEAVY
