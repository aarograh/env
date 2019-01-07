!=======================================================================
!
!  Subroutine to read character string from HDF5 file
!
!=======================================================================
      subroutine h_readstr(file_id, dataset, stringout)
      use hdf5
      implicit none

      integer(hid_t),   intent(in) :: file_id
      character(len=*), intent(in) :: dataset
      character(len=*), intent(out):: stringout

!--- local

      integer(hid_t)     :: dset_id
      integer(hid_t)     :: type_id
      integer            :: ierror, i

      integer, parameter :: max_dimen=2     ! maximum number of dimensions allowed

      integer(hsize_t)   :: h_dims(max_dimen)
      integer(size_t)    :: strlen

      ierror=0
      stringout=' '    ! initialize

!--- read string

!--- open a dataset

      write (3,'(1x,2a)') 'reading dataset: ', trim(dataset)

      call h5dopen_f(file_id, dataset, dset_id, ierror)
      if (ierror.lt.0) then
        write(3,'(3a)') 'error: data set ',trim(dataset), &
                                ' could not be opened'
        write(3,'(a,i8)') 'error code ', ierror
        stop 'error: h5dopen'
      endif

!--- determine data type (scalars do not use dataspace)

      call h5dget_type_f(dset_id, type_id, ierror)
      if (ierror.ne.0) stop  'error: h5dget_type_f'

!  note that type_id does not match H5T_NATIVE_CHARACTER or H5T_STRING

      call h5tget_size_f(type_id, strlen, ierror)
      if (ierror.ne.0) stop  'error: h5dget_size_f'

      if (strlen.gt.len(stringout)) then
        write (3,*) 'file  strlen   ', strlen
        write (3,*) 'input strlenin ', len(stringout)
        write (3,*) 'error: insufficient string length defined'
        stop        'error: insufficient string length defined'
      endif

! Read data from dataset

      call h5dread_f(dset_id, type_id, stringout, h_dims, ierror)
      if (ierror.ne.0) then
        write(3,*) 'error: h5dread_f reading  data set ',trim(dataset)
        stop
      endif

      do i=1, strlen    ! search for null
        if (ichar(stringout(i:i)).eq.0) then
          stringout(i:i)=' '  ! remove null
        endif
      enddo

! Close datatype and dataset

      call h5tclose_f(type_id, ierror)
      call h5dclose_f(dset_id, ierror)

!     if (ifdebug) write (*,'(1x,3a)') 'debug: read_string >',trim(stringout),'<'

      return
      end subroutine 

      subroutine h_readstrex(file_id, dataset, exists, stringout)
      use hdf5
      implicit none

      integer(hid_t),   intent(in)  :: file_id
      character(len=*), intent(in)  :: dataset
      logical         , intent(out) :: exists
      character(len=*), intent(out) :: stringout

      call h_exists(file_id, dataset, exists)
      if (exists) then
        call h_readstr(file_id, dataset, stringout)
      endif
      return
      end subroutine 
