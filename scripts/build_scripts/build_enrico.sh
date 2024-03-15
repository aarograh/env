# CC=mpicc \
# CXX=mpicxx \
# FC=mpifort \
# cmake \
#   -H../enrico_src/ \
#   -B. -DNEK_DIST=none \
#   -D CMAKE_INSTALL_PREFIX=../install \
#   -D CMAKE_INCLUDE_PATH="~/code_installations/scale_master_older/trilinos_install/include;~/code_installations/scale_master_older/install/include" \
#   -D CMAKE_LIBRARY_PATH="~/code_installations/scale_master_older/trilinos_install/lib;~/code_installations/scale_master_older/install/lib" \
#   -D CMAKE_PREFIX_PATH=~/code_installations/scale_master_older/install \
#   -D Trilinos_DIR=~/code_installations/scale_master_older/trilinos_install \
#   -D SCALE_DIR=~/code_installations/scale_master_older/src \
#   $@
# #   -D SCALE_DIR=~/code_installations/scale_master_older/install \

src_dir=$1
shift
install_dir=$1
shift

if [ -z ${src_dir} ]; then
  echo "Pass source directory as first argument!"
else
  if [ -z ${install_dir} ]; then
    echo "Pass installation directory as second argument!"
  else
    rm ${install_dir}/* -rf
    SPACK_DIR=~/spack/var/spack/environments/scale_7/.spack-env/view
    SPACK_LIBS=${SPACK_DIR}/lib
    SPACK_INCLUDES=${SPACK_DIR}/include

    HDF5_LIBRARY_NAMES="hdf5_hl;hdf5;hdf5_cpp;hdf5_fortran"

    Trilinos_LIBRARY_NAMES="tpetra"

    SCALE_DIR=/home/aarog/code_installations/scale_master/install
    SCALE_LIBS=${SCALE_DIR}/lib
    SCALE_INCLUDES=${SCALE_DIR}/include
    SCALE_LIBRARY_NAMES="OminbusDriver;Shift"

    CC=mpicc \
    CXX=mpicxx \
    FC=mpifort \
    cmake \
      $src_dir \
      -D CMAKE_INSTALL_PREFIX=$install_dir \
      -D TPL_ENABLE_MPI=ON \
      -D TPL_ENABLE_HDF5=ON \
      -D HDF5_LIBRARY_DIRS:FILEPATH=${SPACK_LIBS} \
      -D TPL_HDF5_INCLUDE_DIRS:FILEPATH="${SPACK_INCLUDES};${SPACK_DIR}/mod/shared" \
      -D HDF5_LIBRARY_NAMES=${HDF5_LIBRARY_NAMES} \
      -D TPL_ENABLE_Trilinos=ON \
      -D TPL_Trilinos_LIBRARY_DIRS:FILEPATH=${SPACK_LIBS} \
      -D TPL_Trilinos_INCLUDE_DIRS:FILEPATH=${SPACK_INCLUDES} \
      -D TPL_Trilinos_LIBRARIES="${Trilinos_LIBRARY_NAMES}" \
      -D TPL_ENABLE_SCALE=ON \
      -D SCALE_DIR=${SCALE_DIR} \
      -D TPL_SCALE_LIBRARY_DIRS:FILEPATH="${SCALE_DIR}/lib" \
      -D TPL_SCALE_INCLUDE_DIRS:FILEPATH="${SCALE_DIR}/include" \
      -D SCALE_INCLUDE_DIRS:FILEPATH="${SCALE_DIR}/include" \
      -D TPL_SCALE_LIBRARIES="${SCALE_LIBRARY_NAMES}" \
      -D Flibcpp_DIR="${SCALE_DIR}/lib/cmake/Flibcpp" \
      -D pugixml_DIR="${SCALE_DIR}/lib/cmake/pugixml" \
      -D CMAKE_PREFIX_PATH="${SCALE_DIR}/lib/cmake/pugixml"
      $@
  fi
fi