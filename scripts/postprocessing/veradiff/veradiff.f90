      program hdfdiff
      use hdf5
      use global
      implicit none
      character(len=200)  :: input1,input2   
      character(len=132) :: line 
      integer            :: iargs,i,j,k,l,m,n,nn,ai,aj
      logical            :: exists,exists2
      logical            :: isDenovo1,isDenovo2
      integer(hid_t)     :: file_id1,file_id2
      character(len=11)  :: state1,state2,core1,core2


      integer(hsize_t)   :: idims(10)
      integer            :: ierror
      character(len=80)  :: dname
      character(len=20)  :: cstr
      integer            :: ndz(4),ndz2(4)

      real*8             :: sum,sumsq,sumwgt,maxabs,max,dz,rms,max2,sig,sig2
      real*8             :: avg(2,3),elev
      character(len=19)  :: cpower1, cpower2

      real*8 ,allocatable :: radtmp(:,:)
      integer,allocatable :: radndz(:,:)

      real*8, allocatable :: tempp(:,:,:,:)
      integer,allocatable :: tempc(:,:)
      integer             :: tempi

      integer             :: bins(11),total
      real*8              :: nsigma
      character(len=20)   :: dataset
      integer             :: edittype
   
      dataset='powers'
      edittype=0
!--------------------------------------------------------------------------------
      iargs = command_argument_count()
      if (iargs<2) then
        write(*,*) &
      'usage:  veradiff.exe hdf5_ref hdf5 [STATE1] [STATE2] [rel_error]'
        stop
      endif
      call get_command_argument(1,input1)
      if (index(input1,'.')==0) input1=trim(input1)//'.h5'
      inquire(file=input1, exist=exists)
      if (.not.exists) then
        write(*,*) 'error: input file ',trim(input1),' does not exist'
        stop
      endif

      call get_command_argument(2,input2)
      if (index(input2,'.')==0) input2=trim(input2)//'.h5'
      inquire(file=input2, exist=exists)
      if (.not.exists) then
        write(*,*) 'error: input file ',trim(input2),' does not exist'
        stop
      endif
 
      if (iargs>2) then
        call get_command_argument(3,state1)
      endif

      if (iargs>3) then
        call get_command_argument(4,state2)
      else
        state2=state1
      endif

      if (iargs>4) then
        call get_command_argument(5,line)
        read(line,*) relative_error
      endif
       
! open output and log files file
      open(unit=2,file='veradiff.out',status='unknown')
      open(unit=3,file='veradiff.log',status='unknown')

!--------------------------------------------------------------------------------
      call getcwd(line)

      write(2,*) '=============================================='
      write(2,*) ' VERADIFF - Pin Power Comparisons from VERA   '
      write(2,*) 
      write(2,*) '    Version 0.5 - 8/9/2013'
      write(2,*) '=============================================='
      write(2,*) '       first input: ',trim(input1)
      write(2,*) '      second input: ',trim(input2)
      write(2,*) '       working dir: ',trim(line)
      write(2,*) 'use relative error: ',relative_error
      
!--- Initialize FORTRAN interface.

      call h5open_f(ierror)
      if (ierror.ne.0) stop 'error: h5open_f'

!--- open files 

      call h5fopen_f(input1, H5F_ACC_RDONLY_F, file_id1, ierror)
      if (ierror<0) then
        write(*,*) 'error: H5 input file ',trim(input1), &
            ' could not be opened'
        stop
      endif 
      call h5fopen_f(input2, H5F_ACC_RDONLY_F, file_id2, ierror)
      if (ierror<0) then
        write(*,*) 'error: H5 input file ',trim(input2), &
            ' could not be opened'
        stop
      endif 

!--- set default statepoints if they are not input
   
      if (iargs<=2) then
        call h_exists(file_id1, 'STATE_0001', exists)
        if (exists) then
          state1='STATE_0001/'
        else
          state1=''
        endif

        call h_exists(file_id2, 'STATE_0001', exists)
        if (exists) then
          state2='STATE_0001/'
        else
          state2=''
        endif
      endif
     
      if (len_trim(state1)>0) state1=trim(state1)//'/'
      if (len_trim(state2)>0) state2=trim(state2)//'/'

      write(2,*) 
      write(2,*) ' -- STATEPOINTS --'
      write(2,*) '    REF STATEPOINT: ','/'//trim(state1)
      write(2,*) '   TEST STATEPOINT: ','/'//trim(state2)

!--- make sure keff, pin powers, and core maps are on each file

      dname='/'//trim(state1)//'keff'
      call h_exists(file_id1, dname, exists)
      if (.not.exists) stop 'keff dataset is not on file 1'

      dname='/'//trim(state2)//'keff'
      call h_exists(file_id2, dname, exists)
      if (.not.exists) stop 'keff dataset is not on file 2'

      dname='/'//trim(state1)//'pin_powers'
      call h_exists(file_id1, dname, exists)
      if (.not.exists) stop 'pin_powers dataset is not on file 1'

      dname='/'//trim(state2)//'pin_powers'
      call h_exists(file_id2, dname, exists)
      if (.not.exists) stop 'pin_powers dataset is not on file 2'

      core1='CORE/'
      core2='CORE/'

      call h_exists(file_id1, 'CORE', exists)
      if (exists) then
        dname='/'//trim(core1)//'core_map'
      else
        dname='core_map'
        core1='/'
      endif
      call h_exists(file_id1, dname, exists)
      if (.not.exists) stop 'core_map dataset is not on file 1'

      call h_exists(file_id2, 'CORE', exists)
      if (exists) then
        dname='/'//trim(core2)//'core_map'
      else
        dname='core_map'
        core2='/'
      endif
      call h_exists(file_id2, dname, exists)
      if (.not.exists) stop 'core_map dataset is not on file 2'

!--- get denovo flag (is the file generated by denovo)

      dname='/INPUT_PARAMETER_LIST'
      call h_exists(file_id1, dname, isDenovo1)
      call h_exists(file_id2, dname, isDenovo2)
    
!--- get file version numbers (1 is default)

      call h_readex(file_id1,'version',exists,idims,version1)
      if (.not.exists) version1=1

      call h_exists(file_id1, 'veraout_version', exists)
      if (exists) version1=3

      call h_readex(file_id2,'version',exists,idims,version2)
      if (.not.exists) version2=1
  
      call h_exists(file_id2, 'veraout_version', exists)
      if (exists) version2=3

      write(2,*)
      write(2,'(1x,a,1x,i1)') ' first file version: ',version1,'*'
      write(2,'(1x,a,1x,i1)') 'second file version: ',version2,'*'

!--- get dimensions from pin powers and core map

      dname='/'//trim(core1)//'core_map'
      call h_size(file_id1, dname, idims)
      nsize=idims(1)

      dname='/'//trim(core2)//'core_map'
      call h_size(file_id2, dname, idims)
      nsize2=idims(1)

!     if (nsize==0 .or. nsize2==0) then
!       stop 'core_map indicates 0 assemblies?'
!     endif

      if (nsize/=nsize2) then
        stop 'inconsistent core sizes between files'
      endif

      dname='/'//trim(state1)//'pin_powers'
      call h_size(file_id1, dname, idims)
      if (version1==1) then
        npin=idims(1)
        nassy=idims(4)
        nax=idims(3)
      elseif (version1>=2) then
        npin=idims(3)
        nassy=idims(1)
        nax=idims(2)
      endif

      dname='/'//trim(state2)//'pin_powers'
      call h_size(file_id2, dname, idims)
      if (version2==1) then
        npin2=idims(1)
        nassy2=idims(4)
        nax2=idims(3)
      elseif (version2>=2) then
        npin2=idims(3)
        nassy2=idims(1)
        nax2=idims(2)
      endif

      if (npin2/=npin) then
        stop 'inconsistent assembly sizes between files'
      endif

      if (nassy2/=nassy) then
        write(*,*) 'warning: inconsistent number of assemblies'
      endif

      if (nax2/=nax) then
        stop 'inconsistent number of axial levels between files'
      endif

