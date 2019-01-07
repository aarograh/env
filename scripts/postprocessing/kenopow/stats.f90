      subroutine stats
      use global
      use constants
      implicit none
      integer      :: a,ai,aj,pi,pj,k,n,ni,nj,tmpint
      integer      :: cnt,i,nassx,npinx,sym
      real*8       :: vol,avg,sum,vtmp
      real*8       :: hmid,ptop,pbot
      real*8       :: maxpow(2),minpow(2),maxsig(2),minsig(2),maxsigp(3)
      integer      :: ax(4),zx(4),ay(4),zy(4)
      logical      :: iseven,lasta

      real*8           ,allocatable :: absig(:,:,:,:)
      character(len=20),allocatable :: temp(:)
      integer      :: nodef,getsym
!--- allocate and initialize

      allocate(  axials(nax))
      allocate(  axsigs(nax))
      allocate( axsigs2(nax))
      allocate(  asspow(nasst,nax))
      allocate(  asssig(nasst,nax))
      allocate( asssig2(nasst,nax))
      allocate( radials(nasst,npin,npin))
      allocate( radsigs(nasst,npin,npin))
      allocate(radsigs2(nasst,npin,npin))
      allocate(  assrad(nasst))
      allocate(  assrsg(nasst))
      allocate( assrsg2(nasst))
      allocate(   absig(nasst,nax,npin,npin))
      allocate(  nodpow(nasst,nax,4))
      allocate(  nodsig(nasst,nax,4))

      axials(:)=0.0
      axsigs(:)=0.0
      axsigs2(:)=0.0
      asspow(:,:)=0.0
      asssig(:,:)=0.0
      asssig2(:,:)=0.0
      radials(:,:,:)=0.0  
      radsigs(:,:,:)=0.0
      radsigs2(:,:,:)=0.0
      assrad(:)=0.0
      assrsg(:)=0.0
      assrsg2(:)=0.0
      absig(:,:,:,:)=0.0
      nodpow(:,:,:)=0.0
      nodsig(:,:,:)=0.0

!--- calculate maximum and minimum powers and sigmas

      maxpow(:)=0.
      minpow(:)=100.
      maxsig(:)=0.
      minsig(:)=100.
      maxsigp(:)=0.0
      
      do pj=1,npin 
        do pi=1,npin 
          do a=1,nasst
            if (types(a,pi,pj)==1) then
              do k=1,nax
                if (power(a,k,pi,pj)>maxpow(1)) then
                  maxpow(1)=power(a,k,pi,pj)
                  maxpow(2)=sigma(a,k,pi,pj)
                endif
                if (power(a,k,pi,pj)<minpow(1)) then
                  minpow(1)=power(a,k,pi,pj)
                  minpow(2)=sigma(a,k,pi,pj)
                endif
                if (sigma(a,k,pi,pj)>maxsig(2)) then
                  maxsig(2)=sigma(a,k,pi,pj)
                  maxsig(1)=power(a,k,pi,pj)
                endif
                if (sigma(a,k,pi,pj)<minsig(2)) then 
                  minsig(2)=sigma(a,k,pi,pj)
                  minsig(1)=power(a,k,pi,pj)
                endif
                if (power(a,k,pi,pj)>1.0) then
                  if (sigma(a,k,pi,pj)>maxsigp(3)) then
                    maxsigp(3)=sigma(a,k,pi,pj)
                  endif
                elseif (power(a,k,pi,pj)>0.5) then
                  if (sigma(a,k,pi,pj)>maxsigp(2)) then
                    maxsigp(2)=sigma(a,k,pi,pj)
                  endif
                else
                  if (sigma(a,k,pi,pj)>maxsigp(1)) then
                    maxsigp(1)=sigma(a,k,pi,pj)
                  endif
                endif
              enddo
            endif
          enddo
        enddo
      enddo

! calculate actual uncertainties from percent uncertainties 
! for statistics calculations

      do pj=1,npin
        do pi=1,npin
          do k=1,nax
             do a=1,nasst
              absig(a,k,pi,pj)=sigma(a,k,pi,pj)*power(a,k,pi,pj)/100.0
            enddo
          enddo
        enddo
      enddo

