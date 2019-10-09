#make valgrind folder if not present 
MPACT_LIBS_DIR=$PWD
if [ ! -d ${MPACT_LIBS_DIR}/doc ]
then
    mkdir ${MPACT_LIBS_DIR}/doc
fi
if [ ! -d ${MPACT_LIBS_DIR}/doc/valgrindlogs ]
then
    mkdir ${MPACT_LIBS_DIR}/doc/valgrindlogs
fi
#loop over subpackages
for i in CMFD CoreSolvers Coupler CPM Depletion EditsVariables Factories Feedback MassTransport MOC MOCKokkos Nodal Perturb PlanarSynthesis PostOps Reactor Sn ThermalExpandXML Transient UI XS 
do
cd "${MPACT_LIBS_DIR}/$i/unit_tests"
    #loop over tests in folder
    for j in $(ls -d */); do
        cd "${MPACT_LIBS_DIR}/$i/unit_tests/$j"
        #only pull executables
        for k in $(ls | grep '.exe'); do
            valgrind --log-file=${MPACT_LIBS_DIR}/doc/valgrindlogs/$k.txt ./$k
        done
    done
done
exit 0