!-- get symmetry flag (1==full, 4==qtr, none other supported)

      isym=0
      isym2=0

      if (isDenovo1.and.version1<2) then  
        dname='/INPUT_PARAMETER_LIST/STATE/sym'
        call h_readstr(file_id1,dname,cstr)
        if (exists) then
          if (trim(cstr)=='full') then
            isym=1
          elseif (trim(cstr)=='qtr') then
            isym=4
          else
            write(*,*) 'error: sym string',trim(cstr), &
                       'is not valid at this time'
            stop 'unexpected sym dataset value on file 1'
          endif
        endif 
      else
        dname='/'//trim(core1)//'core_sym'
        call h_readex(file_id1,dname,exists,idims,isym)
      endif

      if (isDenovo2.and.version2<2) then  
        dname='/INPUT_PARAMETER_LIST/STATE/sym'
        call h_readstr(file_id2,dname,cstr)
        if (exists) then
          if (trim(cstr)=='full') then
            isym2=1
          elseif (trim(cstr)=='qtr') then
            isym2=4
          else
            write(*,*) 'error: sym string',trim(cstr), &
                       'is not valid at this time'
            stop 'unexpected sym dataset value on file 2'
          endif
        endif 
      else
        dname='/'//trim(core2)//'core_sym'
        call h_readex(file_id2,dname,exists,idims,isym2)
      endif
      
      if (isym==0.and.isym2==0) then
        write(*,*) 'warning: no symmetry detected', &
                       ' - assuming quarter symmetry'
        isym=4
        isym2=4
      elseif (isym==0.and.isym2/=0) then
        write(*,*) 'warning: no symmetry of file 1', &
                       ' - assuming that of file 2'
        isym=isym2
      elseif (isym2==0.and.isym/=0) then
        write(*,*) 'warning: no symmetry of file 2', &
                       ' - assuming that of file 1'
        isym2=isym
      endif

      if (isym/=isym2) then
        write(*,*) 'warning: symmetry mismatch'
      endif

      if (isym/=1 .and. isym/=4) then
        write(*,*) 'unsupported symmetry type for file 1'
      endif

      if (isym2/=1 .and. isym2/=4) then
        write(*,*) 'unsupported symmetry type for file 2'
      endif
!-- check - if nassy and nassy2 are different, nassy must be quarter core
      if (nassy/=nassy2) then
        if (isym/=4 .or. isym2/=1) then
          write(*,*) 'file 1: ',nassy, ' assemblies; ',isym, ' symmetry'
          write(*,*) 'file 2: ',nassy2,' assemblies; ',isym2,' symmetry'
          stop 'error: mismatched assembly numbers require a quarter ' & 
                                   //'core reference'
        endif
      endif


!--- get core map - should always be full geometry

      allocate(coremap(nsize,nsize))
      coremap(:,:)=0
      dname='/'//trim(core1)//'core_map'
      call h_read(file_id1,dname,idims,coremap)

      allocate(coremap2(nsize2,nsize2))
      coremap2(:,:)=0
      dname='/'//trim(core2)//'core_map'
      call h_read(file_id2,dname,idims,coremap2)

!--- if old version, flip core map
      if (version1<2) then
        allocate(tempc(nsize,nsize))
        tempc=coremap
        do i=1,nsize
          do j=1,nsize
            coremap(i,j)=tempc(j,i)
          enddo
        enddo
        deallocate(tempc)
      endif
      if (version2<2) then
        allocate(tempc(nsize2,nsize2))
        tempc=coremap2
        do i=1,nsize
          do j=1,nsize
            coremap2(i,j)=tempc(j,i)
          enddo
        enddo
        deallocate(tempc)
      endif

!--- write geometry

      write(2,*)
      write(2,*)           'problem dimensions:'
      write(2,'(1x,a,i0)') ' number of assemblies = ',nassy
      write(2,'(1x,a,i0)') ' number of assemblies across core = ',nsize
      write(2,'(1x,a,i0)') ' number of pins across = ',npin
      write(2,'(1x,a,i0)') ' number of axial levels = ',nax
      write(2,'(1x,a,i0)') ' core symmetry flag = ',isym
      if (nassy>1) then
        write(2,'(1x,a)')    ' core map (file 1): '
        do j=1,nsize
          write(2,'(3x,20(i3))') (coremap(i,j),i=1,nsize)
        enddo

        write(2,'(1x,a)')    ' core map (file 2): '
        do j=1,nsize2
          write(2,'(3x,20(i3))') (coremap2(i,j),i=1,nsize2)
        enddo
      endif

      if (isym/=1 .and. isym/=4) then
         stop 'only full and quarter core symmetries are permitted'
      endif
      write(*,*)

!--- get eigenvalues and sigmas (if available)

      dname='/'//trim(state1)//'keff'
      call h_read(file_id1,dname,idims,keff1)
      dname='/'//trim(state2)//'keff'
      call h_read(file_id2,dname,idims,keff2)
 
      dname='/'//trim(state1)//'keff_sigma'
      call h_readex(file_id1,dname,exists,idims,ksigma1)
      if (.not.exists) ksigma1=0.0
      isMC1=exists

      dname='/'//trim(state2)//'keff_sigma'
      call h_readex(file_id2,dname,exists,idims,ksigma2)
      if (.not.exists) ksigma2=0.0
      isMC2=exists

      call print_keff(2)
      
!-- allocate arrays 

      allocate(power1(nassy,nax,npin,npin))
      allocate(sigma1(nassy,nax,npin,npin))
      allocate(absig1(nassy,nax,npin,npin))
      allocate(power2(nassy,nax,npin,npin))
      allocate(sigma2(nassy,nax,npin,npin))
      allocate(absig2(nassy,nax,npin,npin))
                                        
      allocate( pdiff(nassy,nax,npin,npin))
      allocate( sdiff(nassy,nax,npin,npin))
      allocate(sigmas(nassy,nax,npin,npin))
      allocate(   wgt(nassy,nax,npin,npin))
      allocate(axmesh(nax+1))

      allocate(pxlo(nassy))
      allocate(pxhi(nassy))
      allocate(pylo(nassy))
      allocate(pyhi(nassy))

      allocate(ffact1(nassy,nax,npin,npin))
      allocate(ffact2(nassy,nax,npin,npin))
      allocate(ffactdiff(nassy,nax,npin,npin))
!-- get pin by pin data

      dname='/'//trim(state1)//'pin_'//trim(dataset)
      if (version1>=2) then
        call h_read(file_id1,dname,idims,power1)
      else
        allocate(tempp(npin,npin,nax,nassy))
        call h_read(file_id1,dname,idims,tempp )
        do l=1,nassy
          do k=1,nax
            do i=1,npin
              do j=1,npin
                power1(l,k,i,j)=tempp(j,i,k,l)
              enddo
            enddo
          enddo
        enddo
        deallocate(tempp)

!-- fix up for denovo -- flipping core map and data
      
        if (nassy>1) then
        if (isDenovo1) then
          write(*,*)
          write(*,*) 'Identified Insilico data - Flipping File 1 Powers'
          allocate(tempp(nassy,nax,npin,npin))
          allocate(tempc(nsize,nsize))
          tempp=0.0
          tempc=0
          if (isym==1) then
            m=1
          else
            m=int(nsize/2)+1
          endif
          do aj=m,nsize
            do ai=m,nsize
              if (coremap(ai,aj)==0) cycle
              write(*,*) '  switching assembly ',coremap(ai,aj),' with ',coremap(aj,ai)
              do k=1,nax
                do i=1,npin
                  do j=1,npin
                    tempp(coremap(aj,ai),k,i,j)=power1(coremap(ai,aj),k,i,j)
                    tempc(aj,ai)=coremap(ai,aj)
                  enddo
                enddo
              enddo
            enddo
          enddo
          power1=tempp
          coremap=tempc
          deallocate(tempp)
          deallocate(tempc)
          write(*,'(1x,a)')    ' core map (file 1): '
          do j=1,nsize
            write(*,'(3x,20(i3))') (coremap(i,j),i=1,nsize)
          enddo
        endif
        endif
      endif
        
      dname='/'//trim(state2)//'pin_'//trim(dataset)
      if (isym2==isym) then
        if (version2>=2) then
          call h_read(file_id2,dname,idims,power2)
        else
          allocate(tempp(npin,npin,nax,nassy))
          call h_read(file_id2,dname,idims,tempp )
          do l=1,nassy
            do k=1,nax
              do i=1,npin
                do j=1,npin
                  power2(l,k,i,j)=tempp(j,i,k,l)
                enddo
              enddo
            enddo
          enddo
          deallocate(tempp)

!-- fix up for denovo -- flipping core map and data

          if (nassy>1) then
          if (isDenovo2) then
          write(*,*) 'Identified Insilico data - Flipping File 2 Powers'
            allocate(tempp(nassy,nax,npin,npin))
            allocate(tempc(nsize,nsize))
            tempp=0.0
            tempc=0
            if (isym2==1) then
              m=1
            else
              m=int(nsize/2)+1
            endif
            do aj=m,nsize
              do ai=m,nsize
                if (coremap2(ai,aj)==0) cycle
               write(*,*) 'switching assembly ',coremap2(ai,aj),' with ',coremap2(aj,ai)
                do k=1,nax
                  do i=1,npin
                    do j=1,npin
                      tempp(coremap2(aj,ai),k,i,j)=power2(coremap2(ai,aj),k,i,j)
                      tempc(aj,ai)=coremap2(ai,aj)
                    enddo
                  enddo
                enddo
              enddo
            enddo
            power2=tempp
            coremap2=tempc
            deallocate(tempp)
            deallocate(tempc)
            write(*,'(1x,a)')    ' core map (file 2): '
            do j=1,nsize
              write(*,'(3x,20(i3))') (coremap2(i,j),i=1,nsize)
            enddo
          endif 
          endif
        endif
      else
        allocate(tempp(nassy2,nax,npin,npin))
        if (version2>=2) then
          call h_read(file_id2,dname,idims,tempp)
        else
          deallocate(power2)
          allocate(power2(npin,npin,nax,nassy2))
          call h_read(file_id2,dname,idims,power2)
          do l=1,nassy
            do k=1,nax
              do i=1,npin
                do j=1,npin
                  tempp(l,k,i,j)=power2(j,i,k,l)
                enddo
              enddo
            enddo
          enddo
          deallocate(power2)
          allocate(power2(nassy,nax,npin,npin))
        endif

