      module global
      implicit none
      logical             :: relative_error=.false. ! 

      integer             :: nsize,nsize2    ! number of assys across the core
      integer             :: npin,npin2      ! number of pins across an assembly
      integer             :: nassy, nassy2   ! number of assembly data in the results
      integer             :: nax,nax2        ! number of axial levels
      integer             :: isym,isym2      ! symmetry flag
      integer             :: version1, version2 ! version of HDF5 output structure
      integer,allocatable :: coremap(:,:)    ! layout of assemblies in core (file 1)
      integer,allocatable :: coremap2(:,:)   ! layout of assemblies in core (file 2)

      real*8              :: keff1,keff2        ! keff results for each file
      real*8              :: ksigma1,ksigma2    ! keff results for each file
      real*8              :: dk,dksigma         ! keff differences
      logical             :: isMC1,isMC2        ! flag for if uncertainties exist

      integer,allocatable :: pxlo(:),pxhi(:)    ! starting and ending pin indices for each assembly
      integer,allocatable :: pylo(:),pyhi(:)
      integer             :: axlo,axhi          ! starting and ending indices for core
      integer             :: aylo,ayhi

      real*8 ,allocatable :: wgt(:,:,:,:)
      real*8 ,allocatable :: axmesh(:)

      real*8 ,allocatable :: power1(:,:,:,:)    ! 3D pin power
      real*8 ,allocatable :: power2(:,:,:,:)    !
      real*8 ,allocatable :: sigma1(:,:,:,:)    ! 3D relative uncertainty (%)
      real*8 ,allocatable :: sigma2(:,:,:,:)    !
      real*8 ,allocatable :: absig1(:,:,:,:)    ! 3D absolute uncertainty
      real*8 ,allocatable :: absig2(:,:,:,:)    !
      real*8 ,allocatable ::  pdiff(:,:,:,:)    ! 3D power differences
      real*8 ,allocatable ::  sdiff(:,:,:,:)    ! uncertainty in 3D power differences
      real*8 ,allocatable :: sigmas(:,:,:,:)    ! number of sigmas in the difference 

      real*8 ,allocatable :: ffact1(:,:,:,:)    ! 3D pin power form factors
      real*8 ,allocatable :: ffact2(:,:,:,:)    ! 3D pin power form factors
      real*8 ,allocatable :: ffactdiff(:,:,:,:) ! 3D pin power form factors

      real*8 ,allocatable :: axpow1(:)          ! 1D axial power
      real*8 ,allocatable :: axpow2(:)          ! 
      real*8 ,allocatable :: axsig1(:)          ! 1D estimated uncertainty
      real*8 ,allocatable :: axsig2(:)          ! 
      real*8 ,allocatable :: axpsg1(:)          ! 1D avg pin uncertainty
      real*8 ,allocatable :: axpsg2(:)          ! 
      real*8 ,allocatable :: axpowdiff(:)       ! axial power differences
      real*8 ,allocatable :: axsigdiff(:)       ! 

      real*8              :: axial_offset1
      real*8              :: axial_offset2
 
      real*8 ,allocatable :: radpow1(:,:,:)     ! 2D radial pin powers
      real*8 ,allocatable :: radpow2(:,:,:)     ! 
      real*8 ,allocatable :: radsig1(:,:,:)     ! 2D estimated uncertainty
      real*8 ,allocatable :: radsig2(:,:,:)     ! 
      real*8 ,allocatable :: radpsg1(:,:,:)     ! 2D avg pin uncertainty
      real*8 ,allocatable :: radpsg2(:,:,:)     ! 
      real*8 ,allocatable :: radpowdiff(:,:,:)  ! axial power differences
      real*8 ,allocatable :: radsigdiff(:,:,:)  ! 
      real*8 ,allocatable :: radwgt(:,:,:)
 
      real*8 ,allocatable :: asspow1(:,:)       ! 3D assembly powers
      real*8 ,allocatable :: asspow2(:,:)       ! 
      real*8 ,allocatable :: asssig1(:,:)       ! 3D estimated uncertainty in assembly powers
      real*8 ,allocatable :: asssig2(:,:)       ! 
      real*8 ,allocatable :: asspsg1(:,:)       ! 3D avg pin uncertainty
      real*8 ,allocatable :: asspsg2(:,:)       ! 
      real*8 ,allocatable :: asspowdiff(:,:)    ! 3D assembly power differences
      real*8 ,allocatable :: asssigdiff(:,:)    ! 3D assembly power differences
      real*8 ,allocatable :: asswgt(:,:)
 
      real*8 ,allocatable :: ardpow1(:)         ! 2D assembly powers
      real*8 ,allocatable :: ardpow2(:)         ! 
      real*8 ,allocatable :: ardsig1(:)         ! 2D estimated uncertainty in assembly powers
      real*8 ,allocatable :: ardsig2(:)         ! 
      real*8 ,allocatable :: ardpsg1(:)         ! 2D avg pin uncertainty
      real*8 ,allocatable :: ardpsg2(:)         ! 
      real*8 ,allocatable :: ardpowdiff(:)      ! 3D assembly power differences
      real*8 ,allocatable :: ardsigdiff(:)      ! 3D assembly power differences
      real*8 ,allocatable :: ardwgt(:)
      end module
