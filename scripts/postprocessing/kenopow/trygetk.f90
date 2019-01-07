      subroutine trygetk(line)
      use global, only: keff, ksigma
      implicit none
      character(len=*), intent(in)  :: line
      character(len=26)             :: key
       
      key='best estimate system k-eff'
      
      if (keff /= 0.0) return
      if (index(line, key)==0) return

      read(line,'(79x,f9.6,8x,f9.6)') keff, ksigma
      end subroutine
