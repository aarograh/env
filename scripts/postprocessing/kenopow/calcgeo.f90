      subroutine calcgeo
      use global
      use constants
      implicit none
      integer :: a,sym,i,j,m,ai,aj
      integer :: getsym                   !external function
      logical :: match 

!--- for it to be core qtr symmetry, we need to verify all the assembly symmetries

      allocate(asssym(nasst))
      do a=1,nasst
        asssym(a)=getsym(a)
      enddo
      
      match=.true.
      
      do aj=1,nass
        do ai=1,nass
          a=assmap(ai,aj)
          if (a==1) then
            if (asssym(a)/=SYM_QTR_SOUTHEAST) then
              match=.false.
            endif
          elseif (aj==1) then
            if (asssym(a)/=SYM_HALF_SOUTH) then
              match=.false.
            endif
          elseif (ai==1) then
            if (asssym(a)/=SYM_HALF_EAST) then
              match=.false.
            endif
          else
            if (asssym(a)/=SYM_FULL) then
              match=.false.
            endif
          endif
        enddo
      enddo
  
      if (match) then
        sym=SYM_QTR_SOUTHEAST
      else
        sym=SYM_FULL
      endif
 
      if (sym==SYM_FULL) then 

        core_sym=sym
        core_size=nass
        allocate(core_map(core_size,core_size))
        do j=1,core_size
          do i=1,core_size
            core_map(i,j)=assmap(i,j)
          enddo
        enddo

      elseif (sym==SYM_QTR_SOUTHEAST) then 

        core_sym=sym
        core_size=int((nass-0.5)*2.0)            ! assumes odd core size
        allocate(core_map(core_size,core_size))
        core_map(:,:)=0
        m=core_size-nass
        do j=1,nass     
          do i=1,nass      
            core_map(i+m,j+m)=assmap(i,j)
          enddo
        enddo
        
        call makefullint(core_map,core_size,core_sym)

!       write(*,*)
!       write(*,*) 'checking core map'
!       do j=1,core_size
!         write(*,'(15(i3))') (core_map(i,j),i=1,core_size)
!       enddo
!       write(*,*)

      else 
        write(*,*) 'Unsupported symmetry option'
        write(*,*) ' assembly symmetry = ',sym
        stop 
      endif
      end subroutine