! convert second geometry to first
! assume odd number of assemblies

        if (isym==4) then
          write(*,*)
          write(*,*) 'Converting full core data to quarter core'
          power2=0.0
          m=int(nsize/2)+1
          do aj=m,nsize
            do ai=m,nsize
              if (coremap2(ai,aj)/=0) then
                write(*,*) 'Getting assembly ',coremap2(ai,aj), &
                                     ' data for assembly ',coremap(ai,aj)
                do j=1,npin
                  do i=1,npin
                    do k=1,nax
                      power2(coremap(ai,aj),k,i,j)=tempp(coremap2(ai,aj),k,i,j)
                    enddo
                  enddo
                enddo
              endif
            enddo
          enddo
        endif
        deallocate(tempp)
      endif
      
!-- for debugging, print powers
!     write(*,*) 'Debug: pin powers file 1'
!     do l=1,nassy
!       do k=1,nax
!         write(*,*) 'Assembly: ',l,' Level: ',k
!         do j=1,npin
!           write(*,'(17f8.5)') (power1(l,k,i,j),i=1,npin)
!         enddo
!         write(*,*)
!       enddo
!     enddo
!     write(*,*)
!     write(*,*) 'Debug: pin powers file 2'
!     do l=1,nassy
!       do k=1,nax
!         write(*,*) 'Assembly: ',l,' Level: ',k
!         do j=1,npin
!           write(*,'(17f8.5)') (power2(l,k,i,j),i=1,npin)
!         enddo
!         write(*,*)
!       enddo
!     enddo
 
      dname='/'//trim(state1)//'pin_'//trim(dataset)//'_sigma'
      if (isMC1) then
        if (version1>=2) then
          call h_readex(file_id1,dname,exists,idims,sigma1)
        else
          allocate(tempp(npin,npin,nax,nassy))
          call h_readex(file_id1,dname,exists,idims,tempp )
          if (exists) then
            do l=1,nassy
              do k=1,nax
                do i=1,npin
                  do j=1,npin
                    sigma1(l,k,i,j)=tempp(j,i,k,l)
                  enddo
                enddo
              enddo
            enddo
          endif
          deallocate(tempp)
        endif

        if (exists) then
          do l=1,nassy
            do k=1,nax
              do i=1,npin
                do j=1,npin
                  if (power1(l,k,i,j)==0.0) then
                    absig1(l,k,i,j)=0.0
                    sigma1(l,k,i,j)=0.0
                  else
                    absig1(l,k,i,j)=sigma1(l,k,i,j)*power1(l,k,i,j)/100.0
                  endif
                enddo
              enddo
            enddo
          enddo
        else
          sigma1=0.0
          absig1=0.0
        endif
      endif

      dname='/'//trim(state2)//'pin_'//trim(dataset)//'_sigma'
      if (isMC2) then
        if (version2>=2) then
          call h_readex(file_id2,dname,exists,idims,sigma2)
        else
          allocate(tempp(npin,npin,nax,nassy))
          call h_readex(file_id2,dname,exists,idims,tempp )
          if (exists) then
            do l=1,nassy
              do k=1,nax
                do i=1,npin
                  do j=1,npin
                    sigma2(l,k,i,j)=tempp(j,i,k,l)
                  enddo
                enddo
              enddo
            enddo
          endif
          deallocate(tempp)
        endif

        if (exists) then
          do l=1,nassy
            do k=1,nax
              do i=1,npin
                do j=1,npin
                  if (power2(l,k,i,j)==0.0) then
                    absig2(l,k,i,j)=0.0
                    sigma2(l,k,i,j)=0.0
                  else
                    absig2(l,k,i,j)=sigma2(l,k,i,j)*power2(l,k,i,j)/100.0
                  endif
                enddo
              enddo
            enddo
          enddo
        else
          sigma2=0.0
          absig2=0.0
        endif
      endif

      if (dataset=='fueltemps') then
        do j=1,npin
          do i=1,npin
            do k=1,nax
              do l=1,nassy
                if (power1(l,k,i,j)>293) then
                  power1(l,k,i,j)=power1(l,k,i,j)*1.8+32
                else
                  power1(l,k,i,j)=0.0 
                endif
                if (power2(l,k,i,j)>293) then
                  power2(l,k,i,j)=power2(l,k,i,j)*1.8+32
                else
                  power2(l,k,i,j)=0.0 
                endif
              enddo
            enddo
          enddo
        enddo  
      endif

      pdiff=power2-power1

      ! calculate MC uncertainty if required
      if (isMC1.and.isMC2) then
        sdiff=sqrt(absig1**2+absig2**2)
      elseif (isMC1) then
        sdiff=absig1
      elseif (isMC2) then
        sdiff=absig2
      else
        sdiff=0.0
      endif

      ! if relative error, divide by reference power and convert to percent
      if (relative_error) then
        do j=1,npin
          do i=1,npin
            do k=1,nax
              do l=1,nassy
                if (power1(l,k,i,j)==0) then
                  pdiff(l,k,i,j)=0.0
                  sdiff(l,k,i,j)=0.0
                else
                  pdiff(l,k,i,j)=pdiff(l,k,i,j)/power1(l,k,i,j)
                  sdiff(l,k,i,j)=sdiff(l,k,i,j)/power1(l,k,i,j)
                endif
              enddo
            enddo
          enddo
        enddo  
      endif       

      if (edittype==0) then
        pdiff=pdiff*100.0
        sdiff=sdiff*100.0
      endif
       
!-- for debugging, print power diff
!     write(*,*) 'Debug: pin powers differences'
!     do l=1,nassy
!       do k=1,nax
!         do j=1,npin
!           write(*,'(17f8.5)') (pdiff(l,k,i,j),i=1,npin)
!         enddo
!         write(*,*)
!       enddo
!     enddo
!    
!-- get axial mesh
     
      exists=.false.
      do while (.not.exists)

        dname='/'//trim(core1)//'axial_mesh'
        call h_readex(file_id1,dname,exists,idims,axmesh)
        if (exists) cycle

        dname='/'//trim(core2)//'axial_mesh'
        call h_readex(file_id2,dname,exists,idims,axmesh)
        if (exists) cycle

        if (isDenovo1) then
          dname='/INPUT_PARAMETER_LIST/EDITS/axial_edit_bounds'
          call h_readex(file_id1,dname,exists,idims,axmesh)
          if (exists) cycle
        endif

        if (isDenovo2) then
          call h_readex(file_id2,dname,exists,idims,axmesh)
          if (exists) cycle
        endif

        if (nax==1) then
          axmesh(1)=0.0
          axmesh(2)=1.0
          exists=.true.
          cycle
        endif

        stop 'Both files missing axial mesh description'
      enddo

!-- set valid pin ranges
!   only handles full and quarter core symmetry for now

      pxlo(:)=1
      pylo(:)=1
      pxhi(:)=npin
      pyhi(:)=npin
      axlo=1
      axhi=nsize 
      aylo=1
      ayhi=nsize 
      if (isym==4) then
        if (mod(npin,2)==0) then
          stop 'veradiff needs to be evaluated for even pins'
        endif
        m=int(npin/2.0)+1   ! odd pins only
        n=int(nsize/2.0)+1  ! odd assemblies only
        do i=n,nsize
          l=coremap(i,n)
          pylo(l)=m
        enddo
        do j=n,nsize
          l=coremap(n,j)
          pxlo(l)=m
        enddo
        axlo=n             ! odd assemblies only
        aylo=n    
      endif

!     do l=1,nassy
!       write(*,*) l,pxlo(l),pxhi(l),pylo(l),pyhi(l)
!     enddo

!-- generate weighting factors for pins
   
      exists=.false.
      do while (.not.exists)

!- first try to get pin volumes

        dname='/'//trim(core1)//'pin_volumesXXX'   ! disable for now
        call h_readex(file_id1,dname,exists,idims,wgt)
        if (exists) then 
          if (version1<2) then
            allocate(tempp(npin,npin,nax,nassy))
            call h_readex(file_id1,'pin_volumes',exists,idims,tempp)
            do l=1,nassy
              do k=1,nax
                do i=1,npin
                  do j=1,npin
                    wgt(l,k,i,j)=tempp(j,i,k,l)
                  enddo
                enddo
              enddo
            enddo
            deallocate(tempp)
          endif
          cycle
        endif

        dname='/'//trim(core2)//'pin_volumesXXXX' ! disable
        call h_readex(file_id2,dname,exists,idims,wgt)
        if (exists) then 
          if (version2<2) then
            allocate(tempp(npin,npin,nax,nassy))
            call h_readex(file_id2,'pin_volumes',exists,idims,tempp)
            do l=1,nassy
              do k=1,nax
                do i=1,npin
                  do j=1,npin
                    wgt(l,k,i,j)=tempp(j,i,k,l)
                  enddo
                enddo
              enddo
            enddo
            deallocate(tempp)
          endif
          cycle
        endif

