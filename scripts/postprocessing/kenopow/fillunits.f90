!----------------------------------------------------------------------
! Gets the unit name and height for each unit, and determines the 
! axial heights for the entire problem
!
! This may be unnecessary because the volume is coming from the
!  fuelunits file, but for now it is useful to at least have the 
!  unit descriptions and get the axial mesh
!----------------------------------------------------------------------
      subroutine fillunits()
      use global
      implicit none
      character(len=132)            :: line
      character(len=48)             :: key
      character(len=80)             :: desc                         ! unit descriptions
      real*8                        :: cells(maxcellshapes)         ! storage array for unit data
      integer                       :: num,bound,ai,aj,pi,pj,k,a
      integer                       :: xa,mm,nn,i,ndx
      real*8                        :: r,x,y,z
      
     ! write(*,*) 'Getting unit volumes...'

      key='volumes for those units utilized in this problem'
      line=''      
      do while (index(line, key)==0) 
        ndx=index(line, '-----   unit')
        if (ndx>0) then
          read(line(ndx+12:ndx+21),*) num
          !write(*,*) 'Reading unit ',num,'...'
          read(7,*)
          read(7,'(a)') desc
          read(7,*)
          if (num<maxunits) then
            do while (index(line, 'boundary')==0)
              read(7,'(a)') line
              if (index(line,'cylinder')>0.or.index(line,'cuboid')>0) then
                read(line,*) i
                read(7,*)
                read(7,*)
                read(7,*)
                z=0.0
                do while (z==0.0)
                  read(7,*) r,r,r,r,r,r,x,y,z
                  read(7,*)
                enddo
                cells(i)=z
              endif
            enddo
            read(line(31:),*) bound
            if (bound>maxcellshapes) then
              write(*,*) 'bound for unit',num, &
                                       'greater than maxcellshapes'
              stop
            endif
            call getloc(num,ai,aj,pi,pj,k,a)
            if (a>0) then
              celldz(a,k,pi,pj)=cells(bound)
               names(a,k,pi,pj)=desc
            endif
          endif
        endif
        read(7,'(a)') line
      enddo
!check consistency of axial levels and set problem heights
      do k=1,nax 
        xa=0
        do pj=1,npin
          do pi=1,npin
            do a=1,nasst
              if (types(a,pi,pj)==1) then
                if (celldz(a,k,pi,pj)>0.0) then
                  if (xa==0) then
                    xa=a
                    mm=pi
                    nn=pj
                  elseif (abs(celldz(a,k,pi,pj)-celldz(xa,k,mm,nn)) &
                                 > 0.0001) then
                    write(2,*) 'warning:  height of cell is off'
                    write(2,*) '  assembly',a     
                    write(2,*) '       rod',pi,pj
                    write(2,*) '     level',k
                    write(2,*) '   height = ',celldz(a,k,pi,pj), &
                        celldz(a,k,pi,pj) - celldz(xa,k,mm,nn)
                  endif 
                endif
              endif
            enddo
          enddo 
        enddo
        if (xa==0) then
          dz(k)=0.0
        else 
          dz(k)=celldz(xa,k,mm,nn)
        endif 
      enddo
      end subroutine
