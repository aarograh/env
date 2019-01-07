      subroutine fuelunits
      use global
      implicit none
      integer :: num,i,j,maxa,maxp,mink,maxk,a,ai,aj,pi,pj,k,maxu
      real*8              :: vol,mul
      real*8 ,allocatable :: temp(:,:)
      integer,allocatable :: fuel(:)

      allocate(temp(maxunits,2))
      allocate(fuel(maxunits))

      fu(:,:)=0
      temp(:,:)=0.
      fuel(:)=0

!--- read fuelunits and get maximum dimentions
      
      maxa=0
      maxp=0
      mink=1000
      maxk=0
      maxu=0
      do
        read(9,*,end=11) num,vol,mul,ai,aj,pi,pj,k 
         
        if (num>maxunits) stop 'increase maxunits'
        if (ai>maxa) maxa=ai 
        if (aj>maxa) maxa=aj 
        if (pi>maxp) maxp=pi
        if (pj>maxp) maxp=pj 
        if ( k>maxk) maxk=k 
        if ( k<mink) mink=k 
        if (num>maxu) maxu=num
        fu(num,1)=ai
        fu(num,2)=aj
        fu(num,3)=pi
        fu(num,4)=pj
        fu(num,5)=k
        temp(num,1)=vol
        temp(num,2)=mul
        fuel(num)=1
      enddo

 11   nass=maxa
      npin=maxp
      kmax=maxk
      kmin=mink
      nax=kmax-kmin+1

!--- set core map and total number of assemblies

      allocate(assmap(nass,nass))
      assmap(:,:)=0
      nasst=0
      do i=1,maxu
        if (fuel(i)==1) then
          call getloc(i,ai,aj,pi,pj,k,a)
          if (assmap(ai,aj)==0) then
            nasst=nasst+1
            assmap(ai,aj)=nasst
          endif
        endif
      enddo

      !write(*,*) 'check assembly map'
      !do j=1,nass
      !  write(*,'(15(i3))') (assmap(i,j),i=1,nass)
      !enddo
      !write(*,*)

!--- put pin volumes, geometry factors, and types in arrays

      allocate(     vols(nasst,nax,npin,npin))
      allocate(     mult(nasst,nax,npin,npin))
      allocate(    types(nasst,npin,npin))
      allocate( minxpins(nasst))
      allocate( minypins(nasst))
      allocate( maxxpins(nasst))
      allocate( maxypins(nasst))

      vols(:,:,:,:)=0.0
      mult(:,:,:,:)=0.0
      types( :,:,:)=0
      minxpins(:)=100
      minypins(:)=100
      maxxpins(:)=0
      maxypins(:)=0

      do i=1,maxu
        if (fuel(i)==1) then
          call getloc(i,ai,aj,pi,pj,k,a)
          vols(a,k,pi,pj)=temp(i,1)    
          mult(a,k,pi,pj)=temp(i,2)    
          types(a,pi,pj)=1

          if (pi<minxpins(a)) minxpins(a)=pi
          if (pj<minypins(a)) minypins(a)=pj
          if (pi>maxxpins(a)) maxxpins(a)=pi
          if (pj>maxypins(a)) maxypins(a)=pj
        endif
      enddo

      deallocate(temp,fuel)
      end subroutine
