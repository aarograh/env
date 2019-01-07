      subroutine writehdf(state)
      use HDF5 ! This module contains all necessary modules
      use global
      implicit none

      character(len=16) :: filename                 ! File name
      character(len=80) :: dsetname                 ! Dataset name
      character(len=10), intent(in) :: state

      integer(hid_t)   :: file_id       ! File identifier
      integer(hsize_t) :: idims(10)     ! Dataset dimension
      integer(hid_t)   :: core_group_id   ! group identifier
      integer(hid_t)   :: state_group_id  ! group identifier

      integer     :: i,j,a,k,x
      integer     :: ierror              ! Error flag
      integer     :: ndx

!--- Initialize FORTRAN interface.

      ndx=index(state,'_')

      if (ndx>1) then
        filename = 'veradiff_'//state(ndx+1:10)//'.h5'
      else
        filename = 'veradiff.h5'
      endif
      call h5open_f(ierror)
      if (ierror.ne.0) stop 'ierror: h5open_f'

!--- Create a new file using default properties.

!      write (*,*) 'creating file: ', trim(filename)

      call h5fcreate_f(filename, H5F_ACC_TRUNC_F, file_id, ierror)
      if (ierror.ne.0) stop 'ierror: h5open_f'

      write (3,'(2a)') 'created file: ', trim(filename)

!--- Write version number

      idims(:)=0     ! clear
      call h_write(file_id, "veraout_version", idims, 1 , H5T_NATIVE_INTEGER)

!--- Create groups

      call h5gcreate_f(file_id, '/CORE',       core_group_id,  ierror)
      call h5gcreate_f(file_id, '/STATE_0001', state_group_id, ierror)

!--- write axial mesh 
 
      idims(:)=0     ! clear
      idims(1)=nax+1 

      call h_write(core_group_id, "axial_mesh" , idims, axmesh, H5T_NATIVE_DOUBLE)

!--- write core map 

      idims(:)=0     ! clear
      idims(1)=nsize 
      idims(2)=nsize 
      call h_write(core_group_id, "core_map", idims, coremap, H5T_NATIVE_INTEGER)

!--- write k-effectives and uncertainties

      idims(:)=0     ! clear

      call h_write(state_group_id, "keff_1", idims, keff1, H5T_NATIVE_DOUBLE)
      call h_write(state_group_id, "keff_2", idims, keff2, H5T_NATIVE_DOUBLE)
     
      if (isMC1) then
        call h_write(state_group_id, "keff_sigma_1", idims, ksigma1, H5T_NATIVE_DOUBLE)
      endif

      if (isMC2) then
        call h_write(state_group_id, "keff_sigma_2", idims, ksigma2, H5T_NATIVE_DOUBLE)
      endif
  
      call h_write(state_group_id, "keff_diff", idims, dk, H5T_NATIVE_DOUBLE)

      if (isMC1 .or. isMC2) then
        call h_write(state_group_id, "keff_sigma_diff", idims, dk, H5T_NATIVE_DOUBLE)
      endif

!--- write core symmetry   

      idims(:)=0     ! clear
      call h_write(core_group_id, "core_sym", idims, isym , H5T_NATIVE_INTEGER)

!--- write pin powers and uncertainties

      idims(:)=0     ! clear
      idims(1)=nassy
      idims(2)=nax 
      idims(3)=npin
      idims(4)=npin

      call h_write(state_group_id, "pin_powers_1"      , idims, power1, H5T_NATIVE_DOUBLE)
      call h_write(state_group_id, "pin_powers_2"      , idims, power2, H5T_NATIVE_DOUBLE)
      call h_write(state_group_id, "pin_powers_diff"   , idims, pdiff , H5T_NATIVE_DOUBLE)

      if (isMC1) then
        call h_write(state_group_id, "pin_powers_sigma_1", idims, sigma1, H5T_NATIVE_DOUBLE)
      endif

      if (isMC2) then
        call h_write(state_group_id, "pin_powers_sigma_2", idims, sigma2, H5T_NATIVE_DOUBLE)
      endif

      if (isMC1 .or. isMC2) then
        call h_write(state_group_id, "pin_powers_diff_sigma", idims, sdiff , H5T_NATIVE_DOUBLE)
        call h_write(state_group_id, "pin_powers_num_sigmas", idims, sigmas, H5T_NATIVE_DOUBLE)
      endif
       
      call h_write(core_group_id, "pin_factors", idims, wgt, H5T_NATIVE_DOUBLE)

      call h_write(state_group_id, "form_factors_1"   , idims, ffact1   , H5T_NATIVE_DOUBLE)
      call h_write(state_group_id, "form_factors_2"   , idims, ffact2   , H5T_NATIVE_DOUBLE)
      call h_write(state_group_id, "form_factors_diff", idims, ffactdiff, H5T_NATIVE_DOUBLE)

