      subroutine axial(fid,power,sigma,ismc,axpow,axsig,axpsg,ao,dataset)
      use global
      use hdf5
      implicit none
      
      integer(hid_t)       :: fid
      integer(hsize_t)     :: idims(10)
      real*8 , intent(in)  :: power(nassy,nax,npin,npin)
      real*8 , intent(in)  :: sigma(nassy,nax,npin,npin)
      logical, intent(in)  :: ismc
      real*8 , intent(out) :: axpow(nax)
      real*8 , intent(out) :: axsig(nax)
      real*8 , intent(out) :: axpsg(nax)
      real*8 , intent(out) :: ao            
      character(len=*),intent(in) :: dataset
      
      integer i,j,k,l
      real*8  sumwgt,elev
      real*8  hmid,ptop,pbot
      real*8  avg,sig1,sig2,dz,tdz
      logical exists,haspsg
      character(len=20) dname

      axpow(:)=0.0
      axsig(:)=0.0
      axpsg(:)=0.0
      haspsg=.false.

!-- check of axial powers exist on the file

      dname='axial_'//trim(dataset)
      call h_exists(fid, dname, exists)
      if (exists) then
        call h_read(fid, dname,idims,axpow)
        if (ismc) then
          call h_read(fid,trim(dname)//'_sigma',idims,axsig)
        endif

         if (dataset=='fueltemps') then
           axpow = axpow*1.8+32
           axpow = axpow*1.8+32
         endif

!-- otherwise calculate from pin powers

      else 
        do k=1,nax
          sumwgt=0.0
          do l=1,nassy
            do j=1,npin
              do i=1,npin
                axpow(k)=axpow(k)+power(l,k,i,j)*wgt(l,k,i,j)
                if (ismc) then
                  axsig(k)=axsig(k)+sigma(l,k,i,j)**2*wgt(l,k,i,j)**2
                  axpsg(k)=axpsg(k)+sigma(l,k,i,j)**2*wgt(l,k,i,j)
                endif
                sumwgt=sumwgt+wgt(l,k,i,j)
              enddo 
            enddo
          enddo
          axpow(k)=axpow(k)/sumwgt
          if (ismc) then
            axsig(k)=sqrt(axsig(k)/sumwgt)/sqrt(sumwgt)
            axpsg(k)=sqrt(axpsg(k)/sumwgt)
            axsig(k)=axsig(k)/axpow(k)*100.0
            axpsg(k)=axpsg(k)/axpow(k)*100.0
          endif
        enddo
        haspsg=.true.
      endif
     
!--- calculate AO
        
      hmid=(axmesh(nax+1)+axmesh(1))/2.0   ! midpoint of the fuel
      pbot=0.0
      ptop=0.0
      do k=1,nax
        if (axmesh(k+1)<=hmid) then
          pbot=pbot+axpow(k)*(axmesh(k+1)-axmesh(k))
        elseif (axmesh(k)<hmid) then
          pbot=pbot+axpow(k)*(hmid-axmesh(k))
          ptop=ptop+axpow(k)*(axmesh(k+1)-hmid)
        else
          ptop=ptop+axpow(k)*(axmesh(k+1)-axmesh(k)) 
        endif
      enddo
      ao=(ptop-pbot)/(ptop+pbot)*100.0

!--- print tabke to output
      
      if (ismc) then

        write(2,*)
        write(2,*) ' Level   Height        Axial Power    Avg Pin Unc'
       write(2,*) '---------------------------------------------------'
        do k=nax,1,-1
          elev=(axmesh(k+1)+axmesh(k))/2.0
          write(2,90), k,elev,axpow(k),axsig(k),axpsg(k)
        enddo
 90     format(3x,i3,2x,f9.4,2x,f8.5,' +/-',f6.3,'%',2x,f6.3,'%')
       write(2,*) '---------------------------------------------------'
       
      else

        write(2,*)
        write(2,*) ' Level   Height   Axial Power   '
        write(2,*) '--------------------------------'
        do k=nax,1,-1
          elev=(axmesh(k+1)+axmesh(k))/2.0
          write(2,91), k,elev,axpow(k)
        enddo
 91     format(3x,i3,2x,f9.4,2x,f8.5)
        write(2,*) '--------------------------------'
      endif

      avg=0.0
      sig1=0.0
      sig2=0.0
      tdz=0.0
      do k=1,nax
        dz=axmesh(k+1)-axmesh(k)
        avg=avg+axpow(k)*dz
        tdz=tdz+dz
        if (ismc) then
          sig1=sig1+axsig(k)**2*dz
          sig2=sig2+axpsg(k)**2*dz
        endif
      enddo
      if (ismc) then
        write(2,92) '            Average Power =',avg/tdz
        write(2,93) '             Axial Offset =',ao
        write(2,94) 'Average Axial Uncertainty =',sqrt(sig1/tdz)
        if (haspsg) then
          write(2,94) 'Average   Pin Uncertainty =',sqrt(sig2/tdz)
        endif
      else
        write(2,92) '   Average Power =',avg/tdz
        write(2,93) '    Axial Offset =',ao
      endif

 92   format(a,1x,f8.5)
 93   format(a,1x,f7.3,'%')
 94   format(a,1x,f6.3,'%')
      end subroutine
