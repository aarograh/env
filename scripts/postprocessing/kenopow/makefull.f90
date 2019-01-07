      subroutine makefull(dat,siz,sym)
      use constants
      implicit none
      integer,intent(in)     :: siz
      real*8 ,intent(inout)  :: dat(siz,siz) 
      integer,intent(in)     :: sym 
      integer                :: i,j,m

      if (sym==SYM_FULL) then

        return

      elseif (sym==SYM_HALF_NORTH) then

        m=int(siz/2.0)+2
        do j=m,siz
          do i=1,siz 
            dat(i,j)=dat(i,siz-j+1)
          enddo
        enddo

      elseif (sym==SYM_HALF_SOUTH) then

        m=int(siz/2.0)
        do j=1,m 
          do i=1,siz 
            dat(i,j)=dat(i,siz-j+1)
          enddo
        enddo

      elseif (sym==SYM_HALF_EAST) then

        m=int(siz/2.0)
        do j=1,siz
          do i=1,m         
            dat(i,j)=dat(siz-i+1,j)
          enddo
        enddo

      elseif (sym==SYM_HALF_WEST) then

        m=int(siz/2.0)+2
        do j=1,siz
          do i=m,siz
            dat(i,j)=dat(siz-i+1,j)
          enddo
        enddo

      elseif (sym==SYM_QTR_NORTHEAST) then

        m=int(siz/2.0)
        do j=1,m+1   
          do i=1,m         
            dat(i,j)=dat(siz-i+1,j)
          enddo
        enddo
        m=int(siz/2.0)+2
        do j=m,siz 
          do i=1,siz 
            dat(i,j)=dat(i,siz-j+1)
          enddo
        enddo

      elseif (sym==SYM_QTR_SOUTHEAST) then

        m=int(siz/2.0)
        do j=m+1,siz
          do i=1,m         
            dat(i,j)=dat(siz-i+1,j)
          enddo
        enddo
        do j=1,m        
          do i=1,siz 
            dat(i,j)=dat(i,siz-j+1)
          enddo
        enddo

      elseif (sym==SYM_QTR_NORTHWEST) then

        m=int(siz/2.0)+2
        do j=1,m-1   
          do i=m,siz      
            dat(i,j)=dat(siz-i+1,j)
          enddo
        enddo
        do j=m,siz 
          do i=1,siz  
            dat(i,j)=dat(i,siz-j+1)
          enddo
        enddo

      elseif (sym==SYM_QTR_SOUTHWEST) then

        m=int(siz/2.0)+2
        do j=m+1,siz
          do i=m,siz      
            dat(i,j)=dat(siz-i+1,j)
          enddo
        enddo
        m=int(siz/2.0)
        do j=1,m        
          do i=1,siz  
            dat(i,j)=dat(i,siz-j+1)
          enddo
        enddo

      endif
      end subroutine

      subroutine makefullint(dat,siz,sym)
      use constants
      implicit none
      integer,intent(in)     :: siz
      integer,intent(inout)  :: dat(siz,siz) 
      integer,intent(in)     :: sym 
      integer                :: i,j,m

      if (sym==SYM_FULL) then

        return

      elseif (sym==SYM_HALF_NORTH) then

        m=int(siz/2.0)+2
        do j=m,siz
          do i=1,siz 
            dat(i,j)=dat(i,siz-j+1)
          enddo
        enddo

      elseif (sym==SYM_HALF_SOUTH) then

        m=int(siz/2.0)
        do j=1,m 
          do i=1,siz 
            dat(i,j)=dat(i,siz-j+1)
          enddo
        enddo

      elseif (sym==SYM_HALF_EAST) then

        m=int(siz/2.0)
        do j=1,siz
          do i=1,m         
            dat(i,j)=dat(siz-i+1,j)
          enddo
        enddo

      elseif (sym==SYM_HALF_WEST) then

        m=int(siz/2.0)+2
        do j=1,siz
          do i=m,siz
            dat(i,j)=dat(siz-i+1,j)
          enddo
        enddo

      elseif (sym==SYM_QTR_NORTHEAST) then

        m=int(siz/2.0)
        do j=1,m+1   
          do i=1,m         
            dat(i,j)=dat(siz-i+1,j)
          enddo
        enddo
        m=int(siz/2.0)+2
        do j=m,siz 
          do i=1,siz 
            dat(i,j)=dat(i,siz-j+1)
          enddo
        enddo

      elseif (sym==SYM_QTR_SOUTHEAST) then

        m=int(siz/2.0)
        do j=m+1,siz
          do i=1,m         
            dat(i,j)=dat(siz-i+1,j)
          enddo
        enddo
        do j=1,m        
          do i=1,siz 
            dat(i,j)=dat(i,siz-j+1)
          enddo
        enddo

      elseif (sym==SYM_QTR_NORTHWEST) then

        m=int(siz/2.0)+2
        do j=1,m-1   
          do i=m,siz      
            dat(i,j)=dat(siz-i+1,j)
          enddo
        enddo
        do j=m,siz 
          do i=1,siz  
            dat(i,j)=dat(i,siz-j+1)
          enddo
        enddo

      elseif (sym==SYM_QTR_SOUTHWEST) then

        m=int(siz/2.0)+2
        do j=m+1,siz
          do i=m,siz      
            dat(i,j)=dat(siz-i+1,j)
          enddo
        enddo
        m=int(siz/2.0)
        do j=1,m        
          do i=1,siz  
            dat(i,j)=dat(i,siz-j+1)
          enddo
        enddo

      endif
      end subroutine
