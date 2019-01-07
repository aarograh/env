      program kenopow
      use global
      implicit none
      character(len=80)  :: inputfile
      character(len=80)  :: fuelunitsfile
      character(len=132) :: line
      character(len=80)  :: tempstr
      integer            :: iargs
      logical            :: exists
      integer            :: i,k,m,num
      
      keff=0.0
      ksigma=0.0
      fuelunitsfile='fuelunits'
!--------------------------------------------------------------------------------
      iargs = command_argument_count()
      if (iargs==0) then
        write(*,*) 'usage:  kenopow.exe keno_output [fuelunits] '// &
                            '[octant_collapse] [max_units]'
        stop
      endif
      call get_command_argument(1,inputfile)
      inquire(file=inputfile, exist=exists)
      if (.not.exists) then
       write(*,*) 'error: input file ',trim(inputfile),' does not exist'
        stop
      endif

      if (iargs>1) then
        call get_command_argument(2,fuelunitsfile)
      endif
      inquire(file=fuelunitsfile, exist=exists)
      if (.not.exists) then
        write(*,*) 'error: units file ',trim(fuelunitsfile), &
                                                   ' does not exist'
        stop
      endif

      if (iargs>2) then
        call get_command_argument(3,tempstr)
        read(tempstr,*) octant_symmetry
        if (octant_symmetry) then
          write(*,*) 'Data collapse using octant symmetry engaged'
        else
          write(*,*) 'Data collapse using octant symmetry disabled'
        endif
      endif

      if (iargs>3) then
        call get_command_argument(4,tempstr)
        read(tempstr,*) maxunits
        write(*,*) 'Maximum number of KENO units allocated as ',maxunits
      endif

! open output file
      open(unit=2,file='kenopow.out',status='replace')

!--------------------------------------------------------------------------------
      allocate(fu(maxunits,5))
      open(unit=9,file=fuelunitsfile,status='old')
      call fuelunits()
      close(9)

      call getcwd(line)

      write(2,*) '=============================================='
      write(2,*) '  KENOPOW - Pin Powers from KENO-VI output'
      write(2,*) 
      write(2,*) '    Version 1.5 - 8/24/2013'
      write(2,*) '=============================================='
      write(2,*) 'keno output: ',trim(inputfile)
      write(2,*) ' fuel units: ',trim(fuelunitsfile)
      write(2,*) 'working dir: ',trim(line)
      write(2,*) ' octant sym: ',octant_symmetry
      write(2,*)
      write(2,*)           'problem dimensions:'
      write(2,'(1x,a,i0)') ' number of assemblies = ',nasst
      write(2,'(1x,a,i0)') ' number of assemblies across = ',nass
      write(2,'(1x,a,i0)') ' number of pins across = ',npin
      write(2,'(1x,a,i0)') ' number of axial levels = ',nax 

      allocate(  fissn(nasst,nax,npin,npin))
      allocate(  power(nasst,nax,npin,npin))
      allocate(  sigma(nasst,nax,npin,npin))
      allocate( celldz(nasst,nax,npin,npin))
      allocate(  names(nasst,nax,npin,npin))
      allocate(     dz(nax))

      open(unit=7,file=inputfile,status='old')
!---------------------------------------------------------------------------------
      call fillunits()
      call calcgeo()
      call getfissions()
      if (octant_symmetry) then
        call collapsefissions()
      endif
      call normalize()
      
      line=''
      do
        read(7,'(a)',end=11) line
        call trygetk(line)                    ! read the calculated eigenvalue results
      enddo
 11   close(7)

!--- fill axial boundaries
      allocate(axmids(nax))
      allocate(axmesh(nax+1))
      axmids(:)=0.0
      axmids(1)=dz(1)/2.0
      axmesh(1)=0.0
      axmesh(2)=dz(1)
      do k=2,nax 
        axmesh(k+1)=axmesh(k)+dz(k)
        axmids(k)=(axmesh(k+1)+axmesh(k))/2.0
      enddo

!--- start printing results

      write(*,*)
      write(2,*)
      write(2,*) ' KENO-VI RESULTS'
      write(2,*) '================='
      write(2,*)
      write(*,'(1x,a,f9.6," +/- ",f9.6)') '  k-effective = ',keff,ksigma
      write(2,'(1x,a,f9.6," +/- ",f9.6)') '  k-effective = ',keff,ksigma
      call stats()
!---------------------------------------------------------------------------------
      call writehdf()
      close(2)
      write(*,*) 'Done!'
      end program
