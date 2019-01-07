!-----------------------------------------------------------------------
!
!  Gets the fission rate density and percent standard deviation 
!   in each unit
!
!-----------------------------------------------------------------------
      subroutine getfissions()
      use global
      implicit none
      character(len=132)            :: line
      character(len=48)             :: key
      integer                       :: num,ai,aj,pi,pj,k,i,j,a
      real*8                        :: rx,sig,fd

!     character(len=20),allocatable :: headers(:)
!     real*8           ,allocatable :: values(:)
!     integer                       :: cnt,nlocs
      
      key='**** fission densities ****'
      line=''      
      do while (index(line, key)==0) 
        read(7,'(a)') line
      enddo
      do i=1,5
        read(7,*)
      enddo

      fissn(:,:,:,:)=0.0
      sigma(:,:,:,:)=0.0

!--- reading this table is KENO version specific
      key='frequency for generations'
      line=''
      do while (index(line, trim(key))==0) 
        read(7,'(a)') line
        if (len_trim(line(1:10))/=0) cycle 
        if (index(line,'unit')/=0) cycle
        if (len_trim(line(13:18))/=0) then
          read(line(13:18),*) num
          read(line(75:90),*) rx  
          read(line(91:99),*) sig
          read(line(100:115),*) fd  
          if (num<maxunits) then
            call getloc(num,ai,aj,pi,pj,k,a)
            if (a>0) then
              fissn(a,k,pi,pj)=rx
              sigma(a,k,pi,pj)=sig

! - read all the regions for this unit and sum 
              read(7,'(a)') line
              do while (len_trim(line(75:90))>0)
                read(line(75:90),*) rx  
                read(line(91:97),*) sig
                read(line(100:115),*) fd  
                if (rx>0.0) then
                  fissn(a,k,pi,pj)=fissn(a,k,pi,pj)+rx
                  sigma(a,k,pi,pj)=sqrt(sigma(a,k,pi,pj)**2+sig**2)
                endif
                read(7,'(a)') line
              enddo
            endif
          endif
        endif
      enddo

!- replace volume with dz to normalize to linear power
      write(*,*) 'Converting Fission Density to Linear Fissions'
      do k=1,nax
        do pj=1,npin
          do pi=1,npin
            do a=1,nasst
              if (mult(a,k,pi,pj)/=0) then
                fissn(a,k,pi,pj)=fissn(a,k,pi,pj)*vols(a,k,pi,pj)/dz(k)/mult(a,k,pi,pj)
                vols(a,k,pi,pj)=dz(k)*mult(a,k,pi,pj)
              endif
            enddo
          enddo
        enddo
      enddo

!--- print debugging file
!     open(unit=8,file='rods.txt',status='unknown')
!     do a=1,nasst
!       do pj=1,npin
!         do pi=1,npin
!           if (types(pj,pi,a)==1) then
!             write(8,51) 'Assembly = ',a     
!             write(8,51) 'Rod location = ',pi,pj
!             do k=nax,1,-1
!               write(8,52) k,dz(k),vols(a,k,pi,pj), &
!                                   mult(a,k,pi,pj), &
!                                  fissn(a,k,pi,pj), &
!                                  sigma(a,k,pi,pj), &
!                             trim(names(a,k,pi,pj))
!             enddo
!           endif
!         enddo
!       enddo
!     enddo
!51   format(1x,a,i0,1x,i0)
!52   format(1x,i3,es12.5,f10.7,f5.2,es10.3,f5.2,a)
!     close(8)

!print a large csv table for excel
!     open(unit=8,file='rods.csv',status='unknown')
!     nlocs=nasst*npin*npin
!     allocate(headers(nlocs))
!     allocate( values(nlocs))
!     cnt=0
!     do a=1,nasst
!       do pj=1,npin
!         do pi=1,npin
!           if (types(pj,pi,a)==1) then
!             cnt=cnt+1
!             write(headers(cnt),60) a,pi,pj
!           endif
!         enddo
!       enddo
!     enddo
!     write(8,61) 'k',(trim(headers(j)),j=1,cnt)
!     do k=1,nax    
!       cnt=0
!       values(:)=0.0
!       do a=1,nasst
!         do pj=1,npin
!           do pi=1,npin
!             if (types(pj,pi,a)==1) then
!               cnt=cnt+1
!               values(cnt)=fissn(a,k,pi,pj)
!             endif
!           enddo
!         enddo
!       enddo
!       write(8,62) k,(values(j),j=1,cnt)
!     enddo
!     write(8,*)
!     write(8,61) 'k',(trim(headers(j)),j=1,cnt)
!     do k=1,nax    
!       cnt=0
!       values(:)=0.0
!       do a=1,nasst
!         do pj=1,npin
!           do pi=1,npin
!             if (types(pj,pi,a)==1) then
!               cnt=cnt+1
!               values(cnt)=sigma(a,k,pi,pj)
!             endif
!           enddo
!         enddo
!       enddo
!       write(8,62) k,(values(j),j=1,cnt)
!     enddo
!     write(8,*)
!     write(8,61) 'k',(trim(headers(j)),j=1,cnt)
!     do k=1,nax 
!       cnt=0
!       values(:)=0.0
!       do a=1,nasst
!         do pj=1,npin
!           do pi=1,npin
!             if (types(pj,pi,a)==1) then
!               cnt=cnt+1
!               values(cnt)=vols(a,k,pi,pj)
!             endif
!           enddo
!         enddo
!       enddo
!       write(8,62) k,(values(j),j=1,cnt)
!     enddo
!     write(8,*)
!     write(8,61) 'k',(trim(headers(j)),j=1,cnt)
!     do k=1,nax 
!       cnt=0
!       values(:)=0.0
!       do a=1,nasst
!         do pj=1,npin
!           do pi=1,npin
!             if (types(pj,pi,a)==1) then
!               cnt=cnt+1
!               values(cnt)=mult(a,k,pi,pj)
!             endif
!           enddo
!         enddo
!       enddo
!       write(8,62) k,(values(j),j=1,cnt)
!     enddo
!60   format('[',2(i0,1x),i0,']')
!61   format(a,',',<nlocs>(a,','))
!62   format(i0,',',<nlocs>(f9.6,','))
!     close(8)
!     deallocate(values)
!     deallocate(headers)
      end subroutine