!- second try to get pin areas (only for version 2)

        allocate(radpow1(nassy,npin,npin))

        dname='/'//trim(core1)//'pin_areas'
        call h_readex(file_id1,dname,exists,idims,radpow1)
        if (.not.exists) then
          dname='/'//trim(core2)//'pin_areas'
          call h_readex(file_id2,dname,exists,idims,radpow1)
        endif
        if (exists) then
          if (version1<2 .or. version2<2) then
            stop 'pin_areas not supported for file version 1'
          endif
          do j=1,npin
            do i=1,npin
              do k=1,nax
                do l=1,nassy
                  wgt(l,k,i,j)=radpow1(l,i,j)*(axmesh(k+1)-axmesh(k))
                enddo
              enddo
            enddo
          enddo
          deallocate(radpow1)
          cycle
        endif

        deallocate(radpow1)

!- third get radial pin factors and multiple by axial mesh sizes
!- prior to veraout version 1 pin_factors are radial

        dname='/'//trim(core1)//'pin_factors'
        call h_readex(file_id1,dname,exists,idims,wgt)
        if (exists .and. version1==3) cycle
        if (.not.exists) then
          dname='/'//trim(core2)//'pin_factors'
          if (isym==isym2) then
            call h_readex(file_id2,dname,exists,idims,wgt)
          else if (isym==4 .and. isym2==1) then
             ! don't even try it
            !allocate(tempp(nassy2,nax,npin,npin))
            !call h_readex(file_id2,dname,exists,idims,tempp)
            !write(*,*)
            !write(*,*)'Converting full core pin factors to quarter core'
            !write(*,*)' warning-- assuming odd assemblies and pins and '
            !write(*,*)'          reducing the weight factor of the pins'
            !write(*,*)'          on the axes by factor of 2'
            !wgt=0.0
            !m=int(nsize/2)+1
            !do aj=m,nsize
            !  do ai=m,nsize
            !    if (coremap2(ai,aj)/=0) then
            !      write(*,*) 'Getting assembly ',coremap2(ai,aj), &
            !                           ' factors for assembly ',coremap(ai,aj)
            !      do j=1,npin
            !        do i=1,npin
            !          do k=1,nax
            !            l=coremap(ai,aj)
            !            if (i<pxlo(l)) then
            !              wgt(l,k,i,j)=0.0
            !            else if (j<pylo(l)) then
            !              wgt(l,k,i,j)=0.0
            !            else
            !              wgt(l,k,i,j)=tempp(coremap2(ai,aj),k,i,j)
            !            endif
            !            if (i==pxlo(l)) wgt(l,k,i,j)=wgt(l,k,i,j)/2.0
            !            if (j==pylo(l)) wgt(l,k,i,j)=wgt(l,k,i,j)/2.0
            !          enddo
            !        enddo
            !      enddo
            !    endif
            !  enddo
            !enddo
            !deallocate(tempp)

          else
            stop 'bad symmetry combinations'
          endif
        endif
        if (exists .and. version2==3) cycle

!- fourth calculate radial pin factors 
        if (.not.exists) then
          write(*,*) 'calculating pin_factors...'
          ! assume weighting factors are uniform for rods
          ! with power in the valid range of symmetry
          wgt=0.0
          do l=1,nassy
            do j=pylo(l),pyhi(l)
              do i=pxlo(l),pxhi(l)
                do k=1,nax
                  if (power1(l,k,i,j)>0.0001) then
                    wgt(l,k,i,j)=1.0                                 
                  endif
                enddo
              enddo
            enddo
          enddo

          ! if symmetry is quarter, fix up north and west pins
          if (isym==4) then
            do l=1,nassy
              if (pylo(l)>1) then
                do i=1,npin
                  do k=1,nax
                    wgt(l,k,i,pylo(l))=wgt(l,k,i,pylo(l))/2.0
                  enddo
                enddo
              endif
              if (pxlo(l)>1) then
                do j=1,npin
                  do k=1,nax
                    wgt(l,k,pxlo(l),j)=wgt(l,k,pxlo(l),j)/2.0
                  enddo
                enddo
              endif
            enddo
          endif

          n=int(nax/2.0)+1
          write(2,*)
          write(2,'(1x,a,i0)') 'Sample Geometry Factors - Level ',n
          write(2,*) '-------------------------------------------------'
          do l=1,nassy
            write(2,'(1x,a,i0)') 'Assembly ',l
            do j=pylo(l),pyhi(l)
              write(2,'(1x,17(f6.3))') (wgt(l,n,i,j),i=pxlo(l),pxhi(l))
            enddo
          enddo

          exists=.true.
        endif

        !multiply radial factors by axial mesh dz
        if (exists) then
          do j=1,npin
            do i=1,npin
              do k=1,nax
                do l=1,nassy
                  wgt(l,k,i,j)=wgt(l,k,i,j)*(axmesh(k+1)-axmesh(k))
                enddo
              enddo
            enddo
          enddo
          cycle
        endif
          
        stop 'unable to determine weighting factors for normalization'
      enddo

!-- debugging print weighting factors
!
!     write(*,*) 'Debug: weight factors'
!     do l=1,nassy
!       do k=1,nax
!         do j=1,npin
!           write(*,'(17f8.5)') (wgt(l,k,i,j),i=1,npin)
!         enddo
!         write(*,*)
!       enddo
!     enddo
!
!     write(*,*) 'Debug: powers'
!     do l=1,nassy
!       do k=1,nax
!         do j=1,npin
!           write(*,'(17f8.5)') (power1(l,k,i,j),i=1,npin)
!         enddo
!         write(*,*)
!       enddo
!     enddo
!
!-- print axial mesh
      write(2,*)
      write(2,*) 'AXIAL MESH'
      write(2,*)
      write(2,*) ' Level  Upper Bound  Thickness'
      write(2,*) '--------------------------------'
      do k=nax,1,-1
        write(2,69) k,axmesh(k+1),axmesh(k+1)-axmesh(k)
      enddo
      write(2,*) '--------------------------------'
 69   format(3x,i3,4x,f8.4,4x,f7.4)
      
!-- write pin data 
      write(2,*)
      write(2,*) '3D PIN POWERS'
      do l=1,nassy
        write(2,*)
        write(2,'(1x,a,i0)') 'Assembly = ',l
        write(2,*) '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
        do k=nax,1,-1
          write(2,'(2x,a,i0)') ' Axial Level = ',k
          write(2,*) ' ================================================'
          write(2,*) '  Reference Pin Powers - File 1'
          write(2,*) '  -----------------------------------------------'
          do j=pylo(l),pyhi(l)
            if (edittype==0) then
              write(2,'(2x,17(f8.5))') (power1(l,k,i,j),i=pxlo(l),pxhi(l))
            else
              write(2,'(2x,17(f8.3))') (power1(l,k,i,j),i=pxlo(l),pxhi(l))
            endif
          enddo
          if (isMC1) then
          write(2,*) '  -----------------------------------------------'
          write(2,*) '  Reference Pin Power Uncertainty (%) - File 1'
          write(2,*) '  -----------------------------------------------'
          do j=pylo(l),pyhi(l)
            write(2,'(2x,17(f7.3,"%"))') (sigma1(l,k,i,j),i=pxlo(l),pxhi(l))
          enddo
          endif
          write(2,*) '  -----------------------------------------------'
          write(2,*) '  Alternate Pin Powers - File 2'
          write(2,*) '  -----------------------------------------------'
          do j=pylo(l),pyhi(l)
            if (edittype==0) then
              write(2,'(2x,17(f8.5))') (power2(l,k,i,j),i=pxlo(l),pxhi(l))
            else
              write(2,'(2x,17(f8.3))') (power2(l,k,i,j),i=pxlo(l),pxhi(l))
            endif
          enddo
          if (isMC2) then
          write(2,*) '  -----------------------------------------------'
          write(2,*) '  Alternate Pin Power Uncertainty (%) - File 2'
          write(2,*) '  -----------------------------------------------'
          do j=pylo(l),pyhi(l)
            write(2,'(2x,17(f7.3,"%"))') (sigma2(l,k,i,j),i=pxlo(l),pxhi(l))
          enddo
          endif
          write(2,*) '  -----------------------------------------------'
          write(2,*) '  Pin Power Difference (%) - 2-1'
          write(2,*) '  -----------------------------------------------'
          do j=pylo(l),pyhi(l)
            if (edittype==0) then
              write(2,'(2x,17(f7.3,"%"))') (pdiff(l,k,i,j),i=pxlo(l),pxhi(l))
            else
              write(2,'(2x,17(f8.3))') (pdiff(l,k,i,j),i=pxlo(l),pxhi(l))
            endif
          enddo
          if (isMC1.or.isMC2) then
          write(2,*) '  -----------------------------------------------'
          write(2,*) '  Difference Uncertainty (%)'
          write(2,*) '  -----------------------------------------------'
          do j=pylo(l),pyhi(l)
            write(2,'(2x,17(f7.3,"%"))') (sdiff(l,k,i,j),i=pxlo(l),pxhi(l))
          enddo
          endif
          write(2,*) '  -----------------------------------------------'
        enddo
      enddo
      write(2,*)