! calculate averages
! average pin power and average pin uncertainty

      avg=0.
      avgsig=0.
      vol=0.
      do pj=1,npin
        do pi=1,npin
          do a=1,nasst
            if (types(a,pi,pj)==1) then
              do k=1,nax
                avg=avg+power(a,k,pi,pj)*vols(a,k,pi,pj)
                avgsig=avgsig+absig(a,k,pi,pj)**2*vols(a,k,pi,pj)
                vol=vol+vols(a,k,pi,pj)
              enddo
            endif
          enddo
        enddo
      enddo
      avgpow=avg/vol
      avgsig=sqrt(avgsig/vol)/avgpow*100.0
      totalvol=vol
      
      if (totalvol==0) then
        write(*,*) 'error:  Total volume is zero'
        stop
      endif

! calculate 1d axial powers
      
      do k=1,nax 
        vol=0.
        do pj=1,npin
          do pi=1,npin
            do a=1,nasst
              if (types(a,pi,pj)==1) then
                axials(k)= axials(k) +power(a,k,pi,pj)* &
                                       vols(a,k,pi,pj)
                axsigs(k)= axsigs(k) +absig(a,k,pi,pj)**2 * &
                                       vols(a,k,pi,pj)**2
                axsigs2(k)=axsigs2(k)+absig(a,k,pi,pj)**2 * &
                                       vols(a,k,pi,pj)
                vol=vol+vols(a,k,pi,pj)
              endif
            enddo
          enddo
        enddo
        if (vol>0.0) then
          axials(k) =axials(k)/vol
          axsigs(k) =sqrt( axsigs(k)/vol)/sqrt(vol)
          axsigs2(k)=sqrt(axsigs2(k)/vol) 

          axsigs(k) = axsigs(k)/axials(k)*100.0
          axsigs2(k)=axsigs2(k)/axials(k)*100.0 
        endif
      enddo

! calculate 2d radial powers
         
      do pj=1,npin
        do pi=1,npin
          do a=1,nasst
            if (types(a,pi,pj)==1) then
              vol=0.
              do k=1,nax
                radials(a,pi,pj)= radials(a,pi,pj) +power(a,k,pi,pj)* &
                                                     vols(a,k,pi,pj)
                radsigs(a,pi,pj)= radsigs(a,pi,pj) +absig(a,k,pi,pj)**2* &
                                                     vols(a,k,pi,pj)**2
                radsigs2(a,pi,pj)=radsigs2(a,pi,pj)+absig(a,k,pi,pj)**2* &
                                                     vols(a,k,pi,pj)
                vol=vol+vols(a,k,pi,pj)
              enddo
              radials(a,pi,pj) =radials(a,pi,pj)/vol
              radsigs(a,pi,pj) =sqrt( radsigs(a,pi,pj)/vol)/sqrt(vol)
              radsigs2(a,pi,pj)=sqrt(radsigs2(a,pi,pj)/vol)

              radsigs(a,pi,pj) = radsigs(a,pi,pj)/radials(a,pi,pj)*100.0
              radsigs2(a,pi,pj)=radsigs2(a,pi,pj)/radials(a,pi,pj)*100.0
            endif
          enddo
        enddo
      enddo
             
! calculate assembly powers
      
      do k=1,nax
        do a=1,nasst
          vol=0.
          do pj=1,npin
            do pi=1,npin
              if (types(a,pi,pj)==1) then
                asspow(a,k)= asspow(a,k) +power(a,k,pi,pj)* &
                                           vols(a,k,pi,pj)
                asssig(a,k)= asssig(a,k) +absig(a,k,pi,pj)**2 * &
                                           vols(a,k,pi,pj)**2
                asssig2(a,k)=asssig2(a,k)+absig(a,k,pi,pj)**2 * &
                                           vols(a,k,pi,pj)
                vol=vol+vols(a,k,pi,pj)
              endif
            enddo
          enddo
          asspow(a,k) =asspow(a,k)/vol
          asssig(a,k) =sqrt( asssig(a,k)/vol)/sqrt(vol) 
          asssig2(a,k)=sqrt(asssig2(a,k)/vol) 

           asssig(a,k)= asssig(a,k)/asspow(a,k)*100.0
          asssig2(a,k)=asssig2(a,k)/asspow(a,k)*100.0  
        enddo
      enddo

