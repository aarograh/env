#!/bin/bash
SCRIPT="$1"
shift

command="$SCRIPT $@ -DMPACT_ENABLE_Teuchos=OFF -DMPACT_ENABLE_Epetra=OFF"
echo $command
$command
