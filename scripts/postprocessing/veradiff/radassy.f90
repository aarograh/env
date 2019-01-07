      subroutine radassy(fid,power,sigma,ismc,ardpow,ardsig,ardpsg,nn,version,dataset)
      use global
      use hdf5
      implicit none
      
      integer(hid_t)       :: fid
      integer(hsize_t)     :: idims(10)
      real*8 , intent(in)  :: power(nassy,nax,npin,npin)
      real*8 , intent(in)  :: sigma(nassy,nax,npin,npin)
      logical, intent(in)  :: ismc
      real*8 , intent(out) :: ardpow(nassy)
      real*8 , intent(out) :: ardsig(nassy)
      real*8 , intent(out) :: ardpsg(nassy)
      real*8 , allocatable :: tempp(:)
      integer, intent(in)  :: nn
      integer, intent(in)  :: version
      character(len=*),intent(in) :: dataset
      
      integer i,j,k,l,aj,ai,m
      real*8  avg,sig1,sig2,sumwgt
      logical exists,haspsg
      character(len=150) :: lout
      character(len=20) dname

      ardpow(:)=0.0
      ardsig(:)=0.0
      ardpsg(:)=0.0
      haspsg=.false.

!-- check of radial assembly powers exist on the file

      dname='radial_assembly_'//trim(dataset)
      call h_exists(fid, dname, exists)
      if (exists) then
        if (nassy==nassy2.or.nn==1) then
          call h_read(fid, dname,idims,ardpow)
          if (ismc) then
            call h_read(fid, trim(dname)//'_sigma',idims,ardsig)
          endif
        else
          allocate(tempp(nassy2))
          call h_read(fid, dname,idims,tempp)

! convert second geometry to first
! assume odd number of assemblies

          if (isym==4) then
            ardpow=0.0
            m=int(nsize/2)
            do aj=m,nsize
              do ai=m,nsize
                if (coremap2(ai,aj)/=0) then
                  ardpow(coremap(ai,aj))=tempp(coremap2(ai,aj))
                endif
              enddo
            enddo
          endif
          deallocate(tempp)
        endif

        if (dataset=='fueltemps') then
          ardpow = ardpow*1.8+32
          ardpow = ardpow*1.8+32
        endif

!-- otherwise calculate from pin powers

      else 
        do l=1,nassy
          sumwgt=0.0
          do k=1,nax
            do j=1,npin
              do i=1,npin
                ardpow(l)=ardpow(l)+power(l,k,i,j)*wgt(l,k,i,j)
                if (ismc) then
                  ardsig(l)=ardsig(l)+sigma(l,k,i,j)**2*wgt(l,k,i,j)**2
                  ardpsg(l)=ardpsg(l)+sigma(l,k,i,j)**2*wgt(l,k,i,j)
                endif
                sumwgt=sumwgt+wgt(l,k,i,j)
              enddo 
            enddo
          enddo
          ardpow(l)=ardpow(l)/sumwgt
          if (ismc) then
            ardsig(l)=sqrt(ardsig(l)/sumwgt)/sqrt(sumwgt)
            ardpsg(l)=sqrt(ardpsg(l)/sumwgt)
            ardsig(l)=ardsig(l)/ardpow(l)*100.0
            ardpsg(l)=ardpsg(l)/ardpow(l)*100.0
          endif
        enddo
        haspsg=.true.
      endif
     
!--- print assembly map output
      
      if (nassy==1) return

      write(2,*)
      write(2,*) ' ================================================'
      if (nn==1) then
        write(2,*) '  Reference Radial Assembly Powers'
      else
        write(2,*) '  Alternate Radial Assembly Powers'
      endif
      write(2,*) '  -----------------------------------------------'
      do aj=aylo,ayhi  
        write(2,'("  ")',advance='no')
        do ai=axlo,axhi 
          l=coremap(ai,aj)
          if (l>0) then
            write(2,'(f8.5)',advance='no') ardpow(l)
          else
            write(2,'(8(" "))',advance='no') 
          endif
        enddo
        write(2,*)
      enddo
      if (ismc) then
      write(2,*) '  -----------------------------------------------'
      if (nn==1) then
        write(2,*) '  Reference Radial Assembly Power Uncertainty (%)'
      else
        write(2,*) '  Alternate Radial Assembly Power Uncertainty (%)'
      endif
      write(2,*) '  -----------------------------------------------'
      do aj=aylo,ayhi  
        write(2,'("  ")',advance='no')
        do ai=axlo,axhi 
          l=coremap(ai,aj)
          if (l>0) then
            write(2,'(f7.3,"%")',advance='no') ardsig(l)
          else
            write(2,'(8(" "))',advance='no') 
          endif
        enddo
        write(2,*)
      enddo
      endif
      write(2,*) '  -----------------------------------------------'

!--- print summary statistics

      avg=0.0
      sig1=0.0
      sig2=0.0
      sumwgt=0.0
      do l=1,nassy
        avg=avg+ardpow(l)*ardwgt(l)
        sumwgt=sumwgt+ardwgt(l)
        if (ismc) then
          sig1=sig1+ardsig(l)**2*ardwgt(l)
          sig2=sig2+ardpsg(l)**2*ardwgt(l)
        endif
      enddo
      write(2,92) '      Average Assembly Power =',avg/sumwgt
      if (ismc) then
        write(2,94) 'Average Assembly Uncertainty =',sqrt(sig1/sumwgt)
        !if (haspsg) then
        !  write(2,94) 'Average   Pin Uncertainty =',sqrt(sig2/wgt)
        ! endif
      endif

 92   format(a,1x,f8.5)
 93   format(a,1x,f7.3,'%')
 94   format(a,1x,f6.3,'%')
      end subroutine