! calculate 2d assembly powers
         
      do a=1,nasst
        vol=0.
        do pj=1,npin
          do pi=1,npin
            if (types(a,pi,pj)==1) then
              do k=1,nax
                assrad(a)= assrad(a) +power(a,k,pi,pj)* &
                                       vols(a,k,pi,pj) 
                assrsg(a)= assrsg(a) +absig(a,k,pi,pj)**2 * &
                                       vols(a,k,pi,pj)**2 
                assrsg2(a)=assrsg2(a)+absig(a,k,pi,pj)**2 * &
                                       vols(a,k,pi,pj)
                vol=vol+vols(a,k,pi,pj)
              enddo
            endif
          enddo
        enddo
         assrad(a)=assrad(a)/vol
         assrsg(a)=sqrt( assrsg(a)/vol)/sqrt(vol)
        assrsg2(a)=sqrt(assrsg2(a)/vol)

         assrsg(a)= assrsg(a)/assrad(a)*100.0 
        assrsg2(a)=assrsg2(a)/assrad(a)*100.0 
      enddo
             
! calculate nodal powers and uncertainties

      iseven = (mod(npin,2)==0)

      if (iseven) then

        ax(1)=1 
        ay(1)=1 
        zx(1)=nint(npin/2.0) 
        zy(1)=nint(npin/2.0)

        ax(2)=zx(1)+1
        ay(2)=1    
        zx(2)=npin
        zy(2)=zy(1) 

        ax(3)=1     
        ay(3)=zy(1)+1
        zx(3)=zx(1)           
        zy(3)=npin

        ax(4)=ax(2)
        ay(4)=ay(3) 
        zx(4)=npin 
        zy(4)=npin 
      
      else

        ax(1)=1 
        ay(1)=1 
        zx(1)=int(npin/2.0)+1 
        zy(1)=int(npin/2.0)+1 

        ax(2)=zx(1)
        ay(2)=1    
        zx(2)=npin
        zy(2)=zy(1) 

        ax(3)=1     
        ay(3)=zy(1)
        zx(3)=zx(1)           
        zy(3)=npin

        ax(4)=ax(2)
        ay(4)=ay(3) 
        zx(4)=npin 
        zy(4)=npin 

        !write(*,*) ax
        !write(*,*) zx
        !write(*,*) ay
        !write(*,*) zy
      endif

      do a=1,nasst
        sym=getsym(a)
        do k=1,nax
          do n=1,4 
            if (nodef(sym,n)==0) cycle
            vol=0.
            do pj=ay(n),zy(n)
              do pi=ax(n),zx(n)
                if (types(a,pi,pj)==1) then

                  vtmp=vols(a,k,pi,pj)
                  if (.not.iseven) then
                    if (mult(a,k,pi,pj)==1) then    ! if its a full pin voiume
                      if (pi==ax(2)) vtmp=vtmp*0.5  ! it shared between nodes
                      if (pj==ay(3)) vtmp=vtmp*0.5
                    endif
                  endif
                  
                  nodpow(a,k,n)=nodpow(a,k,n)+power(a,k,pi,pj)*vtmp
                  nodsig(a,k,n)=nodsig(a,k,n)+absig(a,k,pi,pj)**2*vtmp**2
                  vol=vol+vtmp 
                endif
              enddo
            enddo
            if (vol>0.0) then
              nodpow(a,k,n)=nodpow(a,k,n)/vol
              nodsig(a,k,n)=sqrt(nodsig(a,k,n)/vol)/sqrt(vol) 
              nodsig(a,k,n)=nodsig(a,k,n)/nodpow(a,k,n)*100.0
            endif
          enddo
        enddo
      enddo
 
      !this section is for testing
      !k=1
      !do a=1,nasst
      !  sym=getsym(a)
      !  write(*,*) 'Assembly ',a,'  sim=',sym
        !do pj=1,npin
        !  write(*,'(17(f8.5))') (mult(a,k,pi,pj),pi=1,npin)
        !enddo
        !write(*,*)
        !do pj=1,npin
        !  write(*,'(17(f8.5))') (vols(a,k,pi,pj),pi=1,npin)
        !enddo
        !write(*,*)
        !do pj=1,npin
        !  write(*,'(17(f8.5))') (power(a,k,pi,pj),pi=1,npin)
        !enddo
        !write(*,*)
        !do nj=1,2
        !  write(*,'(2(f8.5))') (nodpow(a,k,ni+(nj-1)*2),ni=1,2)
        !enddo
      !enddo
