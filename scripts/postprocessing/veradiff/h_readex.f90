!=======================================================================
!
!  Wrapper Subroutine to read an array from an HDF5 file after
!    checking to see if it exists
!
!  file_id - file id returned by HDF5 open statement
!  dsetname- data set name
!  exists  - flag to indicate if data exists on the file
!  idims   - array that specifies the size of each dimension
!       set any unused dimensions to zero
!       examples:
!         idims= 100,  0,  0, 0, 0, 0, 0, 0, 0, 0   for 1D array
!         idims= 100, 20,  0, 0, 0, 0, 0, 0, 0, 0   for 2D array
!         idims= 100, 20, 16, 0, 0, 0, 0, 0, 0, 0   for 3D array, etc.
!  dat - data array to be written
!
!=======================================================================
      subroutine h_readex(file_id,dsetname,exists,idims,data)
      use hdf5 ! This module contains all necessary modules
      implicit none

      integer(hid_t),   intent(in)    :: file_id      ! File identifier
      character(len=*), intent(in)    :: dsetname     ! Dataset name
      logical         , intent(out)   :: exists       ! logical check to see if exists first
      integer(hsize_t), intent(out)   :: idims(10)    ! Dataset dimensions
      real            , intent(inout) :: data(*)      ! multi-dimensional array, treated as 1D

      call h_exists(file_id,dsetname,exists)
      if (exists) then
        call h_read(file_id,dsetname,idims,data)
      endif
      return
      end subroutine h_readex
