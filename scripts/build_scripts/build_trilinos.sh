src_dir=$1
shift
install_dir=$1
shift

if [ -n "$src_dir" ]; then
  if [ -n "$install_dir" ]; then
    rm -rf $install_dir/*
    CC=mpicc CXX=mpicxx FC=mpifort cmake $src_dir -D CMAKE_INSTALL_PREFIX=$install_dir -DTrilinos_ENABLE_Intrepid=ON -DTrilinos_ENABLE_Stratimikos=ON -DTrilinos_ENABLE_Thyra=ON -DTrilinos_ENABLE_Anasazi=ON -DTrilinos_ENABLE_TeuchosCore=ON -DTrilinos_ENABLE_TeuchosParameterList=ON -DTrilinos_ENABLE_TeuchosComm=ON -DTrilinos_ENABLE_TeuchosNumerics=ON -DTrilinos_ENABLE_Epetra=ON -DTrilinos_ENABLE_Ifpack=ON -DTrilinos_ENABLE_ML=ON -DTrilinos_ENABLE_Ifpack2=ON -DTrilinos_ENABLE_Tpetra=ON -DTrilinos_ENABLE_EpetraExt=ON -DTrilinos_ENABLE_Belos=ON -DTrilinos_ENABLE_ThyraEpetraAdapters=ON -DTrilinos_ENABLE_ThyraTpetraAdapters=ON -DTrilinos_ENABLE_Amesos=ON -DTrilinos_ENABLE_Amesos2=ON -DTrilinos_ENABLE_AztecOO=ON -DTrilinos_ENABLE_KokkosCore=ON -DTPL_ENABLE_MPI=ON -DCMAKE_CXX_FLAGS="-fPIC" -DCMAKE_C_FLAGS="-fPIC" -DCMAKE_Fortran_FLAGS="-fPIC" $@
  else
    echo "Usage: build_trilinos.sh source_dir install_dir [options]"
  fi
else
  echo "Usage: build_trilinos.sh source_dir install_dir [options]"
fi