!--- calcuate axial offset 

      hmid=axmesh(nax+1)/2.0   ! midpoint of the fuel
      pbot=0.0
      ptop=0.0
      do k=1,nax
        if (axmesh(k+1)<=hmid) then
          pbot=pbot+axials(k)*dz(k)
        elseif (axmesh(k)<hmid) then
          pbot=pbot+axials(k)*(hmid-axmesh(k))
          ptop=ptop+axials(k)*(axmesh(k+1)-hmid)
        else
          ptop=ptop+axials(k)*dz(k)
        endif
      enddo
      axial_offset=(ptop-pbot)/(ptop+pbot)*100.0

!--- output

      write(2,*)
      write(*,91) ' Average power = ',avgpow,avgsig
      write(2,91) ' Average power = ',avgpow,avgsig
      write(2,91) ' Maximum power = ',maxpow(1),maxpow(2)
      write(2,91) ' Minimum power = ',minpow(1),minpow(2)
      write(2,91) ' Maximum sigma = ',maxsig(1),maxsig(2)
      write(2,91) ' Minimum sigma = ',minsig(1),minsig(2)
      write(2,89)  ' Axial Offset = ',axial_offset
      write(*,*)
      write(2,*)
      write(2,*) ' Power dependent maximum sigmas'
      write(*,*) '---------------------------------'
      write(*,90) '     < 0.5 = ',maxsigp(1)
      write(*,90) ' 0.5 - 1.0 = ',maxsigp(2)
      write(*,90) '     > 1.0 = ',maxsigp(3)
      write(2,*) '---------------------------------'
      write(2,90) '     < 0.5 = ',maxsigp(1)
      write(2,90) ' 0.5 - 1.0 = ',maxsigp(2)
      write(2,90) '     > 1.0 = ',maxsigp(3)
      if (octant_symmetry) then
        write(2,*)
        write(2,*) ' Octant symmetry statistics'
        write(2,*) '---------------------------------'
        write(2,'(a,f8.5)') '  Average Difference = ',avgoctdiff
        write(2,'(a,f8.5)') '  Std Dev Difference = ',sigoctdiff
        write(2,'(a,f8.5)') '  Maximum Difference = ',maxoctdiff
        write(2,'(a,f8.5)') '      Max Diff Pow 1 = ',maxoctpow(1)
        write(2,'(a,f8.5)') '      Max Diff Pow 2 = ',maxoctpow(2)
        write(2,'(a,f8.5)') '      Max Diff Unc 1 = ',maxoctpow(1)*maxoctsig(1)/100.0
        write(2,'(a,f8.5)') '      Max Diff Unc 2 = ',maxoctpow(2)*maxoctsig(2)/100.0
        write(2,'(a,f5.1)') '    Number of Sigmas = ', maxoctdiff/ &
             sqrt((maxoctpow(1)*maxoctsig(1)/100.0)**2+ &
                  (maxoctpow(2)*maxoctsig(2)/100.0)**2)
      endif
      write(2,*)
      write(2,*) ' Axial Powers'
      write(2,*)
      write(2,*) ' Level   Height        Axial Power     Avg Pin Unc'
      write(2,*) '----------------------------------------------------'
      do k=nax,1,-1
        write(2,92), k+kmin-1,axmids(k),axials(k),axsigs(k),axsigs2(k)
      enddo
      write(2,*)
      write(2,*) ' Assembly Radial Powers'
      write(2,*) '-----------------------------'
      nassx=nass
      do aj=1,nass
        if (octant_symmetry) nassx=aj
        lasta=1
        do ai=2,nassx
          if (assmap(ai,aj)>0) then
            lasta=ai
            IF(lasta) THEN
              tmpint=1
            ELSE
              tmpint=0
            ENDIF
          endif
        enddo
        write(2,94) (assrad(assmap(ai,aj)),ai=1,tmpint)
      enddo
      write(2,*)
      write(2,*) ' Assembly Radial Uncertainty'
      write(2,*) '-----------------------------'
      do aj=1,nass
        if (octant_symmetry) nassx=aj
        lasta=1
        do ai=2,nassx
          if (assmap(ai,aj)>0) then
            lasta=ai
            IF(lasta) THEN
              tmpint=1
            ELSE
              tmpint=0
            ENDIF
          endif
        enddo
