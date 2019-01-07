if [ ${#} -ge 2 ]
then
  SOURCEDIR=${1}
  BUILDTYPE=${2}
  shift; shift
  ${SOURCEDIR}/build_scripts/build_with_hdf5.sh ${SOURCEDIR}/build_scripts/build_ap_${BUILDTYPE}_omp_all.sh ${SOURCEDIR} \
  -DTPL_ENABLE_PETSC:BOOL=ON \
  -DTPL_PETSC_LIBRARIES="${PETSC_DIR}/${PETSC_ARCH}/lib/libcraypetsc_gnu_real.a" \
  -DTPL_HDF5_LIBRARIES="${HDF5_ROOT}/lib/libhdf5_gnu_parallel.a;${HDF5_ROOT}/lib/libhdf5_fortran_gnu_parallel.a" \
  ${@}
else
  echo "Usage: build.sh <source.dir> <debug|release>"
fi
