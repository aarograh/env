      subroutine radial(fid,power,sigma,ismc,radpow,radsig,radpsg,version,dataset)
      use global
      use hdf5
      implicit none
      
      integer(hid_t)       :: fid
      integer(hsize_t)     :: idims(10)
      real*8 , intent(in)  :: power(nassy,nax,npin,npin)
      real*8 , intent(in)  :: sigma(nassy,nax,npin,npin)
      logical, intent(in)  :: ismc
      real*8 , intent(out) :: radpow(nassy,npin,npin)
      real*8 , intent(out) :: radsig(nassy,npin,npin)
      real*8 , intent(out) :: radpsg(nassy,npin,npin)
      integer, intent(in)  :: version
      character(len=*),intent(in) :: dataset
      
      integer              :: i,j,k,l
      real*8               :: sumwgt
      real*8               :: avg,sig1,sig2
      logical              :: exists,haspsg

      real*8, allocatable  :: tempp(:,:,:)
      character(len=20) dname

      radpow(:,:,:)=0.0
      radsig(:,:,:)=0.0
      radpsg(:,:,:)=0.0
      haspsg=.false.

!-- check of axial powers exist on the file

      dname='radial_'//trim(dataset)
      call h_exists(fid, dname, exists)
      if (exists) then
        if (version==2) then
          call h_read(fid, dname,idims,radpow)
        else
          allocate(tempp(npin,npin,nassy))
          call h_read(fid, dname,idims,tempp )
          do j=1,npin
            do i=1,npin
              do l=1,nassy
                radpow(l,i,j)=tempp(j,i,l)
              enddo
            enddo
          enddo
          deallocate(tempp)
        endif
          
        if (ismc) then
          dname='radial_'//trim(dataset)//'_sigma'
          if (version==2) then
            call h_read(fid, dname,idims,radsig)
          else
            allocate(tempp(npin,npin,nassy))
            call h_read(fid, dname,idims,tempp )
            do j=1,npin
              do i=1,npin
                do l=1,nassy
                  radsig(l,i,j)=tempp(j,i,l)
                enddo
              enddo
            enddo
            deallocate(tempp)
          endif
        endif

        if (dataset=='fueltemps') then
          radpow = radpow*1.8+32
          radpow = radpow*1.8+32
        endif
!-- otherwise calculate from pin powers

      else
        do l=1,nassy
          do i=1,npin
            do j=1,npin
              sumwgt=0.0
              do k=1,nax
                radpow(l,i,j)=radpow(l,i,j)+power(l,k,i,j)*wgt(l,k,i,j)
                if (ismc) then
                  radsig(l,i,j)=radsig(l,i,j)+sigma(l,k,i,j)**2*wgt(l,k,i,j)**2
                  radpsg(l,i,j)=radpsg(l,i,j)+sigma(l,k,i,j)**2*wgt(l,k,i,j)
                endif
                sumwgt=sumwgt+wgt(l,k,i,j)
              enddo 
              if (sumwgt==0.0) cycle
              radpow(l,i,j)=radpow(l,i,j)/sumwgt
              if (ismc) then
                radsig(l,i,j)=sqrt(radsig(l,i,j)/sumwgt)/sqrt(sumwgt)
                radpsg(l,i,j)=sqrt(radpsg(l,i,j)/sumwgt)
                radsig(l,i,j)=radsig(l,i,j)/radpow(l,i,j)*100.0
                radpsg(l,i,j)=radpsg(l,i,j)/radpow(l,i,j)*100.0
              endif
            enddo
          enddo
        enddo
        haspsg=.true.
      endif

!--- print radial powers to output
      
      do l=1,nassy
        write(2,*)
        write(2,'(1x,a,i0)') 'Assembly = ',l
        write(2,*) '<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
        write(2,*) ' Radial Powers'
        write(2,*) ' --------------------------------------------------'
        do j=pylo(l),pyhi(l)
          write(2,'(2x,17(f8.5))') (radpow(l,i,j),i=pxlo(l),pxhi(l))
        enddo
        if (ismc) then
        write(2,*) ' --------------------------------------------------'
        write(2,*) ' Radial Power Estimated Uncertainty'
        write(2,*) ' --------------------------------------------------'
        do j=pylo(l),pyhi(l)
          write(2,'(2x,17(f7.3,"%"))') (radsig(l,i,j),i=pxlo(l),pxhi(l))
        enddo
        if (haspsg) then
        write(2,*) ' --------------------------------------------------'
        write(2,*) ' Radial Average Pin Uncertainty'
        write(2,*) ' --------------------------------------------------'
        do j=pylo(l),pyhi(l)
          write(2,'(2x,17(f7.3,"%"))') (radpsg(l,i,j),i=pxlo(l),pxhi(l))
        enddo
        endif
        endif
       !write(2,*) ' --------------------------------------------------'
       !write(2,*) ' Normalized Radial Weighting Factors'
       !write(2,*) ' --------------------------------------------------'
       !do j=pylo(l),pyhi(l)
       !  write(2,'(2x,17(f8.3))') (radwgt(j,i,l)/axmesh(nax+1),i=pxlo(l),pxhi(l))
       !enddo
      enddo
      write(2,*) ' --------------------------------------------------'
       
      avg=0.0
      sig1=0.0
      sig2=0.0
      sumwgt=0.0
      do i=1,npin
        do j=1,npin
          do l=1,nassy
            avg=avg+radpow(l,i,j)*radwgt(l,i,j)
            sumwgt=sumwgt+radwgt(l,i,j)
            if (ismc) then
              sig1=sig1+radsig(l,i,j)**2*radwgt(l,i,j)
              sig2=sig2+radpsg(l,i,j)**2*radwgt(l,i,j) 
            endif
          enddo
        enddo
      enddo
      write(2,92) '             Average Power =',avg/sumwgt
      if (ismc) then
      write(2,94) 'Average Radial Uncertainty =',sqrt(sig1/sumwgt)
      if (haspsg) then
      write(2,94) 'Average    Pin Uncertainty =',sqrt(sig2/sumwgt)
      endif
      endif
 92   format(1x,a,1x,f8.5)
 93   format(1x,a,1x,f7.3,'%')
 94   format(1x,a,1x,f6.3,'%')
      end subroutine