!-- maximum 3D difference by axial level

      write(2,*)
      write(2,*) 'MAXIMUM POWER DIFFERENCES BY AXIAL LEVEL'
      write(2,*)
      write(2,'(1x,2a)') ' Level   Height        Reference            ',&

                   'Alternate         Max Power Diff    Assy   Rod' 
      write(2,'(94("-"))') 

      max2=0.0
      ndz(:)=1
      do k=nax,1,-1
        max=0.0
        do l=1,nassy
          do i=pxlo(l),pxhi(l)
            do j=pylo(l),pyhi(l)
              if (abs(pdiff(l,k,i,j))>max) then
                max=abs(pdiff(l,k,i,j))
                ndz(1)=l 
                ndz(2)=k 
                ndz(3)=i 
                ndz(4)=j 
              endif
            enddo
          enddo
        enddo
        if (max>max2) then
          max2=max
          ndz2=ndz
        endif

        j=ndz(4)
        i=ndz(3)
        l=ndz(1)

        call powerstr(power1(l,k,i,j),sigma1(l,k,i,j),isMC1,cpower1,edittype)
        call powerstr(power2(l,k,i,j),sigma2(l,k,i,j),isMC2,cpower2,edittype)

        elev=(axmesh(k+1)+axmesh(k))/2.0
        if (edittype==0) then
          write(2,36), k,elev,cpower1,cpower2,pdiff(l,k,i,j), &
                           sdiff(l,k,i,j),ndz(1),ndz(3),ndz(4)
        else
          write(2,38), k,elev,cpower1,cpower2,pdiff(l,k,i,j), &
                           sdiff(l,k,i,j),ndz(1),ndz(3),ndz(4)
        endif
      enddo
      write(2,'(94("-"))') 
      write(2,37) ' Maximum difference = ',max2,'at level',ndz2(2), &
          'in assembly',ndz2(1),'in pin',ndz2(3),ndz2(4)

 36   format(3x,i3,2x,f9.4,2(2x,a19),2x,f7.3,'% +/-',f6.3,'%', &
                                  2x,i2,2x,'[',i0,',',i0,']')
 37   format(a,f7.3,'%',1x,a,1x,i0,1x,a,1x,i0,1x,a,' [',i0,',',i0,']')

 38   format(3x,i3,2x,f9.4,2(2x,a19),2x,f8.3,' +/-',f6.3,'%', &
                                  2x,i2,2x,'[',i0,',',i0,']')
!-- Maximum 3D Differences by 2D radial pins 

      allocate(radtmp(npin,npin)) 
      allocate(radndz(npin,npin)) 

      write(2,*)
      write(2,*) 'MAXIMUM POWER DIFFERENCES (2-1) BY 2D PIN'

      max2=0.0
      do l=1,nassy
        do i=pxlo(l),pxhi(l)
          do j=pylo(l),pyhi(l)
            radtmp(i,j)=0.0
            do k=nax,1,-1
              if (abs(pdiff(l,k,i,j))>radtmp(i,j)) then
                radtmp(i,j)=abs(pdiff(l,k,i,j))
                radndz(i,j)=k 
              endif
            enddo
            if (radtmp(i,j)>max2) then
              max2=radtmp(i,j)
              ndz(1)=l
              ndz(2)=radndz(i,j)
              ndz(3)=i
              ndz(4)=j
            endif
          enddo
        enddo

        write(2,*)
        write(2,'(1x,a,i0)') 'Assembly = ',l
        write(2,*) '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
        write(2,*) ' Maximum Difference (%)'
        write(2,*) ' --------------------------------------------------'
        do j=pylo(l),pyhi(l)
          if (edittype==0) then
            write(2,'(2x,17(f7.3,"%"))') (radtmp(i,j),i=pxlo(l),pxhi(l))
          else
            write(2,'(2x,17(f8.3))') (radtmp(i,j),i=pxlo(l),pxhi(l))
          endif
        enddo
        if (isMC1 .or. isMC2) then
        write(2,*) ' --------------------------------------------------'
        write(2,*) ' Uncertainty for Maximum Difference (%)'
        write(2,*) ' --------------------------------------------------'
        do j=pylo(l),pyhi(l)
       !  write(2,'(2x,17(f7.3,"%"))') (sdiff(l,radndz(i,j),i,j),i=pxlo(l),pxhi(l))
        enddo
        endif
        write(2,*) ' --------------------------------------------------'
        write(2,*) ' Maximum Difference Axial Plane'
        write(2,*) ' --------------------------------------------------'
        do j=pylo(l),pyhi(l)
          write(2,'(2x,17(3x,i2,3x))') (radndz(i,j),i=pxlo(l),pxhi(l))
        enddo
      enddo
      write(2,*) ' --------------------------------------------------'
      write(2,37) ' Maximum difference = ',max2,'at level',ndz(2), &
          'in assembly',ndz(1),'in pin',ndz(3),ndz(4)

!-- 1D axial results

      allocate(   axpow1(nax)) 
      allocate(   axpow2(nax)) 
      allocate(   axsig1(nax)) 
      allocate(   axsig2(nax)) 
      allocate(   axpsg1(nax)) 
      allocate(   axpsg2(nax)) 
      allocate(axpowdiff(nax))
      allocate(axsigdiff(nax))

      write(2,*)
      write(2,*) 'AXIAL POWERS (File 1)'
      call axial(file_id1,power1,absig1,isMC1,axpow1,axsig1,axpsg1,axial_offset1,dataset)

      write(2,*)
      write(2,*) 'AXIAL POWERS (File 2)'
      call axial(file_id2,power2,absig2,isMC2,axpow2,axsig2,axpsg2,axial_offset2,dataset)

      axpowdiff=axpow2-axpow1
      if (isMC1 .and. isMC2) then
        axsigdiff=sqrt(axsig2**2+axsig1**2)
      else if (isMC1) then
        axsigdiff=axsig1
      else if (isMC2) then
        axsigdiff=axsig2
      else
        axsigdiff=0.0
      endif
      if (relative_error) then
        do k=1,nax
          if (axpow1(k)==0) then
            axpowdiff(k)=0.0
          else
            axpowdiff(k)=axpowdiff(k)/axpow1(k)
          endif
        enddo
      endif
      axpowdiff=axpowdiff*100.0

      write(2,*)
      write(2,*) 'AXIAL POWER DIFFERENCES (2-1)'
      write(2,*)
      write(2,*) ' Level   Height        Reference            Alternate' &
                 //'         Axial Power Diff  '
      write(2,'(81("-"))') 

      max=0.0
      sum=0.0
      rms=0.0
      sumwgt=0.0
      do k=nax,1,-1
        elev=(axmesh(k+1)+axmesh(k))/2.0
        call powerstr(axpow1(k),axsig1(k),isMC1,cpower1,edittype)
        call powerstr(axpow2(k),axsig2(k),isMC2,cpower2,edittype)

        write(2,76), k,elev,cpower1,cpower2,axpowdiff(k),axsigdiff(k)

        dz=axmesh(k+1)-axmesh(k)
        Sum=sum+axpowdiff(k)*dz
        rms=rms+axpowdiff(k)**2*dz
        sumwgt=sumwgt+dz
        if (abs(axpowdiff(k))>max) then
          max=abs(axpowdiff(k))
          ndz(1)=k
        endif
      enddo
      write(2,'(81("-"))') 
      write(2,77) ' Average difference = ',sum/sumwgt
      write(2,77) '     RMS difference = ',sqrt(rms/sumwgt)
      write(2,78) ' Maximum difference = ',max,'at level',ndz(1)
      write(2,35) '      AO difference = ',axial_offset2-axial_offset1

 76   format(3x,i3,2x,f9.4,2(2x,a19),2x,f7.3,'% +/-',f6.3,'%')
 77   format(a,f7.3,'%')
 78   format(a,f7.3,'%',1x,a,1x,i0)
 35   format(a,f7.3,'%')

