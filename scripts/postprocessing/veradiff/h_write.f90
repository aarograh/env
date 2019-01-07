!=======================================================================
!
!  Wrapper Subroutine to write an array to an HDF5 file
!
!  file_id - file id returned by HDF5 open statement
!  dsetname- data set name
!  idims   - array that specifies the size of each dimension
!       set any unused dimensions to zero
!       examples:
!         idims= 100,  0,  0, 0, 0, 0, 0, 0, 0, 0   for 1D array
!         idims= 100, 20,  0, 0, 0, 0, 0, 0, 0, 0   for 2D array
!         idims= 100, 20, 16, 0, 0, 0, 0, 0, 0, 0   for 3D array, etc.
!  dat - data array to be written
!
!   Prefix  H5A Attributes
!     H5D   Datasets
!     H5E   Error reports
!     H5F   Files
!     H5G   Groups
!     H5I   Identifiers
!     H5L   Links
!     H5O   Objects
!     H5P   Property lists
!     H5R   References
!     H5S   Dataspaces
!     H5T   Datatypes
!     H5Z   Filters
!
!=======================================================================
      subroutine h_write(file_id, dsetname, idims, dat, type_id)
      USE hdf5 ! This module contains all necessary modules
      implicit none

      character(len=*), intent(in) :: dsetname     ! Dataset name
      integer(hid_t),   intent(in) :: file_id      ! File identifier
      integer(hsize_t), intent(in) :: idims(10)    ! Dataset dimensions
      integer(hid_t)  , intent(in) :: type_id      ! flat for dataset type
      real                         :: dat(*)      ! multi-dimensional array, treated as 1D

!--- local

      integer(hid_t) :: dset_id       ! Dataset identifier
      integer(hid_t) :: dspace_id     ! Dataspace identifier

      integer  :: i
      integer  :: irank               ! Dataset rank
      integer  :: ierror              ! Error flag

!--- calculate rank from idims array
      irank=0
      do i=1, 10
        if (idims(i).gt.0) irank=i
      enddo

      write (3,'(2a,i3)') ' writing dataspace name: ', dsetname
      write (3,*) '  creating dataspace with rank ', irank
      if (irank>0) then
        write (3,*) '  creating dataspace with dims ', idims(1:irank)
      endif

! Create the dataspace (information about array)

      call h5screate_simple_f(irank, idims, dspace_id, ierror)
      if (ierror.ne.0) stop 'ierror: h5screate_simple'

      write (3,*) '  created dataspace id        ', dspace_id

! Create the dataset with default properties.

      call h5dcreate_f(file_id, dsetname, type_id, dspace_id, dset_id, ierror)
      if (ierror.ne.0) then
        write(*,*) ' dataset: ',trim(dsetname)
        stop 'ierror: h5dcreate_f'
      endif

! Write dataset

      call h5dwrite_f(dset_id, type_id, dat, idims, ierror)
      if (ierror.ne.0) stop 'ierror: h5dwrite_f'

! End access to the dataset and release resources used by it. (release dataset id)

      call h5dclose_f(dset_id, ierror)
      if (ierror.ne.0) stop 'ierror: h5dclose_f'

! Terminate access to the data space.  (release dataspace id)

      call h5sclose_f(dspace_id, ierror)
      if (ierror.ne.0) stop 'ierror: h5sclose_f'

      return
      end subroutine h_write
