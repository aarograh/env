!=======================================================================
!
!  Wrapper Subroutine to read an array from an HDF5 file
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
!  type_id - returned type
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
      subroutine h_read(file_id, dsetname, idims, data)
      use hdf5 ! This module contains all necessary modules
      implicit none

      character(len=*), intent(in)    :: dsetname     ! Dataset name
      integer(hid_t),   intent(in)    :: file_id      ! File identifier
      integer(hsize_t), intent(out)   :: idims(10)    ! Dataset dimensions
      integer(hid_t)                  :: type_id      ! flag for dataset type
      real            , intent(inout) :: data(*)      ! multi-dimensional array, treated as 1D

!--- local

      integer(hid_t)   :: dset_id        ! Dataset identifier
      integer(hid_t)   :: dspace_id      ! Dataspace identifier
      integer(hsize_t) :: h_maxdims(10)  ! Dataset dimensions
      integer          :: ierror         ! error code

      integer  :: i
      integer  :: irank               ! Dataset rank

      write(3,*)
      write(3,*)   'opening dataset: ',trim(dsetname)

! Open the dataset
      call h5dopen_f(file_id, dsetname, dset_id, ierror)
      if (ierror<0) then
        write(3,*) 'data set ',trim(dsetname), ' could not be opened'
        stop 'error in h5dopen'
      endif

! Get the dataspace (information about array)

      call h5dget_space_f(dset_id, dspace_id, ierror) 
      if (ierror<0) stop 'error in h5dget_space'

! Get the data type

      call h5dget_type_f(dset_id, type_id, ierror)           
      if (ierror<0) stop 'error in h5dget_type' 

! Get rank       
      call h5sget_simple_extent_ndims_f(dspace_id, irank, ierror)  
      if (ierror<0) stop 'error in h5sget_simple_extent_ndims' 
      if (irank.gt.10) stop 'maximum dimensions exceeded'

! Get Dimensions
      call h5sget_simple_extent_dims_f(dspace_id, idims, h_maxdims, ierror) 
      if (ierror<0) stop 'error in h5sget_simple_extent_dims'  

      write(3,*)   'reading dataset: ',trim(dsetname)
      write(3,90)  '      rank: ', irank   
      write(3,90)  'dimensions: ', idims(1:irank)
      write(3,90)  '      type: ', type_id 

! Get data

      call h5dread_f(dset_id, type_id, data, idims, ierror) 
      if (ierror.ne.0) then
        write(3,*) 'error reading data set ',trim(dsetname)
        stop       'error in h5dread'
      endif

! close resources
      call h5tclose_f(type_id,ierror)
      if (ierror<0) stop 'error: h5tclose'

      call h5sclose_f(dspace_id, ierror)
      if (ierror<0) stop 'error: h5sclose'

      call h5dclose_f(dset_id, ierror)
      if (ierror<0) stop 'error: h5dclose'

      return
 90   format(2x,a,10(i0,1x))
      end subroutine h_read 
