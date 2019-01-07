objects = global_mod.o veradiff.o  \
          axial.o radial.o \
	  h_write.o h_read.o h_size.o \
	  h_exists.o h_readex.o h_sizeex.o \
          h_readstr.o writehdf.o \
          assembly.o radassy.o \

EXE = veradiff.exe
FC  = gfortran
INC = -I/opt/hdf5/1.8.11/gcc_4.6.3/lib/ -I/opt/hdf5/1.8.11/gcc_4.6.3/include/
LIB = -L/opt/hdf5/1.8.11/gcc_4.6.3/lib/ -lhdf5 -lhdf5_fortran -Wl,-rpath -Wl,/opt/hdf5/1.8.11/gcc_4.6.3/lib/ -lz -lm
DBG = -ggdb -O0 -fbacktrace -fbounds-check -ffpe-trap=zero,overflow,underflow
FFLAGS = $(DBG)

.SUFFIXES: .f90 .o

$(EXE): $(objects)
	$(FC) $(FFLAGS) -o $@ $(objects) $(LIB)
	rm -f *.o *.M *.mod
	ls -l $@ 

clean:
	rm -f $(objects) *.exe

.f90.o:
	$(FC) $(FFLAGS) -c $(INC) $?
