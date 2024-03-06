install_path=/home/aarog/sbir_microrx/install_scale

rm -rf $install_path/*
CXX=`which mpic++` CC=`which mpicc` FC=`which mpifort` F90=`which mpif90` cmake \
   -D SCALE_GIT_SUBMODULE=OFF \
   -D SCALE_USE_CUDA=OFF \
   -D SCALE_USE_SWIG_Python=OFF \
   -D SCALE_USE_SWIG_Fortran=OFF \
   -D SCALE_USE_Qt=OFF \
   -D SCALE_USE_OpenMP=ON \
   -D CMAKE_INSTALL_PREFIX=${install_path} \
   $@
