      subroutine assembly(fid,power,sigma,ismc,asspow,asssig,asspsg,nn,version,dataset)
      use global
      use hdf5
      implicit none
      
      integer(hid_t)       :: fid
      integer(hsize_t)     :: idims(10)
      real*8 , intent(in)  :: power(nassy,nax,npin,npin)
      real*8 , intent(in)  :: sigma(nassy,nax,npin,npin)
      logical, intent(in)  :: ismc
      real*8 , intent(out) :: asspow(nassy,nax)
      real*8 , intent(out) :: asssig(nassy,nax)
      real*8 , intent(out) :: asspsg(nassy,nax)
      real*8 , allocatable :: tempp(:,:)
      integer, intent(in)  :: nn
      integer, intent(in)  :: version
      character(len=*),intent(in) :: dataset
      
      integer i,j,k,l,aj,ai,m
      real*8  avg,sig1,sig2,sumwgt
      logical exists,haspsg
      character(len=150) :: lout
      character(len=20) dname

      asspow(:,:)=0.0
      asssig(:,:)=0.0
      asspsg(:,:)=0.0
      haspsg=.false.

!-- check of assembly powers exist on the file

      dname='assembly_'//trim(dataset)
      call h_exists(fid, dname, exists)
      if (exists) then
        if (nassy==nassy2.or.nn==1) then
          
          if (version==2) then
            call h_read(fid, dname,idims,asspow)
          else
            allocate(tempp(nax,nassy))
            call h_read(fid, dname,idims,tempp )
            do k=1,nax
              do l=1,nassy
                asspow(l,k)=tempp(k,l)
              enddo
            enddo
            deallocate(tempp)
          endif

          if (ismc) then
            dname='assembly_'//trim(dataset)//'_sigma'
            if (version==2) then
              call h_read(fid, dname,idims,asssig)
            else
              allocate(tempp(nax,nassy))
              call h_read(fid, dname,idims,tempp )
              do k=1,nax
                do l=1,nassy
                  asssig(l,k)=tempp(k,l)
                enddo
              enddo
              deallocate(tempp)
            endif
          endif

        else
          allocate(tempp(nassy2,nax))
          call h_read(fid, dname,idims,tempp)

! convert second geometry to first
! assume odd number of assemblies

          if (isym==4) then
            asspow=0.0
            m=int(nsize/2)
            do aj=m,nsize
              do ai=m,nsize
                if (coremap2(ai,aj)/=0) then
                  do k=1,nax
                    asspow(coremap(ai,aj),k)=tempp(coremap2(ai,aj),k)
                  enddo
                endif
              enddo
            enddo
          endif
          deallocate(tempp)
        endif

        if (dataset=='fueltemps') then
          asspow = asspow*1.8+32
          asspow = asspow*1.8+32
        endif
!-- otherwise calculate from pin powers

      else 
        do l=1,nassy
          do k=1,nax
            sumwgt=0.0
            do j=1,npin
              do i=1,npin
                asspow(l,k)=asspow(l,k)+power(l,k,i,j)*wgt(l,k,i,j)
                if (ismc) then
                  asssig(l,k)=asssig(l,k)+sigma(l,k,i,j)**2*wgt(l,k,i,j)**2
                  asspsg(l,k)=asspsg(l,k)+sigma(l,k,i,j)**2*wgt(l,k,i,j)
                endif
                sumwgt=sumwgt+wgt(l,k,i,j)
              enddo 
            enddo
            asspow(l,k)=asspow(l,k)/sumwgt
            if (ismc) then
              asssig(l,k)=sqrt(asssig(l,k)/sumwgt)/sqrt(sumwgt)
              asspsg(l,k)=sqrt(asspsg(l,k)/sumwgt)
              asssig(l,k)=asssig(l,k)/asspow(l,k)*100.0
              asspsg(l,k)=asspsg(l,k)/asspow(l,k)*100.0
            endif
          enddo
        enddo
        haspsg=.true.
      endif
     
!--- print assembly map output
      
      if (nassy==1) return

      do k=nax,1,-1
        write(2,*)
        write(2,'(2x,a,i0)') ' Axial Level = ',k
        write(2,*) ' ================================================'
        if (nn==1) then
          write(2,*) '  Reference Assembly Powers'
        else
          write(2,*) '  Alternate Assembly Powers'
        endif
        write(2,*) '  -----------------------------------------------'
        do aj=aylo,ayhi  
          write(2,'("  ")',advance='no')
          do ai=axlo,axhi 
            l=coremap(ai,aj)
            if (l>0) then
              write(2,'(f8.5)',advance='no') asspow(l,k)
            else
              write(2,'(8(" "))',advance='no') 
            endif
          enddo
          write(2,*)
        enddo
        if (ismc) then
        write(2,*) '  -----------------------------------------------'
        if (nn==1) then
          write(2,*) '  Reference Assembly Power Uncertainty (%)'
        else
          write(2,*) '  Alternate Assembly Power Uncertainty (%)'
        endif
        write(2,*) '  -----------------------------------------------'
        do aj=aylo,ayhi  
          write(2,'("  ")',advance='no')
          do ai=axlo,axhi 
            l=coremap(ai,aj)
            if (l>0) then
              write(2,'(f7.3,"%")',advance='no') asssig(l,k)
            else
              write(2,'(8(" "))',advance='no') 
            endif
          enddo
          write(2,*)
        enddo
        endif
        write(2,*) '  -----------------------------------------------'
      enddo

!--- print summary statistics

      avg=0.0
      sig1=0.0
      sig2=0.0
      sumwgt=0.0
      do k=1,nax
        do l=1,nassy
          avg=avg+asspow(l,k)*asswgt(l,k)
          sumwgt=sumwgt+asswgt(l,k)
          if (ismc) then
            sig1=sig1+asssig(l,k)**2*asswgt(l,k)
            sig2=sig2+asspsg(l,k)**2*asswgt(l,k)
          endif
        enddo
      enddo
      if (ismc) then
        write(2,92) '      Average Assembly Power =',avg/sumwgt
        write(2,94) 'Average Assembly Uncertainty =',sqrt(sig1/sumwgt)
        !if (haspsg) then
        !  write(2,94) 'Average   Pin Uncertainty =',sqrt(sig2/wgt)
        ! endif
      else
        write(2,92) ' Average Assembly Power =',avg/sumwgt
      endif

 92   format(a,1x,f8.5)
 93   format(a,1x,f7.3,'%')
 94   format(a,1x,f6.3,'%')
      end subroutine
