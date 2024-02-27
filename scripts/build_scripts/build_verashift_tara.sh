SOURCE_DIR=$1
shift
cmake \
    -D VERA_CONFIGURE_OPTIONS_FILE:FILEPATH="$SOURCE_DIR/cmake/std/gcc-8.3.0/mpi-release-debug-shared-options.cmake" \
    -D VERA_ENABLE_TESTS:BOOL=ON \
    -D DART_TESTING_TIMEOUT:STRING=900.00 \
    -D VERA_ENABLE_CASL_MOOSE:BOOL=OFF \
    -D VERA_ENABLE_VeraShift:BOOL=ON \
    -D VERA_ENABLE_VERAOneWay:BOOL=ON \
    -D VERA_ENABLE_Insilico:BOOL=ON \
    -D VERA_INCL_CEData:BOOL=ON \
    -D VERA_ENABLE_ALL_PACKAGES:BOOL=ON \
    -D VERA_TEST_CATEGORIES:STRING=HEAVY \
    -D VERAIn_ENABLE_TESTS=ON \
    -D CMAKE_SHARED_LINKER_FLAGS_INIT:STRING="-Wno-missing-include-dirs -Wno-deprecated-declarations -Wno-sign-compare -Wno-unused-local-typedefs" \
    -D CMAKE_EXE_LINKER_FLAGS_INIT:STRING="-Wno-missing-include-dirs -Wno-deprecated-declarations -Wno-sign-compare -Wno-unused-local-typedefs" \
    -D MPI_EXEC_MAX_NUMPROCS=36 \
    $@ \
    $SOURCE_DIR
