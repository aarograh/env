#!/bin/bash
# Set the source directory
SOURCE_DIR="$1"
shift

#command="$SOURCE_DIR/build_scripts/build_with_casl_env_540.sh $SOURCE_DIR/build_scripts/build_petsc_debug_omp_all.sh -GNinja -DMPACT_ENABLE_MEMPROF=ON $SOURCE_DIR $@"
command="$SOURCE_DIR/build_scripts/build_with_casl_env_540.sh $SOURCE_DIR/build_scripts/build_petsc_debug_omp_all.sh -DMPACT_ENABLE_MEMPROF=ON -G Ninja $SOURCE_DIR $@"
echo $command
$command
