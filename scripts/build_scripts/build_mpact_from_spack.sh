#!/bin/bash
SCRIPT=$1
MPACT=$2
shift 2

SPACK_DIR=~/spack/var/spack/environments/vera_4-4_tpls/.spack-env/view
SPACK_LIBS=${SPACK_DIR}/lib
SPACK_INCLUDES=${SPACK_DIR}/include

PETSC_LIBRARY_NAMES="petsc"
HDF5_LIBRARY_NAMES="hdf5_hl;hdf5;hdf5_cpp;hdf5_fortran"

${SCRIPT} ${MPACT}        -DMPACT_BUILD_STANDARD=OFF                          \
   -DTPL_ENABLE_BLAS=ON   -DBLAS_LIBRARY_DIRS:FILENAME=${SPACK_LIBS}          \
   -DTPL_ENABLE_LAPACK=ON -DLAPACK_LIBRARY_DIRS:FILEPATH=${SPACK_LIBS}        \
   -DTPL_ENABLE_HDF5=ON   -DHDF5_LIBRARY_DIRS:FILEPATH=${SPACK_LIBS}          \
                          -DTPL_HDF5_INCLUDE_DIRS:FILEPATH="${SPACK_INCLUDES};${SPACK_DIR}/mod/shared"      \
                          -DHDF5_LIBRARY_NAMES:STRING=${HDF5_LIBRARY_NAMES}   \
   -DTPL_ENABLE_SILO=ON   -DSILO_LIBRARY_DIRS:FILEPATH=${SPACK_LIBS}          \
                          -DSILO_INCLUDE_DIRS:FILEPATH=${SPACK_INCLUDES}      \
                          -DPETSC_LIBRARY_DIRS:FILEPATH=${SPACK_LIBS}         \
                          -DPETSC_INCLUDE_DIRS:FILEPATH=${SPACK_INCLUDES}     \
                          -DPETSC_LIBRARY_NAMES:STRING=${PETSC_LIBRARY_NAMES} \
   $@
#   -DTPL_ENABLE_SLEPC=ON  -DSLEPC_LIBRARY_DIRS:FILEPATH=${SLEPC_LIBRARY_DIRS}    \
#                          -DSLEPC_INCLUDE_DIRS:FILEPATH=${SLEPC_INCLUDE_DIRS}    \
