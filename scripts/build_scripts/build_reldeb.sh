#!/bin/bash
# Set the source directory
SOURCE_DIR="$1"
shift

command="$SOURCE_DIR/build_scripts/build_with_casl_env_830_newTPLs.sh $SOURCE_DIR/build_scripts/build_with_debug_info.sh $SOURCE_DIR/build_scripts/build_petsc_release_omp_all.sh $SOURCE_DIR -DFutility_ENABLE_DBC=ON -DMPACT_ENABLE_MEMPROF=ON -DMPACT_TEST_CATEGORIES=HEAVY $@"
#command="$SOURCE_DIR/build_scripts/build_with_casl_env_2023-04-05.sh $SOURCE_DIR/build_scripts/build_with_debug_info.sh $SOURCE_DIR/build_scripts/build_petsc_release_omp_all.sh $SOURCE_DIR -DFutility_ENABLE_DBC=ON -DMPACT_ENABLE_MEMPROF=ON -DMPACT_TEST_CATEGORIES=HEAVY $@"
echo $command
$command
