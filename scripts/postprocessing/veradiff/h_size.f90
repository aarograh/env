!=======================================================================
!
!  Wrapper Subroutine to read an array dimensions from an HDF5 file
!
!=======================================================================
      subroutine h_size(file_id, dsetname, idims)
      USE hdf5 ! This module contains all necessary modules
      implicit none

      character(len=*), intent(in)    :: dsetname     ! Dataset name
      integer(hid_t),   intent(in)    :: file_id      ! File identifier
      integer(hsize_t), intent(out)   :: idims(10)    ! Dataset dimensions

!--- local

      integer(hid_t)   :: type_id        ! flag for dataset type
      integer(hid_t)   :: dset_id        ! Dataset identifier
      integer(hid_t)   :: dspace_id      ! Dataspace identifier
      integer(hsize_t) :: h_maxdims(10)  ! Dataset dimensions
      integer          :: ierror         ! error code

      integer  :: i
      integer  :: irank               ! Dataset rank

      write(3,*)
      write(3,*)   'opening dataset for dimensions: ',trim(dsetname)

! Open the dataset
      call h5dopen_f(file_id, dsetname, dset_id, ierror)
      if (ierror<0) then
        write(3,*) 'data set ',trim(dsetname), ' could not be opened'
        stop       'error in h5dopen'
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

      write(3,*)   'reading dataset dimensions: ',trim(dsetname)
      write(3,90)  '      rank: ', irank   
      write(3,90)  'dimensions: ', idims(1:irank)
      write(3,90)  '      type: ', type_id 

! close resources
      call h5tclose_f(type_id,ierror)
      if (ierror<0) stop 'error: h5tclose'

      call h5sclose_f(dspace_id, ierror)
      if (ierror<0) stop 'error: h5sclose'

      call h5dclose_f(dset_id, ierror)
      if (ierror<0) stop 'error: h5dclose'

      return
 90   format(2x,a,10(i0,1x))
      end subroutine 
