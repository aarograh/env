${1}/build_scripts/build_with_hdf5.sh ${1}/build_scripts/build_ap_release_omp_all.sh ${1} \
-DTPL_ENABLE_PETSC:BOOL=ON \
-DTPL_PETSC_LIBRARIES="${PETSC_DIR}/${PETSC_ARCH}/lib/libcraypetsc_gnu_real.a" \
-DTPL_HDF5_LIBRARIES="${HDF5_ROOT}/lib/libhdf5.a;${HDF5_ROOT}/lib/libhdf5_fortran.a" \
-DMPACT_ENABLE_ALL_PACKAGES:BOOL=TRUE