! TODO: the end of the below line had lasta instead of tmpint
        write(2,101) (assrsg(assmap(ai,aj)),ai=1,tmpint)
      enddo
      write(2,*)
      write(2,*) ' Assembly Radial Avg Pin Uncertainty'
      write(2,*) '-------------------------------------'
      do aj=1,nass
        if (octant_symmetry) nassx=aj
        lasta=1
        do ai=2,nassx
          if (assmap(ai,aj)>0) then
            lasta=ai
            IF(lasta) THEN
              tmpint=1
            ELSE
              tmpint=0
            ENDIF
          endif
        enddo
        write(2,101) (assrsg2(assmap(ai,aj)),ai=1,tmpint)
      enddo
      write(2,*)
      write(2,*) ' Assembly Axial Powers'
      write(2,*)
      write(2,*) ' Level   Height       Axial Powers'
      write(2,*) '--------------------------------------'
      allocate(temp(nasst))
      nassx=nass
      cnt=0
      do aj=1,nass
        if (octant_symmetry) nassx=aj
        do ai=1,nassx
           if (assmap(ai,aj)>0) then
              cnt=cnt+1
              write(temp(cnt),95) ai,aj
           endif
        enddo
      enddo
      write(2,98) (trim(temp(i)),i=1,cnt)
      do k=nax,1,-1
        cnt=0
        do aj=1,nass
          if (octant_symmetry) nassx=aj
          do ai=1,nassx
             a=assmap(ai,aj)
             if (a>0) then
                cnt=cnt+1
                write(temp(cnt),96) asspow(a,k),asssig(a,k)
             endif
          enddo
        enddo
        write(2,97) k+kmin-1,axmids(k),(trim(temp(i)),i=1,cnt)
      enddo
      deallocate(temp)
      nassx=nass
      write(2,*)
      write(2,*) ' Radial Pin Powers'
      write(2,*) '-----------------------------------'
      do aj=1,nass
        if (octant_symmetry) nassx=aj
        do ai=1,nassx
          a=assmap(ai,aj)
          if (maxxpins(a)==0) cycle
          write(2,99) '  Assembly:',a
          if (ai==aj.and.octant_symmetry) then
            do pj=minypins(a),maxypins(a)
               write(2,93) (radials(a,pi,pj),pi=minxpins(a),pj)
            enddo
          else
            do pj=minypins(a),maxypins(a) 
               write(2,93) (radials(a,pi,pj),pi=minxpins(a),maxxpins(a))
            enddo
          endif
          write(2,*)
        enddo
      enddo
      write(2,*)
      write(2,*) ' Radial Pin Power Uncertainties'
      write(2,*) '-----------------------------------'
      do aj=1,nass
        if (octant_symmetry) nassx=aj
        do ai=1,nassx
          a=assmap(ai,aj)
          if (maxxpins(a)==0) cycle
          write(2,99) '  Assembly:',a
          if (ai==aj.and.octant_symmetry) then
            do pj=minypins(a),maxypins(a)
                write(2,100) (radsigs(a,pi,pj),pi=minxpins(a),pj)
            enddo
          else
            do pj=minypins(a),maxypins(a)
                write(2,100) (radsigs(a,pi,pj),pi=minxpins(a),maxxpins(a))
            enddo
          endif
          write(2,*)
        enddo
      enddo
      write(2,*)
      write(2,*) ' Radial Average Pin Uncertainties'
      write(2,*) '-----------------------------------'
      do aj=1,nass
        if (octant_symmetry) nassx=aj
        do ai=1,nassx
          a=assmap(ai,aj)
          if (maxxpins(a)==0) cycle
          write(2,99) '  Assembly:',a
          if (ai==aj.and.octant_symmetry) then
            do pj=minypins(a),maxypins(a)
                write(2,100) (radsigs2(a,pi,pj),pi=minxpins(a),pj)
            enddo
          else
            do pj=minypins(a),maxypins(a)
                write(2,100) (radsigs2(a,pi,pj),pi=minxpins(a),maxxpins(a))
            enddo
          endif
          write(2,*)
        enddo
      enddo
