      module global
      implicit none
      integer,parameter    :: maxcellshapes=200              ! maximum number of shapes in each keno unit
      logical              :: octant_symmetry=.true.        ! option to use octant symmetry
      integer              :: maxunits=5000                 ! maximum number of units in the model

      integer              :: nass                          ! number of assemblies across the core geometry (wrt symmetry)
      integer              :: nasst                         ! total number of assemblies 
      integer              :: npin                          ! number of pins across an assembly
      integer              :: kmin                          ! lowest axial level     
      integer              :: kmax                          ! highest axial level   
      integer              :: nax                           ! total number of axial levels   
      integer,allocatable  :: fu(:,:)                       ! core positions of each unit (from file)

      integer              :: core_size                     ! number of assembies across the full core
      integer              :: core_sym                      ! core symmetry flag
      integer,allocatable  :: core_map(:,:)                 ! assembly identifiers in full geometry

      real*8,allocatable             ::   vols(:,:,:,:)     ! volume in each cell        
      real*8,allocatable             ::   mult(:,:,:,:)     ! geomtry multiplier for each cell
      real*8,allocatable             ::  fissn(:,:,:,:)     ! fission rate in each cell
      real*8,allocatable             ::  power(:,:,:,:)     ! normalized power in each cell
      real*8,allocatable             ::  sigma(:,:,:,:)     ! reaction rate uncertainty in each cell
      real*8,allocatable             :: celldz(:,:,:,:)     ! keno unit heights
      integer,allocatable            ::  types(:,:,:)       ! indicator if radial location is a fuel rod
      character(len=80) ,allocatable ::  names(:,:,:,:)     ! name of each keno cell
      
      real*8,allocatable   :: dz(:)                         ! the axial height of each axial level     
      real*8,allocatable   :: axmids(:)                     ! the midpoint of each axial level
      real*8,allocatable   :: axmesh(:)                     ! the axial mesh boundaries
      real*8               :: keff                          ! keno eigenvalue
      real*8               :: ksigma                        ! eiganvalue uncertainty
      real*8               :: avgpow                        ! average pin power 
      real*8               :: avgsig                        ! average power distribution uncertainty
      real*8               :: totalvol                      ! sum of fuel volumes  
      integer,allocatable  :: assmap(:,:)                   ! assembly identifiers in KENO geometry
      integer,allocatable  :: asssym(:)                     ! assembly symmetry in KENO geometry

      real*8,allocatable   :: axials(:)                     ! total axial power distribution
      real*8,allocatable   :: axsigs(:)                     ! total axial uncertainties
      real*8,allocatable   :: axsigs2(:)                    ! total axial pin ncertainties
      real*8,allocatable   :: asspow(:,:)                   ! assembly axial power distributions
      real*8,allocatable   :: asssig(:,:)                   ! assembly axial uncertainties           
      real*8,allocatable   :: asssig2(:,:)                  ! assembly axial pin uncertainties           
      real*8,allocatable   :: radials(:,:,:)                ! pin radial power distribution
      real*8,allocatable   :: radsigs(:,:,:)                ! pin radial uncertainties       
      real*8,allocatable   :: radsigs2(:,:,:)               ! pin radial pin ncertainties       
      real*8,allocatable   :: assrad(:)                     ! assembly radial power distributions
      real*8,allocatable   :: assrsg(:)                     ! assembly radial uncertainties           
      real*8,allocatable   :: assrsg2(:)                    ! assembly radial pin uncertainties           
      real*8,allocatable   :: nodpow(:,:,:)                 ! nodal powers distribution
      real*8,allocatable   :: nodsig(:,:,:)                 ! nodal powers uncertainty  

      integer,allocatable  :: minxpins(:)
      integer,allocatable  :: minypins(:)
      integer,allocatable  :: maxxpins(:)
      integer,allocatable  :: maxypins(:)

      real                 :: avgoctdiff                    ! average power difference between octant pairs
      real                 :: sigoctdiff                    ! standard deviation of difference between octant pairs
      real                 :: maxoctdiff                    ! maximum difference between octant pairs
      real                 :: maxoctpow(2)                  ! powers of maximum difference between octant pairs
      real                 :: maxoctsig(2)                  ! sigmas of maximum difference between octant pairs
      real                 :: axial_offset                  ! the calculated axial offset for the problem
      end module
