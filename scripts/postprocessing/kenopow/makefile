objects = constants_mod.o global_mod.o getsym.o collapsefissions.o fillunits.o fuelunits.o \
	  getfissions.o getloc.o h_write.o kenopow.o normalize.o \
 	  stats.o trygetk.o writehdf.o calcgeo.o makefull.o

EXE = kenopow.exe
FC = /opt/hdf5/1.8.11/gcc_4.6.3/bin/h5fc
DBG = -g -O0 -traceback
FFLAGS =  $(DB)

.SUFFIXES: .o .f90

$(EXE): $(objects)
	$(FC) $(FFLAGS) $(objects) -o $@
	rm -f *.o *.M *.mod
	ls -l $@ 

clean:
	rm -f $(objects) *.exe

.f90.o:
	$(FC) $(FFLAGS) -c $?