!--- write the axial average powers
      if (nax>1) then

        idims(:)=0     ! clear
        idims(1)=nax  

        call h_write(state_group_id, "axial_powers_1" , idims, axpow1, H5T_NATIVE_DOUBLE)
        call h_write(state_group_id, "axial_powers_2" , idims, axpow2, H5T_NATIVE_DOUBLE)
        call h_write(state_group_id, "axial_powers_diff", idims, axpowdiff, H5T_NATIVE_DOUBLE)

        if (isMC1) then
          call h_write(state_group_id, "axial_powers_sigma_1" , idims, axsig1, H5T_NATIVE_DOUBLE)
        endif
        
        if (isMC2) then
          call h_write(state_group_id, "axial_powers_sigma_2" , idims, axsig2, H5T_NATIVE_DOUBLE)
        endif

        if (isMC1 .or. isMC2) then
          call h_write(state_group_id, "axial_powers_diff_sigma" , idims, axsigdiff, H5T_NATIVE_DOUBLE)
        endif
      endif

!--- write the radial average powers
     
      if (nax>1) then

        idims(:)=0     ! clear
        idims(1)=nassy
        idims(2)=npin 
        idims(3)=npin 

        call h_write(state_group_id, "radial_powers_1" , idims, radpow1, H5T_NATIVE_DOUBLE)
        call h_write(state_group_id, "radial_powers_2" , idims, radpow2, H5T_NATIVE_DOUBLE)
        call h_write(state_group_id, "radial_powers_diff", idims, radpowdiff, H5T_NATIVE_DOUBLE)

        if (isMC1) then
          call h_write(state_group_id, "radial_powers_sigma_1" , idims, radsig1, H5T_NATIVE_DOUBLE)
        endif
        
        if (isMC2) then
          call h_write(state_group_id, "radial_powers_sigma_2" , idims, radsig2, H5T_NATIVE_DOUBLE)
        endif

        if (isMC1 .or. isMC2) then
          call h_write(state_group_id, "radial_powers_diff_sigma" , idims, radsigdiff, H5T_NATIVE_DOUBLE)
        endif

        call h_write(core_group_id, "radial_factors" , idims, radwgt, H5T_NATIVE_DOUBLE)
      endif

!--- write assembly powers and uncertainties

      idims(:)=0     ! clear
      idims(1)=nassy
      idims(2)=nax  

      call h_write(state_group_id, "assembly_powers_1"      , idims, asspow1, H5T_NATIVE_DOUBLE)
      call h_write(state_group_id, "assembly_powers_2"      , idims, asspow2, H5T_NATIVE_DOUBLE)
      call h_write(state_group_id, "assembly_powers_diff"   , idims, asspowdiff, H5T_NATIVE_DOUBLE)

      if (isMC1) then
        call h_write(state_group_id, "assembly_powers_sigma_1", idims, asssig1, H5T_NATIVE_DOUBLE)
      endif

      if (isMC2) then
        call h_write(state_group_id, "assembly_powers_sigma_2", idims, asssig2, H5T_NATIVE_DOUBLE)
      endif

      if (isMC1 .or. isMC2) then
        call h_write(state_group_id, "assembly_powers_diff_sigma", idims, asssigdiff , H5T_NATIVE_DOUBLE)
      endif
       
      call h_write(core_group_id, "assembly_factors", idims, asswgt, H5T_NATIVE_DOUBLE)

!--- write 2D assembly powers and uncertainties

      if (nax>1) then
        idims(:)=0     ! clear
        idims(1)=nassy

        call h_write(state_group_id, "radial_assembly_powers_1"      , idims, ardpow1, H5T_NATIVE_DOUBLE)
        call h_write(state_group_id, "radial_assembly_powers_2"      , idims, ardpow2, H5T_NATIVE_DOUBLE)
        call h_write(state_group_id, "radial_assembly_powers_diff"   , idims, ardpowdiff, H5T_NATIVE_DOUBLE)

        if (isMC1) then
          call h_write(state_group_id, "radial_assembly_powers_sigma_1", idims, ardsig1, H5T_NATIVE_DOUBLE)
        endif

        if (isMC2) then
          call h_write(state_group_id, "radial_assembly_powers_sigma_2", idims, ardsig2, H5T_NATIVE_DOUBLE)
        endif

        if (isMC1 .or. isMC2) then
          call h_write(state_group_id, "radial_assembly_powers_diff_sigma", idims, ardsigdiff , H5T_NATIVE_DOUBLE)
        endif
         
        call h_write(core_group_id, "radial_assembly_factors", idims, ardwgt, H5T_NATIVE_DOUBLE)
      endif 

!--- Create groups

      call h5gclose_f(core_group_id , ierror)
      call h5gclose_f(state_group_id, ierror)

!--- Close the file and interface

      call h5fclose_f(file_id, ierror)
      call h5close_f(ierror)
      end