!
! write full model output to new csv file
!
      nassx=nass
      open(unit=11,file='kenopow.csv',status='unknown')
      do k=1,nax 
        write(11,*) 
        write(11,'(a,i0,a)') ' <<< Axial Level = ',k+kmin-1,' >>>'
        do aj=1,nass
          a=assmap(1,aj)
          if (maxxpins(a)==0) cycle
          if (octant_symmetry) nassx=aj
          do pj=minypins(a),maxypins(a)
            do ai=1,nassx
              a=assmap(ai,aj)
              if (maxxpins(a)==0) cycle
              if (ai==aj.and.octant_symmetry) then
                npinx=pj
              else
                npinx=maxxpins(a)
              endif
              do pi=minxpins(a),npinx            
                write(11,'(f8.5,'','')',advance='no') power(a,k,pi,pj)
              enddo
            enddo
            write(11,*)
          enddo
        enddo 
        write(11,*)
        do aj=1,nass
          a=assmap(1,aj)
          if (maxxpins(a)==0) cycle
          if (octant_symmetry) nassx=aj
          do pj=minypins(a),maxypins(a)
            do ai=1,nassx
              a=assmap(ai,aj)
              if (maxxpins(a)==0) cycle
              if (ai==aj.and.octant_symmetry) then
                npinx=pj
              else
                npinx=maxxpins(a)
              endif
              do pi=minxpins(a),npinx            
                write(11,'(f6.3,''%,'')',advance='no') sigma(a,k,pi,pj)
              enddo
            enddo
            write(11,*)
          enddo
        enddo 
        write(11,*)
        do aj=1,nass
          a=assmap(1,aj)
          if (maxxpins(a)==0) cycle
          if (octant_symmetry) nassx=aj
          do pj=minypins(a),maxypins(a)
            do ai=1,nassx
              a=assmap(ai,aj)
              if (maxxpins(a)==0) cycle
              if (ai==aj.and.octant_symmetry) then
                npinx=pj
              else
                npinx=maxxpins(a)
              endif
              do pi=minxpins(a),npinx            
                sum=vols(a,k,pi,pj)
                if (octant_symmetry) then
                  if (ai==aj .and. pi==pj) then
                  else
                    sum=sum+vols(a,k,pi,pj)
                  endif
                endif 
                write(11,'(1p,e12.5,'','')',advance='no') sum
              enddo
            enddo
            write(11,*)
          enddo
        enddo 
      enddo
      if (nax/=1) then
      write(11,*) 
      write(11,'(a,i0,a)') ' << Radial Results (Axially Integrated)>>> '
      do aj=1,nass
        a=assmap(1,aj)
        if (maxxpins(a)==0) cycle
        if (octant_symmetry) nassx=aj
        do pj=minypins(a),maxypins(a)
          do ai=1,nassx
            a=assmap(ai,aj)
            if (maxxpins(a)==0) cycle
            if (ai==aj.and.octant_symmetry) then
              npinx=pj
            else
              npinx=maxxpins(a)
            endif
            do pi=minxpins(a),npinx            
              write(11,'(f8.5,'','')',advance='no') radials(a,pi,pj)
            enddo
          enddo
          write(11,*)
        enddo
      enddo 
      write(11,*)
      do aj=1,nass
        a=assmap(1,aj)
        if (maxxpins(a)==0) cycle
        if (octant_symmetry) nassx=aj
        do pj=minypins(a),maxypins(a)
          do ai=1,nassx
            a=assmap(ai,aj)
            if (maxxpins(a)==0) cycle
            if (ai==aj.and.octant_symmetry) then
              npinx=pj
            else
              npinx=maxxpins(a)
            endif
            do pi=minxpins(a),npinx            
              if (radials(a,pi,pj)==0.0) then
                write(11,'(f6.3,''%,'')',advance='no') 0.0
              else
                write(11,'(f6.3,''%,'')',advance='no') radsigs(a,pi,pj)
              endif
            enddo
          enddo
          write(11,*)
        enddo
      enddo 
      write(11,*)
      do aj=1,nass
        a=assmap(1,aj)
        if (maxxpins(a)==0) cycle
        if (octant_symmetry) nassx=aj
        do pj=minypins(a),maxypins(a)
          do ai=1,nassx
            a=assmap(ai,aj)
            if (maxxpins(a)==0) cycle
            if (ai==aj.and.octant_symmetry) then
              npinx=pj
            else
              npinx=maxxpins(a)
            endif
            do pi=minxpins(a),npinx            
              if (radials(a,pi,pj)==0.0) then
                write(11,'(f6.3,''%,'')',advance='no') 0.0
              else
                write(11,'(f6.3,''%,'')',advance='no') radsigs2(a,pi,pj)
              endif
            enddo
          enddo
          write(11,*)
        enddo
      enddo 
      write(11,*)
      do aj=1,nass
        a=assmap(1,aj)
        if (maxxpins(a)==0) cycle
        if (octant_symmetry) nassx=aj
        do pj=minypins(a),maxypins(a)
          do ai=1,nassx
            a=assmap(ai,aj)
            if (maxxpins(a)==0) cycle
            if (ai==aj.and.octant_symmetry) then
              npinx=pj
            else
              npinx=maxxpins(a)
            endif
            do pi=minxpins(a),npinx            
              sum=0
              do k=1,nax 
                sum=vols(a,k,pi,pj)
                if (octant_symmetry) then
                  if (ai==aj .and. pi==pj) then
                  else
                    sum=sum+vols(a,k,pi,pj)
                  endif
                endif 
              enddo
              write(11,'(1p,e12.5,'','')',advance='no') sum
            enddo
          enddo
          write(11,*)
        enddo
      enddo 
      endif
      close(11)
      deallocate(absig)
!
 89   format(1x,a,f7.3,'%')
 90   format(1x,a,f6.3,'%')
 91   format(a,f8.5,' +/-',f6.3,'%')
 92   format(3x,i3,2x,f9.4,2x,f8.5,' +/-',f6.3,'%',2x,f6.3,'%')
 93   format(1x,17(1x,f8.5),3x,17(1x,f6.3,'%'))
 94   format(1x,15(1x,f8.5))
 95   format(1x,'[',i0,',',i0,']')
 96   format(f8.5,' +/-',f6.3,'%')
 97   format(3x,i3,2x,f9.4,2x,100(a,1x))
 98   format(3x,3x,2x,9x,2x,100(7x,a,7x))
 99   format(1x,a,'[',i0,']')
 100  format(1x,17(1x,f6.3,'%'))
 101  format(1x,15(1x,f6.3,'%'))
      end subroutine
