!----------------------------------------------------
!  Converts the unit number to an array position    !
!----------------------------------------------------
      subroutine getloc(num,ai,aj,pi,pj,k,a)
      use global, only: fu, assmap, kmin
      implicit none
      integer, intent(in)   :: num       ! unit number
      integer, intent(out)  :: ai 
      integer, intent(out)  :: aj
      integer, intent(out)  :: pi 
      integer, intent(out)  :: pj
      integer, intent(out)  :: k ! k index in axial array
      integer, intent(out)  :: a ! assembly number
      ai=fu(num,1)
      aj=fu(num,2)
      pi=fu(num,3)
      pj=fu(num,4)
       k=fu(num,5)
      if (k>0) then
        k=k-kmin+1     !convert k to 1 based index instead of actual model levels
      endif
      if (ai==0) then
        a=0
      else
        a=assmap(ai,aj)
      endif
      endsubroutine
