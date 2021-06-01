#!/bin/bash
# Set the source directory
SOURCE_DIR="$1"
shift

command="build_notrilinos.sh $SOURCE_DIR/build_scripts/build_with_casl_env_830_newTPLs.sh $SOURCE_DIR/build_scripts/build_mpi_debug_omp_all.sh $SOURCE_DIR -DMPACT_ENABLE_MEMPROF=ON -DMPACT_TEST_CATEGORIES=HEAVY $@"
echo $command
$command
