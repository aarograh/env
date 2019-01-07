!=======================================================================
!
!  Wrapper Subroutine to read an array dimensions from an HDF5 file
!    but only if the dataset exists
!
!=======================================================================
      subroutine h_sizeex(file_id, dsetname, exists, idims)
      USE hdf5 ! This module contains all necessary modules
      implicit none

      integer(hid_t),   intent(in)    :: file_id      ! File identifier
      character(len=*), intent(in)    :: dsetname     ! Dataset name
      logical         , intent(out)   :: exists       ! logical check to see if exists first
      integer(hsize_t), intent(out)   :: idims(10)    ! Dataset dimensions
      integer                         :: ierror       ! error code

      call h_exists(file_id, dsetname, exists)
      if (exists) then
        call h_size(file_id,dsetname,idims)
      endif
      return
      end subroutine h_sizeex
