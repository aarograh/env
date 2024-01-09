#!/bin/bash
src_dir=$1
shift
install_dir=$1
shift

VERA_DEV_ENV_BASE=/home/tools/gcc-8.3.0
VERA_TPLS=${VERA_DEV_ENV_BASE}/tpls/opt

rm -rf CMake*
export CC=mpicc
export CXX=mpicxx
export F90=mpif90
CMAKE=cmake
#CMAKE=/home/oxh/bin/cmake
DATA=${src_dir}/data
MPI=${VERA_DEV_ENV_BASE}/toolset/mpich-3.3.2
LAPACK=${VERA_TPLS}/lapack-3.5.0
HDF5=${VERA_TPLS}/hdf5-1.10.1
#QT=
#OPTIONS_FILE=/opt/SCALE-6.3.1-Source/script/options_scale_packages.cmake

$CMAKE \
   -D CMAKE_Fortran_COMPILER=${F90} \
   -D SCALE_USE_Trilinos=ON \
   -D TPL_ENABLE_MPI:BOOL=ON \
   -D MPI_BASE_DIR:FILEPATH="${MPI}" \
   -D BUILD_SHARED:BOOL=ON \
   -D SCALE_DATA_DIR:STRING="${DATA}" \
   -D ENABLE_PYTHON_WRAPPERS:BOOL=OFF \
   -D DART_TESTING_TIMEOUT:STRING=3500 \
   -D SCALE_ENABLE_TESTS:BOOL=ON \
   -D SCALE_ENABLE_REGRESSION_TESTS:BOOL=ON \
   -D SCALE_ENABLE_SAMPLE_TESTS:BOOL=ON \
   -D CMAKE_BUILD_TYPE:STRING=RELEASE \
   -D CMAKE_INSTALL_PREFIX:STRING=${install_dir} \
   -D BLAS_LIBRARIES:STRING=${LAPACK}/lib/libblas.so \
   -D LAPACK_LIBRARIES:STRING=${LAPACK}/lib/liblapack.so \
   -D TPL_HDF5_LIBRARY_DIR:STRING=${HDF5}/lib \
   -D TPL_HDF5_INCLUDE_DIR:STRING=${HDF5}/include \
   -D TPL_ENABLE_QT=OFF \
   $* \
   $src_dir
#   -D SCALE_CONFIGURE_OPTIONS_FILE:FILEPATH=${OPTIONS_FILE} \
#   -D QT_DIR:STRING=${QT} \
#   -D TPL_QT_BIN:STRING=${QT}/bin \
#   -D SCALE_USE_SWIG_Python=OFF \
