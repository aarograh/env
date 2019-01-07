      subroutine normalize
      use global
      implicit none
      integer :: a,ai,aj,pi,pj,k,j
      real*8  :: sum,vol

     !character(len=20),allocatable :: headers(:)
     !real*8           ,allocatable :: values(:)
     !integer                       :: cnt,nlocs

!---------
      sum=0.0
      vol=0.0
      power(:,:,:,:)=0.0
      do pj=1,npin
        do pi=1,npin
          do k=1,nax 
            do a=1,nasst
              sum=sum+fissn(a,k,pi,pj)*vols(a,k,pi,pj)
              vol=vol+vols(a,k,pi,pj)
            enddo
          enddo
        enddo
      enddo
      if (sum==0.0) then
        write(*,*) 'no fissions - cannot normalize'
        stop
      endif
      do pj=1,npin
        do pi=1,npin
          do k=1,nax 
            do a=1,nasst
              power(a,k,pi,pj)=fissn(a,k,pi,pj)*vol/sum
            enddo
          enddo
        enddo
      enddo

      avgoctdiff = avgoctdiff*vol/sum
      sigoctdiff = sigoctdiff*vol/sum
      maxoctdiff = maxoctdiff*vol/sum
      maxoctpow(:)=maxoctpow(:)*vol/sum

!      do a=1,nasst
!        write(*,*) 'Assembly ',a
!        do k=1,nax 
!         do pj=1,npin
!            write(*,'(17f7.4)') (power(a,k,pi,pj),pi=1,npin)
!          enddo
!        enddo
!      enddo
!print debugging file
!     open(unit=8,file='rods.txt',status='old',access='append')
!     write(8,*)
!     write(8,*) 'normalized pin powers'
!     do a=1,nasst
!       do pj=1,npin
!         do pi=1,npin  
!           if (types(pj,pi,a)==1) then
!             write(8,51) 'Assembly = ',a
!             write(8,51) 'Rod location = ',pi,pj
!             do k=nax,1,-1
!               write(8,52) k,dz(k),vols(a,k,pi,pj), &
!                                   mult(a,k,pi,pj), &
!                                  power(a,k,pi,pj), &
!                                  sigma(a,k,pi,pj), &
!                             trim(names(a,k,pi,pj))
!             enddo
!           endif
!         enddo
!       enddo
!     enddo
!51   format(1x,a,i0,1x,i0)
!52   format(1x,i3,es12.5,f10.7,f5.2,f8.5,f5.2,a)
!     close(8)
!print a large csv table for excel
!     open(unit=8,file='power.csv',status='unknown')
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
!     write(8,61) 'k','dz',(trim(headers(j)),j=1,cnt)
!     do k=1,nax 
!       cnt=0
!       values(:)=0.0
!       do a=1,nasst
!         do pj=1,npin
!           do pi=1,npin 
!             if (types(pj,pi,a)==1) then
!               cnt=cnt+1
!               values(cnt)=power(a,k,pi,pj)
!             endif
!           enddo
!         enddo
!       enddo
!       write(8,62) k,dz(k),(values(j),j=1,cnt)
!     enddo
!     write(8,*)
!     write(8,61) 'k','dz',(trim(headers(j)),j=1,cnt)
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
!       write(8,62) k,dz(k),(values(j),j=1,cnt)
!     enddo
!     write(8,*)
!     write(8,61) 'k','dz',(trim(headers(j)),j=1,cnt)
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
!       write(8,62) k,dz(k),(values(j),j=1,cnt)
!     enddo
!60   format('[',2(i0,1x),i0,']')
!61   format(2(a,','),<cnt>(a,','))
!62   format(i0,',',<cnt+1>(f9.6,','))
!     close(8)
!     deallocate(values)
!     deallocate(headers)
      end subroutine
