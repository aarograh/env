#!/bin/bash
# Set the source directory
SOURCE_DIR="$1"
shift

command="$SOURCE_DIR/build_scripts/build_with_casl_env.sh $SOURCE_DIR/build_scripts/build_petsc_release_omp_all.sh $SOURCE_DIR -GNinja $@"
echo $command
$command
