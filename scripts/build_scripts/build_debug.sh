#!/bin/bash
# Set the source directory
SOURCE_DIR="$1"
shift

command="$SOURCE_DIR/build_scripts/build_with_casl_env_830_newTPLs.sh $SOURCE_DIR/build_scripts/build_mpi_debug_omp_all.sh $SOURCE_DIR -DMPACT_ENABLE_MEMPROF=ON -DBLAS_LIBRARY_DIRS=/home/tools/gcc-8.3.0/tpls/opt/lapack-3.5.0/lib -DLAPACK_LIBRARY_DIRS=/home/tools/gcc-8.3.0/tpls/opt/lapack-3.5.0/lib -DMPACT_TEST_CATEGORIES=HEAVY -DMPACT_ENABLE_Teuchos=ON -DMPACT_ENABLE_Epetra=OFF -DMPACT_ENABLE_Tpetra=OFF -DMPACT_ENABLE_MueLu=OFF -DMPACT_ENABLE_Ifpack2=OFF -DMPACT_ENABLE_Anasazi=OFF -DMPACT_ENABLE_Belos=OFF -DMPACT_ENABLE_CTeuchos=OFF -DMPACT_ENABLE_ForTeuchos=OFF $@"
echo $command
$command