!-- 2D radial results 

      allocate(   radpow1(nassy,npin,npin)) 
      allocate(   radpow2(nassy,npin,npin)) 
      allocate(   radsig1(nassy,npin,npin)) 
      allocate(   radsig2(nassy,npin,npin)) 
      allocate(   radpsg1(nassy,npin,npin)) 
      allocate(   radpsg2(nassy,npin,npin)) 
      allocate(radpowdiff(nassy,npin,npin))
      allocate(radsigdiff(nassy,npin,npin))
      allocate(    radwgt(nassy,npin,npin))

      radwgt(:,:,:)=0.0
      do k=1,nax
        do j=1,npin
          do i=1,npin
            do l=1,nassy
              radwgt(l,i,j)=radwgt(l,i,j)+wgt(l,k,i,j)
            enddo
          enddo
        enddo
      enddo

      write(2,*)
      write(2,*) 'RADIAL POWERS (File 1)'
      call radial(file_id1,power1,absig1,isMC1,radpow1,radsig1,radpsg1,version1,dataset)

      write(2,*)
      write(2,*) 'RADIAL POWERS (File 2)'
      call radial(file_id2,power2,absig2,isMC2,radpow2,radsig2,radpsg2,version2,dataset)

      radpowdiff=radpow2-radpow1
      if (isMC1 .and. isMC2) then
        radsigdiff=sqrt(radsig2**2+radsig1**2)
      else if (isMC1) then
        radsigdiff=radsig1
      else if (isMC2) then
        radsigdiff=radsig2
      else
        radsigdiff=0.0
      endif
      if (isMC1 .or. isMC2) then
      endif
      if (relative_error) then
        do j=1,npin
          do i=1,npin
            do l=1,nassy
              if (radpow1(l,i,j)==0) then
                radpowdiff(l,i,j)=0.0
              else
                radpowdiff(l,i,j)=radpowdiff(l,i,j)/radpow1(l,i,j)
              endif
            enddo
          enddo
        enddo
      endif
      radpowdiff=radpowdiff*100.0

      write(2,*)
      write(2,*) 'RADIAL POWER DIFFERENCES (2-1)'
      do l=1,nassy
        write(2,*)
        write(2,'(1x,a,i0)') 'Assembly = ',l
        write(2,*) '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
        write(2,*) ' Radial Power Difference'
        write(2,*) ' --------------------------------------------------'
        do j=pylo(l),pyhi(l)
          if (edittype==0) then
            write(2,'(2x,17(f7.3,"%"))') (radpowdiff(l,i,j),i=pxlo(l),pxhi(l))
          else
            write(2,'(2x,17(f8.3))') (radpowdiff(l,i,j),i=pxlo(l),pxhi(l))
          endif
        enddo
        if (isMC1 .or. isMC2) then
        write(2,*) ' --------------------------------------------------'
        write(2,*) ' Radial Power Difference Uncertainty'
        write(2,*) ' --------------------------------------------------'
        do j=pylo(l),pyhi(l)
          write(2,'(2x,17(f7.3,"%"))') (radsigdiff(l,i,j),i=pxlo(l),pxhi(l))
        enddo
        endif
      enddo
      write(2,*) ' --------------------------------------------------'

      sum=0.0
      rms=0.0
      max=0.0
      sumwgt=0.0
      ndz(:)=0
      do l=1,nassy
        do i=pxlo(l),pxhi(l)
          do j=pylo(l),pyhi(l)
            sum=sum+radpowdiff(l,i,j)*radwgt(l,i,j)
            rms=rms+radpowdiff(l,i,j)**2*radwgt(l,i,j)
            sumwgt=sumwgt+radwgt(l,i,j)
            if (abs(radpowdiff(l,i,j))>max) then
              max=abs(radpowdiff(l,i,j))
              ndz(1)=l
              ndz(2)=i
              ndz(3)=j
            endif
          enddo
        enddo
      enddo
      write(2,77) ' Average difference = ',sum/sumwgt
      write(2,77) '     RMS difference = ',sqrt(rms/sumwgt)
      write(2,51) ' Maximum difference = ',max,'in assembly',ndz(1), &
                        'at pin',ndz(2),ndz(3)

 51   format(a,f7.3,'%',1x,a,1x,i0,1x,a,1x,'[',i0,',',i0,']')


!-- 3D assembly power results
     
      allocate(asspow1(nassy,nax))
      allocate(asspow2(nassy,nax))  
      allocate(asssig1(nassy,nax))  
      allocate(asssig2(nassy,nax))  
      allocate(asspsg1(nassy,nax))  
      allocate(asspsg2(nassy,nax))  
      allocate(asspowdiff(nassy,nax))
      allocate(asssigdiff(nassy,nax))
      allocate(asswgt(nassy,nax))

      asswgt(:,:)=0.0
      do k=1,nax
        do l=1,nassy
          do j=1,npin
            do i=1,npin
              asswgt(l,k)=asswgt(l,k)+wgt(l,k,i,j)
            enddo
          enddo
        enddo
      enddo

      if (nassy>1) write(2,*)
      if (nassy>1) write(2,*) 'ASSEMBLY POWERS (File 1)'
      call assembly(file_id1,power1,absig1,isMC1,asspow1,asssig1,asspsg1,1,version1,dataset)

      if (nassy>1) write(2,*)
      if (nassy>1) write(2,*) 'ASSEMBLY POWERS (File 2)'
      call assembly(file_id2,power2,absig2,isMC2,asspow2,asssig2,asspsg2,2,version2,dataset)

      asspowdiff=(asspow2-asspow1)*100.0
      if (isMC1 .and. isMC2) then
        asssigdiff=sqrt(asssig2**2+asssig1**2)
      else if (isMC1) then
        asssigdiff=asssig1
      else if (isMC2) then
        asssigdiff=asssig2
      else
        asssigdiff=0.0
      endif
      if (relative_error) then
        asspowdiff=asspowdiff/asspow1
      endif

      if (nassy>1) then
      write(2,*)
      write(2,*) 'ASSEMBLY POWER DIFFERENCES (2-1)'
      do k=nax,1,-1
        write(2,*)
        write(2,'(1x,a,i0)') 'Axial Level = ',k
        write(2,*) '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
        write(2,*) ' Assembly Power Difference'
        write(2,*) ' --------------------------------------------------'
        do j=aylo,ayhi
          write(2,'("  ")',advance='no')
          do i=axlo,axhi
            l=coremap(i,j)
            if (l/=0) then
              if (edittype==0) then
                write(2,'(f7.3,"%")',advance='no') asspowdiff(l,k)
              else
                write(2,'(f8.3)',advance='no') asspowdiff(l,k)
              endif
            else
              write(2,'(a8)',advance='no') '        '                   
            endif
          enddo
          write(2,*)
        enddo
        if (isMC1 .or. isMC2) then
        write(2,*) ' --------------------------------------------------'
        write(2,*) ' Assembly Power Difference Uncertainty'
        write(2,*) ' --------------------------------------------------'
        do j=aylo,ayhi
          write(2,'("  ")',advance='no')
          do i=axlo,axhi
            l=coremap(i,j)
            if (l/=0) then
              write(2,'(f7.3,"%")',advance='no') asssigdiff(l,k)
            else
              write(2,'(a8)',advance='no') '        '                   
            endif
          enddo
          write(2,*)
        enddo
        endif
      enddo
      write(2,*) ' --------------------------------------------------'

      sum=0.0
      rms=0.0
      max=0.0
      sumwgt=0.0
      ndz(:)=0
      do k=1,nax
        do l=1,nassy
          sum=sum+asspowdiff(l,k)*asswgt(l,k)
          rms=rms+asspowdiff(l,k)**2*asswgt(l,k)
          sumwgt=sumwgt+asswgt(l,k)
          if (abs(asspowdiff(l,k))>max) then
            max=abs(asspowdiff(l,k))
            ndz(1)=l
            ndz(2)=k
          endif
        enddo
      enddo
      write(2,77) ' Average difference = ',sum/sumwgt
      write(2,77) '     RMS difference = ',sqrt(rms/sumwgt)
      write(2,53) ' Maximum difference = ',max,'in assembly',ndz(1), &
                        'at level ',ndz(2)
      endif
 53   format(a,f7.3,'%',1x,a,1x,i0,1x,a,1x,i0)

