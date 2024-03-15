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
    CXX=`which mpic++` CC=`which mpicc` FC=`which mpifort` F90=`which mpif90` cmake \
       -D SCALE_GIT_SUBMODULE=OFF \
       -D SCALE_USE_CUDA=OFF \
       -D SCALE_USE_SWIG_Python=ON \
       -D SCALE_USE_SWIG_Fortran=OFF \
       -D SCALE_USE_Qt=OFF \
       -D SCALE_USE_OpenMP=ON \
       -D CMAKE_INSTALL_PREFIX=${install_path} \
       -D SCALE_DATA_DIR=${install_path}/../scale_data \
       -D CMAKE_CXX_FLAGS="-fPIC" \
       -D CMAKE_C_FLAGS="-fPIC" \
       -D CMAKE_Fortran_FLAGS="-fPIC" \
       $src_path $@
  fi
fi
