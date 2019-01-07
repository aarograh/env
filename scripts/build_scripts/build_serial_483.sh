#!/bin/bash
# Set the source directory
SOURCE_DIR="$1"
shift

command="build_noscale.sh build_notrilinos.sh $SOURCE_DIR/build_scripts/build_with_hdf5.sh $SOURCE_DIR/build_scripts/build_gnu_debug_omp_all.sh $SOURCE_DIR -DMPACT_ENABLE_MEMPROF=ON $@"
echo $command
$command