!-- 2D assembly power results
     
      allocate(ardpow1(nassy))
      allocate(ardpow2(nassy))  
      allocate(ardsig1(nassy))  
      allocate(ardsig2(nassy))  
      allocate(ardpsg1(nassy))  
      allocate(ardpsg2(nassy))  
      allocate(ardpowdiff(nassy))
      allocate(ardsigdiff(nassy))
      allocate(ardwgt(nassy))

      ardwgt(:)=0.0
      do l=1,nassy
        do k=1,nax
          ardwgt(l)=ardwgt(l)+asswgt(l,k)
        enddo
      enddo

      if (nassy>1) then
        write(2,*)
        write(2,*) 'RADIAL ASSEMBLY POWER DIFFERENCES (2-1)'
      endif

      call radassy(file_id1,power1,absig1,isMC1,ardpow1,ardsig1,ardpsg1,1,version1,dataset)
      call radassy(file_id2,power2,absig2,isMC2,ardpow2,ardsig2,ardpsg2,2,version2,dataset)

      ardpowdiff=(ardpow2-ardpow1)*100.0
      if (isMC1 .and. isMC2) then
        ardsigdiff=sqrt(ardsig2**2+ardsig1**2)
      else if (isMC1) then
        ardsigdiff=ardsig1
      else if (isMC2) then
        ardsigdiff=ardsig2
      else
        ardsigdiff=0.0
      endif
      if (relative_error) then
        ardpowdiff=ardpowdiff/ardpow1
      endif

      if (nassy>1) then
      write(2,*)
      write(2,*) '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
      write(2,*) ' Assembly Power Difference'
      write(2,*) ' --------------------------------------------------'
      do j=aylo,ayhi
        write(2,'("  ")',advance='no')
        do i=axlo,axhi
          l=coremap(i,j)
          if (l/=0) then
            if (edittype==0) then
              write(2,'(f7.3,"%")',advance='no') ardpowdiff(l)
            else
              write(2,'(f8.3)',advance='no') ardpowdiff(l)
            endif
          else
            write(2,'(a8)',advance='no') '        '                   
          endif
        enddo
        write(2,*)
      enddo
      if (isMC1 .or. isMC2) then
      write(2,*) ' --------------------------------------------------'
      write(2,*) ' Assembly Power Difference Uncertainty'
      write(2,*) ' --------------------------------------------------'
      do j=aylo,ayhi
        write(2,'("  ")',advance='no')
        do i=axlo,axhi
          l=coremap(i,j)
          if (l/=0) then
            write(2,'(f7.3,"%")',advance='no') ardsigdiff(l)
          else
            write(2,'(a8)',advance='no') '        '                   
          endif
        enddo
        write(2,*)
      enddo
      endif
      write(2,*) ' --------------------------------------------------'

      sum=0.0
      rms=0.0
      max=0.0
      sumwgt=0.0
      ndz(:)=0
      do l=1,nassy
        sum=sum+ardpowdiff(l)*ardwgt(l)
        rms=rms+ardpowdiff(l)**2*ardwgt(l)
        sumwgt=sumwgt+ardwgt(l)
        if (abs(ardpowdiff(l))>max) then
          max=abs(ardpowdiff(l))
          ndz(1)=l
        endif
      enddo
      write(2,77) ' Average difference = ',sum/sumwgt
      write(2,77) '     RMS difference = ',sqrt(rms/sumwgt)
      write(2,53) ' Maximum difference = ',max,'in assembly',ndz(1)
      endif

!-- pin power form factor results

      if (nassy==1) then
        asspow1(1,:)=axpow1(:)
        asspow2(1,:)=axpow2(:)
      endif
      do k=1,nax 
        do l=1,nassy
          do j=1,npin
            do i=1,npin
              if (asspow1(l,k)==0) then
                ffact1(l,k,i,j)=0
              else
                ffact1(l,k,i,j)=power1(l,k,i,j)/asspow1(l,k)
              endif
              if (asspow2(l,k)==0) then
                ffact2(l,k,i,j)=0
              else
                ffact2(l,k,i,j)=power2(l,k,i,j)/asspow2(l,k)
              endif
              ffactdiff(l,k,i,j)=(ffact2(l,k,i,j)-ffact1(l,k,i,j))*100.0
              if (relative_error) then
                if (ffact1(l,k,i,j)==0) then
                  ffactdiff(l,k,i,j)=0
                else
                  ffactdiff(l,k,i,j)=ffactdiff(l,k,i,j)/ffact1(l,k,i,j)
                endif
              endif
            enddo
          enddo
        enddo
      enddo
 
      write(2,*)
      write(2,*) 'MAXIMUM FORM FACTOR DIFFERENCES BY AXIAL LEVEL (2-1)'
      write(2,*)
      write(2,'(1x,2a)') ' Level   Height   Reference ',&
                   'Alternate  Max Diff  Assy  Rod' 

      write(2,'(62("-"))') 

      max2=0.0
      ndz2(:)=0
      do k=nax,1,-1
        max=0.0
        ndz(:)=0.0
        do l=1,nassy
          do i=pxlo(l),pxhi(l)
            do j=pylo(l),pyhi(l)
              if (abs(ffactdiff(l,k,i,j))>max) then
                max=abs(ffactdiff(l,k,i,j))
                ndz(1)=l 
                ndz(2)=k 
                ndz(3)=i 
                ndz(4)=j 
              endif
            enddo
          enddo
        enddo

        if (max>max2) then
          max2=max
          ndz2=ndz
        endif

        j=ndz(4)
        i=ndz(3)
        l=ndz(1)

        elev=(axmesh(k+1)+axmesh(k))/2.0
        write(2,52), k,elev,ffact1(l,k,i,j),ffact2(l,k,i,j),max, &
                         ndz(1),ndz(3),ndz(4)
      enddo
      write(2,'(62("-"))') 
      write(2,37) ' Maximum difference = ',max2,'at level',ndz2(2), &
          'in assembly',ndz2(1),'in pin',ndz2(3),ndz2(4)

 52   format(3x,i3,2x,f9.4,2(2x,f8.5),2x,f7.3,'%',&
                                  2x,i2,2x,'[',i0,',',i0,']')

!-- error in peak pin power and locations

      max=0.0
      sig=0.0
      ndz(:)=0
      max2=0.0
      sig2=0.0
      ndz2(:)=0
      do k=1,nax    
        do l=1,nassy
          do i=pxlo(l),pxhi(l)
            do j=pylo(l),pyhi(l)
              if (power1(l,k,i,j)>max) then
                max=power1(l,k,i,j)              
                sig=sigma1(l,k,i,j)              
                ndz(1)=l 
                ndz(2)=k 
                ndz(3)=i 
                ndz(4)=j 
              endif
              if (power2(l,k,i,j)>max2) then
                max2=power2(l,k,i,j)              
                sig2=sigma2(l,k,i,j)              
                ndz2(1)=l 
                ndz2(2)=k 
                ndz2(3)=i 
                ndz2(4)=j 
              endif
            enddo
          enddo
        enddo
      enddo
      
      write(2,*)
      write(2,*) 'DIFFERENCES IN MAXIMUM PIN POWERS'
      call print_peaks(max,max2,sig,sig2,ndz,ndz2)
      
!-- calculate 3D total average, max abs, and rms difference

      sum=0.0
      sumsq=0.0
      sumwgt=0.0
      maxabs=0.0
      avg(:,:)=0.0

      do k=1,nax
        do l=1,nassy
          do j=pylo(l),pyhi(l)
            do i=pxlo(l),pxhi(l)
              avg(1,1)=avg(1,1)+power1(l,k,i,j)   *wgt(l,k,i,j)
              avg(2,1)=avg(2,1)+power2(l,k,i,j)   *wgt(l,k,i,j)
              avg(1,2)=avg(1,2)+absig1(l,k,i,j)**2*wgt(l,k,i,j)**2
              avg(2,2)=avg(2,2)+absig2(l,k,i,j)**2*wgt(l,k,i,j)**2
              avg(1,3)=avg(1,3)+absig1(l,k,i,j)**2*wgt(l,k,i,j)
              avg(2,3)=avg(2,3)+absig2(l,k,i,j)**2*wgt(l,k,i,j)
 
              sum  =sum  +pdiff(l,k,i,j)   *wgt(l,k,i,j)
              sumsq=sumsq+pdiff(l,k,i,j)**2*wgt(l,k,i,j)
              sumwgt=sumwgt+wgt(l,k,i,j)
 
              if (abs(pdiff(l,k,i,j))>maxabs) then
                maxabs=abs(pdiff(l,k,i,j))
                ndz(1)=l
                ndz(2)=k
                ndz(3)=i
                ndz(4)=j
              endif
             
            enddo
          enddo
        enddo
      enddo
 
      avg(1,1)=avg(1,1)/sumwgt
      avg(2,1)=avg(2,1)/sumwgt
      avg(1,2)=sqrt(avg(1,2)/sumwgt)/sqrt(sumwgt)/avg(1,1)*100.0
      avg(2,2)=sqrt(avg(2,2)/sumwgt)/sqrt(sumwgt)/avg(2,1)*100.0
      avg(1,3)=sqrt(avg(1,3)/sumwgt)/avg(1,1)*100.0
      avg(2,3)=sqrt(avg(2,3)/sumwgt)/avg(2,1)*100.0

