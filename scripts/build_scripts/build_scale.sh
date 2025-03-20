src_path=$1
shift
install_path=$1
shift

if [ -z ${src_path} ]; then
  echo "source path must be passed as first argument"
else
  if [ -z ${install_path} ]; then
    echo "install path must be passed as second argument"
  else
    rm -rf $install_path/*
    rm -rf CMake*
    CXX=`which mpic++` CC=`which mpicc` FC=`which mpif90` F90=`which mpif90` cmake \
    -DTPL_ENABLE_MPI=ON \
    -DCMAKE_BUILD_TYPE="RelWithDebInfo" \
    -DSCALE_ENABLE_ALL_PACKAGES=ON \
    -DCMAKE_INSTALL_PREFIX=$install_path \
    -DBUILD_SHARED_LIBS=ON \
    -DTPL_ENABLE_Netcdf=OFF \
    -DSCALE_USE_DAGMC=OFF \
       -D SCALE_GIT_SUBMODULE=OFF \
       -D SCALE_USE_Fortran=ON \
       -D SCALE_USE_CUDA=OFF \
       -D SCALE_USE_SWIG_Python=OFF \
       -D SCALE_USE_SWIG_Fortran=OFF \
       -D SCALE_DATA_DIR=/projects/veracity/aaron/scale_master/scale_7_data \
       -D SCALE_BUILD_OMNIBUS_DOCS=ON \
    $src_path
  fi
fi
