!---------------------------------------------------------------------!
!                                                                     !
! Eighth collapse from quarter assembly with symmetry                 !
!  maintains quarter assembly geometry, in the quarter array          !
!                                                                     !
!---------------------------------------------------------------------!
      subroutine collapsefissions()
      use global
      implicit none
      integer    :: ai,aj,pi,pj,k,j,a1,a2  ! lower left octant indices
      real*8     :: sum,sumsq  ! get the statistics on the octant pairs
      real*8     :: diff, vol
      
     !integer    :: cnt,nlocs
     !character(len=20),allocatable :: headers(:)
     !real*8           ,allocatable :: values(:)

      sum=0.0
      sumsq=0.0
      maxoctdiff=-1
      vol=0.0

      do aj=1,nass
        do ai=1,aj
          a1=assmap(ai,aj)
          a2=assmap(aj,ai)
          if (a1==0 .or. a2==0) cycle
          do pj=1,npin
            do pi=1,npin
              if (types(a1,pi,pj)/=1) cycle             !assume types is symmetric
              if (ai==aj.and.pi>=pj) cycle
              do k=1,nax 
                diff=fissn(a1,k,pi,pj)-fissn(a2,k,pj,pi)
                if (abs(diff) > maxoctdiff) then
                  maxoctdiff = abs(diff)
                  maxoctpow(1)=fissn(a1,k,pi,pj)
                  maxoctpow(2)=fissn(a2,k,pj,pi)
                  maxoctsig(1)=sigma(a1,k,pi,pj)
                  maxoctsig(2)=sigma(a2,k,pj,pi)
                endif

                sum=sum+diff*vols(a1,k,pi,pj)           !assume volume is same in each pin
                sumsq=sumsq+diff*diff*vols(a1,k,pi,pj) 
                vol=vol+vols(a1,k,pi,pj) 

                fissn(a1,k,pi,pj)=(fissn(a1,k,pi,pj)+ &
                                   fissn(a2,k,pj,pi))/2.0
                sigma(a1,k,pi,pj)=sqrt((sigma(a1,k,pi,pj)**2+ &
                                        sigma(a2,k,pj,pi)**2)/2.0)/sqrt(2.0)
                fissn(a2,k,pj,pi)=fissn(a1,k,pi,pj)
                sigma(a2,k,pj,pi)=sigma(a1,k,pi,pj)
              enddo
            enddo
          enddo
        enddo
      enddo

!- save statistics on octant pairs
      avgoctdiff = sum/vol
      sigoctdiff = sqrt(sumsq/vol-(sum/vol)**2)

!print a large csv table for excel
!     open(unit=8,file='rods.csv',status='old',access='append')
!     write(8,*)
!     nlocs=nasst*npin*npin
!     allocate(headers(nlocs))
!     allocate( values(nlocs))
!     cnt=0
!     do a1=1,nasst
!       do pj=1,npin
!         do pi=1,npin
!           if (types(pj,pi,a1)==1) then
!             cnt=cnt+1
!             write(headers(cnt),60) a1,pi,pj
!           endif
!         enddo
!       enddo
!     enddo
!     write(8,61) 'k',(trim(headers(j)),j=1,cnt)
!     do k=1,nax 
!       cnt=0
!       values(:)=0.0
!       do a1=1,nasst
!         do pj=1,npin
!           do pi=1,npin
!             if (types(pj,pi,a1)==1) then
!               cnt=cnt+1
!               values(cnt)=fissn(a1,k,pi,pj)
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
!       do a1=1,nasst
!         do pj=1,npin
!           do pi=1,npin
!             if (types(pj,pi,a1)==1) then
!               cnt=cnt+1
!               values(cnt)=sigma(a1,k,pi,pj)
!             endif
!           enddo
!         enddo
!       enddo
!       write(8,62) k,(values(j),j=1,cnt)
!     enddo
!60   format('[',2(i0,1x),i0,']')
!61   format(a,',',<cnt>(a,','))
!62   format(i0,',',<cnt>(f9.6,','))
!     close(8)
!     deallocate(values)
!     deallocate(headers)
      end subroutine
