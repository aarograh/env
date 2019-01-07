cmake \
-DVERA_TRIBITS_DIR:PATH=/home/aarograh/VERA/Trilinos/cmake/tribits \
-DVERA_ENABLE_TESTS:BOOL=OFF \
-DVERA_TEST_CATEGORIES:STRING=BASIC \
-DVERA_EXTRA_REPOSITORIES:STRING=Trilinos,TeuchosWrappersExt,VERAInExt,DataTransferKit,COBRA-TF,SCALE,MPACT,LIMEExt,PSSDriversExt \
-DVERA_ENABLE_KNOWN_EXTERNAL_REPOS_TYPE=Continuous \
-DVERA_EXTRAREPOS_FILE=/home/aarograh/VERA/cmake/ExtraRepositoriesList.cmake \
-DVERA_ENABLE_VRIPSScobra_preproc:BOOL=ON \
-DVERA_ENABLE_ALL_OPTIONAL_PACKAGES:BOOL=ON \
-DVERA_ENABLE_ALL_FORWARD_DEP_PACKAGES:BOOL=ON \
-DTPL_ENABLE_BLAS=ON -DTPL_BLAS_LIBRARIES:STRING="$BLASLAPACKLIBS" \
DTPL_ENABLE_LAPACK=ON -DTPL_LAPACK_LIBRARIES:STRING="$BLASLAPACKLIBS" \
/home/aarograh/VERA
