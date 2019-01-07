      subroutine writehdf
      use HDF5 ! This module contains all necessary modules
      use global
      use constants
      implicit none

      character(len=10)  :: filename = "kenopow.h5"  ! File name
      character(len=12) :: dsetname                 ! Dataset name

      integer(hid_t)   :: file_id       ! File identifier
      integer(hsize_t) :: idims(10)     ! Dataset dimensions (2D array)

      integer     :: i,j,a,k,x
      integer     :: ierror              ! Error flag

      real*8, allocatable :: test(:,:,:,:)

!--- Initialize FORTRAN interface.

      call h5open_f(ierror)
      if (ierror.ne.0) stop 'ierror: h5open_f'

!--- Create a new file using default properties.

!      write (*,*) 'creating file: ', trim(filename)

      call h5fcreate_f(filename, H5F_ACC_TRUNC_F, file_id, ierror)
      if (ierror.ne.0) stop 'ierror: h5open_f'

      write (2,'(2a)') 'created file: ', trim(filename)

!--- write version

      idims(:)=0     ! clear
      call h_write(file_id,"version", idims, 2, H5T_NATIVE_INTEGER)

!--- write core map 

      idims(:)=0     ! clear
      idims(1)=core_size
      idims(2)=core_size

      call h_write(file_id, "core_map", idims, core_map, H5T_NATIVE_INTEGER)

!--- write k-effective and uncertainty

      idims(:)=0     ! clear

      call h_write(file_id,       "keff", idims, dble(keff)  , H5T_NATIVE_DOUBLE)
      call h_write(file_id, "keff_sigma", idims, dble(ksigma), H5T_NATIVE_DOUBLE)
     
!--- write core symmetry   

      if (core_sym==SYM_FULL) then
        x=1
      elseif (core_sym==SYM_QTR_SOUTHEAST) then
        x=4
      else
        x=0
      endif
      idims(:)=0     ! clear

      call h_write(file_id, "core_sym", idims, x , H5T_NATIVE_INTEGER)

!--- write pin powers and uncertainties

      idims(:)=0     ! clear
      idims(1)=nasst
      idims(2)=nax 
      idims(3)=npin 
      idims(4)=npin 

      do a=1,nasst
        do k=1,nax
          call makefull(power(a,k,:,:),npin,asssym(a))
          call makefull(sigma(a,k,:,:),npin,asssym(a))
        enddo
      enddo

      call h_write(file_id, "pin_powers"      , idims, power, H5T_NATIVE_DOUBLE)
      call h_write(file_id, "pin_powers_sigma", idims, sigma, H5T_NATIVE_DOUBLE)
      call h_write(file_id, "pin_volumes"     , idims,  vols, H5T_NATIVE_DOUBLE)
      call h_write(file_id, "pin_factors"     , idims,  mult, H5T_NATIVE_DOUBLE)
!     call h_write(file_id, "test_data"       , idims,  test, H5T_NATIVE_DOUBLE)

!--- write axial mesh    
 
      idims(:)=0     ! clear
      idims(1)=nax+1 

      call h_write(file_id, "axial_mesh" , idims, axmesh, H5T_NATIVE_DOUBLE)

!--- write axial powers  
 
      idims(:)=0     ! clear
      idims(1)=nax 

      call h_write(file_id, "axial_powers" ,       idims, axials, H5T_NATIVE_DOUBLE)
      call h_write(file_id, "axial_powers_sigma" , idims, axsigs, H5T_NATIVE_DOUBLE)

!--- write radial powers  
 
      idims(:)=0     ! clear
      idims(1)=nasst
      idims(2)=npin 
      idims(3)=npin 

      call h_write(file_id, "radial_powers" ,       idims, radials, H5T_NATIVE_DOUBLE)
      call h_write(file_id, "radial_powers_sigma" , idims, radsigs, H5T_NATIVE_DOUBLE)

!--- write assembly powers  
 
      idims(:)=0     ! clear
      idims(1)=nasst
      idims(2)=nax 

      call h_write(file_id, "assembly_powers" ,       idims, asspow, H5T_NATIVE_DOUBLE)
      call h_write(file_id, "assembly_powers_sigma" , idims, asssig, H5T_NATIVE_DOUBLE)

!--- write assembly radial powers  
 
      idims(:)=0     ! clear
      idims(1)=nasst

      call h_write(file_id, "assembly_radial_powers" ,       idims, assrad, H5T_NATIVE_DOUBLE)
      call h_write(file_id, "assembly_radial_powers_sigma" , idims, assrsg, H5T_NATIVE_DOUBLE)

!--- write nodal powers  
 
      idims(:)=0     ! clear
      idims(1)=nasst
      idims(2)=nax 
      idims(3)=4  

      call h_write(file_id, "nodal_powers" ,       idims, nodpow, H5T_NATIVE_DOUBLE)
      call h_write(file_id, "nodal_powers_sigma" , idims, nodsig, H5T_NATIVE_DOUBLE)
!--- Close the file and interface

      call h5fclose_f(file_id, ierror)
      call h5close_f(ierror)
      end
