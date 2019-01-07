      function getsym(assy)
      use global
      use constants
      implicit none
      integer, intent(in) :: assy     ! assembly index
      integer             :: mpin     ! index of the midpoint of the lattice
      integer             :: ax,bx,ay,by
      integer             :: numx,numy
      integer             :: npins    ! max numner of pins accross a full assembly
      integer             :: getsym

      ax=minxpins(assy)
      bx=maxxpins(assy)
      ay=minypins(assy)
      by=maxypins(assy)
      numx=bx-ax+1
      numy=by-ay+1
      npins=npin                     !need to check this for weird cases
                                     !assumes that if quarter symmetry then assembly 1 must be SOUTHEAST symmetry
      mpin=int(npins/2)+1

      if (numx==npins.and.numy==npins) then
        getsym=SYM_FULL
        return
      endif

      if (numx==npins) then
        if (ay==1.and.by==mpin) then
          getsym=SYM_HALF_NORTH
          return
        else if (ay==mpin.and.by==npins) then
          getsym=SYM_HALF_SOUTH
          return
        endif
      endif

      if (numy==npins) then
        if (ax==1.and.bx==mpin) then
          getsym=SYM_HALF_WEST 
          return
        else if (ax==mpin.and.bx==npins) then
          getsym=SYM_HALF_EAST 
          return
        endif
      endif

      if (ax==1.and.bx==mpin) then
        if (ay==1.and.by==mpin) then
          getsym=SYM_QTR_NORTHWEST
          return
        elseif (ay==mpin.and.by==npins) then
          getsym=SYM_QTR_SOUTHWEST
          return
        endif
      elseif (ax==mpin.and.bx==npins) then
        if (ay==1.and.by==mpin) then
          getsym=SYM_QTR_NORTHEAST
          return
        elseif (ay==mpin.and.by==npins) then
          getsym=SYM_QTR_SOUTHEAST
          return
        endif
      endif

      write(*,*) 'ERROR: Pin indices don''t make sense'
      write(*,*) 'Assembly: ',assy
      write(*,*) ' Min/Max x pin: ',ax,bx
      write(*,*) ' Min/Max y pin: ',ay,by
      stop
      endfunction

      subroutine getsizes(sym,xx,yy)
      use global, only: npin  
      use constants
      implicit none
      integer, intent(in)  :: sym ! symmetry option
      integer, intent(out) :: xx  ! num pins accross
      integer, intent(out) :: yy  ! num pins vertically
      
      select case (sym)
      case (SYM_FULL)
        xx=npin
        yy=npin
      case (SYM_HALF_NORTH)
        xx=npin
        yy=int(npin/2)+1
      case (SYM_HALF_SOUTH)
        xx=npin
        yy=int(npin/2)+1
      case (SYM_HALF_EAST)
        xx=int(npin/2)+1
        yy=npin
      case (SYM_HALF_WEST)
        xx=int(npin/2)+1
        yy=npin
      case (SYM_QTR_NORTHEAST)
        xx=int(npin/2)+1
        yy=xx
      case (SYM_QTR_SOUTHEAST)
        xx=int(npin/2)+1
        yy=xx
      case (SYM_QTR_NORTHWEST)
        xx=int(npin/2)+1
        yy=xx
      case (SYM_QTR_SOUTHWEST)
        xx=int(npin/2)+1
        yy=xx
      end select
      endsubroutine

      function nodef(sym,node)
      use constants
      implicit none
      integer, intent(in) :: sym
      integer, intent(in) :: node
      integer nodef
      nodef=0
      select case (sym)
      case (SYM_FULL)
        nodef=1
      case (SYM_HALF_NORTH)
        if (node==1 .or. node==2) nodef=1
      case (SYM_HALF_SOUTH)
        if (node==3 .or. node==4) nodef=1
      case (SYM_HALF_EAST)
        if (node==2 .or. node==4) nodef=1
      case (SYM_HALF_WEST)
        if (node==1 .or. node==2) nodef=1
      case (SYM_QTR_NORTHEAST)
        if (node==2) nodef=1
      case (SYM_QTR_SOUTHEAST)
        if (node==4) nodef=1
      case (SYM_QTR_NORTHWEST)
        if (node==1) nodef=1
      case (SYM_QTR_SOUTHWEST)
        if (node==3) nodef=1
      end select
      return
      end function