!-- print summary

      write(2,*)
      write(2,*) 'RESULTS SUMMARY'
      write(2,*) 
      write(2,*) 'Summary of Reference Power Distribution - File 1'
      write(2,*) '----------------------------------------------------'
      if (edittype==0) then
        write(2,'(a,f8.5)')     '         Average Power = ',avg(1,1)
      else
        write(2,'(a,f8.3)')     '         Average Power = ',avg(1,1)
      endif
      if (isMC1) then
      write(2,'(a,f6.3,"%")') ' Estimated Uncertainty = ',avg(1,2)
      write(2,'(a,f6.3,"%")') '   Avg Pin Uncertainty = ',avg(1,3)
      endif

      write(2,*) 
      write(2,*) 'Summary of Alternate Power Distribution - File 2'
      write(2,*) '----------------------------------------------------'
      if (edittype==0) then
        write(2,'(a,f8.5)')     '         Average Power = ',avg(2,1)
      else
        write(2,'(a,f8.3)')     '         Average Power = ',avg(2,1)
      endif
      if (isMC2) then
      write(2,'(a,f6.3,"%")') ' Estimated Uncertainty = ',avg(2,2)
      write(2,'(a,f6.3,"%")') '   Avg Pin Uncertainty = ',avg(2,3)
      endif

!-- print results

      if (isMC1.or.isMC2) then
        write(*,80) '  k-eff Difference = ',nint((keff2-keff1)*10**5), &
                              nint(sqrt(ksigma1**2+ksigma2**2)*10**5) 
      else
        write(*,79) '  k-eff Difference = ',nint((keff2-keff1)*10**5)
      endif
      write(*,81) '    RMS Difference = ',sqrt(sumsq/sumwgt)
      write(*,82) 'Maximum Difference = ',maxabs,' in pin ',ndz(3), &
                       ndz(4),' of level ',ndz(2),' of assembly ',ndz(1)
      write(*,81) 'Average Difference = ',sum/sumwgt

      write(2,*)
      write(2,*) 'Summary of Total Power Distribution Differences'
      write(2,*) '----------------------------------------------------'
      if (isMC1.or.isMC2) then
        write(2,80) '  k-eff Difference = ',nint((keff2-keff1)*10**5), &
                              nint(sqrt(ksigma1**2+ksigma2**2)*10**5)
      else
        write(2,79) '  k-eff Difference = ',nint((keff2-keff1)*10**5) 
                      
      endif
      write(2,81) '    RMS Difference = ',sqrt(sumsq/sumwgt)
      write(2,82) 'Maximum Difference = ',maxabs,' in pin ',ndz(3), &
                       ndz(4),' of level ',ndz(2),' of assembly ',ndz(1)
      write(2,81) 'Average Difference = ',sum/sumwgt
      write(2,*)

      l=ndz(1)
      k=ndz(2)
      i=ndz(3)
      j=ndz(4)

      write(2,*) ' Relative Error for location of Maximum Difference'
      write(2,*) '----------------------------------------------------'
      write(2,91) '--  Reference Pin =',power1(l,k,i,j),sigma1(l,k,i,j)
      write(2,91) '--  Alternate Pin =',power2(l,k,i,j),sigma2(l,k,i,j)
      write(2,92) '-- Relative Error =',(power2(l,k,i,j)-power1(l,k,i,j)) &
             /power1(l,k,i,j)*100, &
            sqrt(absig1(l,k,i,j)**2+absig2(l,k,i,j)**2)/power1(l,k,i,j)*100
 91   format(1x,a,f8.5,' +/- ',f6.3,'%',f8.5)
 92   format(1x,a,f7.3,'% +/- ',f6.3,'%')

      write(2,*) 
      write(2,*) ' Binning of Diffs/Sigmas'
      write(2,*) '----------------------------------------------------'
      bins(:)=0
      total=0
      sigmas=0.0
      max=0.0

      do k=1,nax
        do l=1,nassy
          do j=pylo(l),pyhi(l)
            do i=pxlo(l),pxhi(l)
              if (power1(l,k,i,j)>0.0) then
                total=total+1
                if (sdiff(l,k,i,j)==0.0) then
                  nsigma=0
                else
                  nsigma=abs(pdiff(l,k,i,j))/sdiff(l,k,i,j)
                endif
                sigmas(l,k,i,j)=nsigma
                if (nsigma>max) max=nsigma
                do m=1,10
                  if (m>nsigma) then
                    bins(m)=bins(m)+1
                    exit
                  endif
                enddo
                if (nsigma>10) then
                  bins(11)=bins(11)+1
                endif
              endif
            enddo
          enddo
        enddo
      enddo

      sum=0.0
      do i=1,10
        sum=sum+bins(i)
        write(2,'(3x,i2,3x,i6,2(3x,f5.1,"%"))') i,bins(i),bins(i)/real(total)*100.0,sum/real(total)*100.0
      enddo
      sum=sum+bins(11)
      write(2,'(2x,a3,3x,i6,2(3x,f5.1,"%"))') '>10',bins(11),bins(i)/real(total)*100.0,sum/real(total)*100.0
      write(2,'(1x,a,1x,f6.1)') 'Maximum =',max

! close HDF files

      call h5fclose_f(file_id1, ierror)
      call h5fclose_f(file_id2, ierror)

! write output HDF5 file

      call writehdf(state2)

      close(2)
      close(3)
      write(*,*)           
      write(*,*) 'Done!'

 79   format(1x,a,i6,' pcm')
 80   format(1x,a,i6,' +/- ',i3,' pcm')
 81   format(1x,a,f7.3,'%')
 82   format(1x,a,f7.3,'%',a,'[',i0,',',i0,']',a,i0,a,i0)
      end program

!======================================================================
      subroutine print_keff(nu)
      use global
      implicit none
      integer, intent(in) :: nu

      dk=(keff2-keff1)*10**5
      dksigma=sqrt(ksigma1**2+ksigma2**2)*10**5

      write(nu,*)
      if (isMC1) then
        write(nu,32) '  Reference k-effective = ',keff1,ksigma1
      else
        write(nu,31) '  Reference k-effective = ',keff1
      endif
      if (isMC2) then
        write(nu,32) '  Alternate k-effective = ',keff2,ksigma2
      else
        write(nu,31) '  Alternate k-effective = ',keff2
      endif
      write(2,*)  '----------------------------------------------------'
      if (isMC1 .or. isMC2) then
        write(nu,34) ' k-effective Difference = ',nint(dk),nint(dksigma)
      else
        write(nu,33) ' k-effective Difference = ',nint(dk) 
      endif
 31   format(1x,a,f8.5)
 32   format(1x,a,f8.5,' +/- ',f8.5)
 33   format(1x,a,i8,' pcm')
 34   format(1x,a,i8,' +/- ',i8,' pcm')
      end subroutine

!======================================================================
      subroutine powerstr(power,sigma,mc,string,edittype)
      implicit none
      real*8          , intent(in)  :: power
      real*8          , intent(in)  :: sigma
      logical         , intent(in)  :: mc
      character(len=*), intent(out) :: string
      integer         , intent(in)  :: edittype

      if (mc) then
        if (edittype==0) then   
          write(string,'(f8.5," +/-",f6.3,"%")') power,sigma
        else
          write(string,'(f8.3," +/-",f6.3,"%")') power,sigma
        endif
      else
        if (edittype==0) then   
          write(string,'(5x,f8.5)') power
        else
          write(string,'(5x,f8.3)') power
        endif
      endif
      end subroutine
!======================================================================
      subroutine print_peaks(mx1,mx2,sg1,sg2,ndz1,ndz2)
      use global
      implicit none
      real*8,  intent(in) :: mx1,mx2,sg1,sg2
      integer, intent(in) :: ndz1(4),ndz2(4)
      real*8              :: diff,dsigma

      diff=(mx2-mx1)*100
      if (relative_error) then
        diff=diff/mx1
      endif
      dsigma=sqrt(sg1**2+sg2**2)

      write(2 ,*)
      if (isMC1) then
        write(2 ,36) '  Reference Peak Pin = ',mx1,sg1,'at level',ndz1(2), &
          'in assembly',ndz1(1),'in pin',ndz1(3),ndz1(4)
      else
        write(2 ,35) '  Reference Peak Pin = ',mx1,'at level',ndz1(2), &
          'in assembly',ndz1(1),'in pin',ndz1(3),ndz1(4)
      endif
      if (isMC2) then
        write(2 ,36) '  Alternate Peak Pin = ',mx2,sg2,'at level',ndz2(2), &
          'in assembly',ndz2(1),'in pin',ndz2(3),ndz2(4)
      else
        write(2 ,35) '  Alternate Peak Pin = ',mx2,'at level',ndz2(2), &    
          'in assembly',ndz2(1),'in pin',ndz2(3),ndz2(4)
      endif
      write(2,*)  '----------------------------------------------------'
      if (isMC1 .or. isMC2) then
        write(2 ,38) ' Peak Pin Difference = ',diff,dsigma
      else
        write(2 ,37) ' Peak Pin Difference = ',diff     
      endif
 35   format(1x,a,f9.5,1x,a,1x,i0,1x,a,1x,i0,1x,a,' [',i0,',',i0,']')
 36   format(1x,a,f9.5,' +/- ',f6.3,'%',1x,a,1x,i0,1x,a,1x,i0,1x,a,' [',i0,',',i0,']')
 37   format(1x,a,f8.4,'%')
 38   format(1x,a,f8.4,'% +/- ',f6.3,'%')
      end subroutine
!======================================================================
