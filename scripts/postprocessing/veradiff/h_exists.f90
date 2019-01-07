!=======================================================================
!
!  Wrapper Subroutine to see is dataset exists on an HDF5 file
!
!=======================================================================
      subroutine h_exists(file_id, dsetname, exists)
      USE hdf5 ! This module contains all necessary modules
      implicit none

      integer(hid_t),   intent(in)    :: file_id      ! File identifier
      character(len=*), intent(in)    :: dsetname     ! Dataset name
      logical         , intent(out)   :: exists       ! logical check to see if exists first
      integer                         :: ierror       ! error code

      call h5lexists_f(file_id, dsetname, exists, ierror)
      if (ierror/=0) then
        write(3,*) 'error checking for existance of ',trim(dsetname)
        stop       'error in h5lexists'
      endif
      return 
      end subroutine h_exists
