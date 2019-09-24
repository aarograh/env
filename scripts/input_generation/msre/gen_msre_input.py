import sys
import numpy as np
import copy

helpstring=\
"""
  You done messed up!
                -- A-A-ron

  """

nargs = len(sys.argv)
if nargs > 1:
  print helpstring
  exit(1)

class geomClass(object):
  _id = 0
  _nextID = 0
  _list = None
  _height = 0.0

class pinmeshClass(geomClass):
  _nRegions = 0

  def __init__(self):
    self._id = pinmeshClass.getNextID()
    self._height = assembly_height

    if not pinmeshClass._list:
      pinmeshClass._list = []
    pinmeshClass._list.append(self)

  @staticmethod
  def getNextID():
    pinmeshClass._nextID += 1
    return pinmeshClass._nextID

  @staticmethod
  def editAll():
    [pinmesh.edit() for pinmesh in pinmeshClass._list]
    print

class pinmeshClass_cyl(pinmeshClass):
  _radii = []
  _submesh_r = []
  _submesh_azi = []
  _pitch = 0.0

  def __init__(self,radii,subr,subazi,pitch):
    super(pinmeshClass_cyl, self).__init__()
    self._radii = radii[:]
    self._submesh_r = subr[:]
    self._submesh_azi = subazi[:]
    self._pitch = pitch
    self._nRegions = len(self._radii)+1

  def getX(self):
    return self._pitch

  def getY(self):
    return self._pitch

  def getRegionCentroid(self, region):
    return [1000000000.0, 100000000.0]

  def edit(self):
    print '  pinmesh ' + format(self._id,'2d')

class pinmeshClass_qcyl(pinmeshClass_cyl):
  _quadrant = 0

  def __init__(self,radii,subr,subazi,pitch,quad):
    assert(quad > 0 and quad < 5)
    super(pinmeshClass_qcyl, self).__init__(radii,subr,subazi,pitch)
    self._quadrant = quad

  def getRegionCentroid(self, region):
    if region > len(self._radii):
      centroid = [0.5*(self._pitch + self._radii[-1]), 0.5*(self._pitch + self._radii[-1])]
    elif region == 1:
      centroid = [0.5*self._radii[0], 0.5*self._radii[0]]
    else:
      centroid = [0.5*sum(self._radii[region-1:region+1]), 0.5*sum(self._radii[region-1:region+1])]

    if self._quadrant == 2 or self._quadrant == 3:
      centroid[0] = self._pitch - centroid[0]
    if self._quadrant == 3 or self._quadrant == 4:
      centroid[1] = self._pitch - centroid[1]

    if ldebug:
      print 'centroid', region, self._id, self._quadrant, self._radii, self._pitch, centroid
    return centroid

  def edit(self):
    if self._quadrant == 1:
      lengths = [0.0, self._pitch, 0.0, self._pitch]
    elif self._quadrant == 2:
      lengths = [-self._pitch, 0.0, 0.0, self._pitch]
    elif self._quadrant == 3:
      lengths = [-self._pitch, 0.0, -self._pitch, 0.0]
    elif self._quadrant == 4:
      lengths = [0.0, self._pitch, -self._pitch, 0.0]
    print '  pinmesh ' + format(self._id,'2d') + ' gcyl ' + \
        ' '.join(format(radius,float_edit_format) for radius in self._radii) + ' / ' + \
        ' '.join(format(length,float_edit_format) for length in lengths) + ' / ' + \
        format(self._height,float_edit_format) + ' / ' + \
        ' '.join(str(subr) for subr in self._submesh_r) + ' / ' + \
        ' '.join(str(subazi) for subazi in self._submesh_azi) + ' / 1'

class pinmeshClass_rect(pinmeshClass):
  _nx = 0
  _ny = 0
  _x = []
  _y = []
  _submesh_x = []
  _submesh_y = []

  def __init__(self,x,y,subx,suby):
    super(pinmeshClass_rect, self).__init__()
    self._x = x[:]
    self._y = y[:]
    self._nx = len(x)
    self._ny = len(y)
    self._submesh_x = subx[:]
    self._submesh_y = suby[:]
    self._nRegions = len(x)*len(y)

  def getX(self):
    return self._x[-1]

  def getY(self):
    return self._y[-1]

  def getRegionCentroid(self, region):
    ix = np.mod(region-1,self._nx)
    iy = self._ny - int(region-1)/int(self._nx) - 1
    if ix == 0:
      x = 0.0
    else:
      x = self._x[ix-1]
    x = 0.5*(x + self._x[ix])
    if iy == 0:
      y = 0.0
    else:
      y = self._y[iy-1]
    y = 0.5*(y + self._y[iy])

    return [x, y]

  def edit(self):
    print '  pinmesh ' + format(self._id,'2d') + ' rec ' + \
        ' '.join(format(x,float_edit_format) for x in self._x) + ' / ' + \
        ' '.join(format(y,float_edit_format) for y in self._y) + ' / ' + \
        format(self._height,float_edit_format) + ' / ' + \
        ' '.join(str(subx) for subx in self._submesh_x) + ' / ' + \
        ' '.join(str(suby) for suby in self._submesh_y) + ' / 1'

class pinClass(geomClass):
  _pinmesh = None
  _materials = []

  def __init__(self, pinmesh=None, materials=None, source=None):
    if pinmesh and materials:
      self._pinmesh = pinmesh
      self._materials = materials[:]
      self._height = assembly_height
      pinClass.addPin(self)
    elif source:
      self._id = copy.deepcopy(source._id)
      self._pinmesh = source._pinmesh
      self._materials = copy.deepcopy(source._materials)
      self._height = copy.deepcopy(source._height)

  def __eq__(self, other):
    if isinstance(other, pinClass):
      if self._pinmesh._id == other._pinmesh._id and \
          self._materials[:] == other._materials[:]:
        return True
      else:
        return False
    else:
      False

  @staticmethod
  def getNextID():
    pinClass._nextID += 1
    return pinClass._nextID

  @staticmethod
  def addPin(pin):
    if not pinClass._list:
      pinClass._list = []
    pin_is_new = True
    for oldpin in pinClass._list:
      if pin == oldpin:
        pin_is_new = False
        del pin
        pin = oldpin

    if pin_is_new:
      pin._id = pinClass.getNextID()
      pinClass._list.append(pin)
    return pin

  def getPinMesh(self):
    return self._pinmesh

  def getMaterials(self):
    return self._materials

  def getX(self):
    return self._pinmesh.getX()

  def getY(self):
    return self._pinmesh.getY()

  def getCorners(self, offset=[0.0, 0.0]):
    corners = []
    corners.append(copy.deepcopy(offset))
    corners.append([offset[0] + self.getX(), offset[1]])
    corners.append([offset[0], offset[1] + self.getY()])
    corners.append([offset[0] + self.getX(), offset[1] + self.getY()])
    return corners

  def replaceMaterials(self, radius, material, origin, outerRadius=10000000000.0):
    clone = pinClass(source=self)
    for region in range(self._pinmesh._nRegions):
      centroid = self._pinmesh.getRegionCentroid(region+1)
      centroid[0] += origin[0]
      centroid[1] += origin[1]
      if ldebug:
        print 'pin:', region, origin, centroid, ':', radius, outerRadius, pointsInCircle([centroid], outerRadius), pointsInCircle([centroid], radius)
      if pointsInCircle([centroid], outerRadius)[0] and not pointsInCircle([centroid], radius)[0]:
        if ldebug:
          print 'Changing region material from ', clone._materials[region], ' to ', material
        clone._materials[region] = copy.deepcopy(material)

    if clone == self:
      del clone
      return self
    else:
      if ldebug:
        print 'Adding new pin'
      return pinClass.addPin(clone)

  @staticmethod
  def editAll():
    [pin.edit() for pin in pinClass._list]
    print

  def edit(self):
    print '  pin ' + format(self._id,'4d') + ' ' + format(self._pinmesh._id) + ' / ' + \
        ' '.join(str(material) for material in self._materials)

class latticeClass(geomClass):
  _nextID = 0
  _pins = []
  _nx = 0
  _ny = 0
  _delx = []
  _dely = []

  def __init__(self, nx=None, ny=None, source=None):
    if nx and ny:
      self._nx = nx
      self._ny = ny
      for j in range(ny):
        self._pins.append([])
        for i in range(nx):
          self._pins[j].append(None)
      self._height = assembly_height
      latticeClass.addLattice(self)
    elif source:
      self._id = copy.deepcopy(source._id)
      self._pins = copy.deepcopy(source._pins)
      self._nx = copy.deepcopy(source._nx)
      self._ny = copy.deepcopy(source._ny)
      self._delx = copy.deepcopy(source._delx)
      self._dely = copy.deepcopy(source._dely)
      self._height = copy.deepcopy(source._height)

  def __eq__(self, other):
    if isinstance(other, latticeClass):
      if self._pins[:] == other._pins[:] and self._nx == other._nx and self._ny == other._ny and \
          self._delx[:] == other._delx[:] and self._dely[:] == other._dely[:]:
        return True
      else:
        return False
    else:
      return False

  @staticmethod
  def getNextID():
    latticeClass._nextID += 1
    return latticeClass._nextID

  @staticmethod
  def addLattice(lattice):
    if not latticeClass._list:
      latticeClass._list = []
    lattice_is_new = True
    for oldlattice in latticeClass._list:
      if lattice == oldlattice:
        lattice_is_new = False
        del lattice
        lattice = oldlattice

    if lattice_is_new:
      lattice._id = latticeClass.getNextID()
      latticeClass._list.append(lattice)
    return lattice

  def setPin(self,ix,iy,pin):
    self._pins[iy-1][ix-1] = pin

  def getPin(self,ix,iy):
    return self._pins[iy-1][ix-1]

  def getNX(self):
    return self._nx

  def getNY(self):
    return self._ny

  def getX(self):
    return sum(self._delx)

  def getY(self):
    return sum(self._dely)

  def getCorners(self, offset=[0.0, 0.0]):
    corners = []
    corners.append(copy.deepcopy(offset))
    corners.append([offset[0] + self.getX(), offset[1]])
    corners.append([offset[0], offset[1] + self.getY()])
    corners.append([offset[0] + self.getX(), offset[1] + self.getY()])
    return corners

  def update(self):
    self._delx = []
    for i in range(self._nx):
      pin = self.getPin(i+1,1)
      self._delx.append(pin.getX())
    self._dely = []
    for i in range(self._ny):
      pin = self.getPin(1,i+1)
      self._dely.append(pin.getY())

  def replaceMaterials(self, radius, material, origin, outerRadius=10000000000.0):
    clone = latticeClass(source=self)
    ystart = origin[1] + self.getY()
    for iy in reversed(range(self._ny)):
      ystart -= self._dely[iy]
      xstart = origin[0]
      for ix in range(self._nx):
        pin = self.getPin(ix+1,self._ny-iy)
        corners = pin.getCorners([xstart, ystart])
        if ldebug:
          if origin[1] > 71.0:
            print 'lattice:', iy, ix, ystart, xstart, ':', radius, outerRadius, ':', \
                pointsInCircle(corners, outerRadius), ':', pointsInCircle(corners, radius), ':', corners
        if not any(pointsInCircle(corners, outerRadius)) or all(pointsInCircle(corners, radius)):
          newpin = pin
        else:
          newpin = pin.replaceMaterials(radius, material, [xstart, ystart], outerRadius)
        clone.setPin(ix+1,self._ny-iy,newpin)
        xstart += self._delx[ix]
        if ldebug:
          print

    if clone == self:
      del clone
      return self
    else:
      return latticeClass.addLattice(clone)

  @staticmethod
  def editAll():
    [lattice.editModule() for lattice in latticeClass._list]
    print
    [lattice.editLattice() for lattice in latticeClass._list]
    print

  def editModule(self):
    print '  module ' + format(self._id,'3d') + ' ' + str(self._nx) + ' ' + str(self._ny) + ' 1'
    print '    ' + '\n    '.join(' '.join(format(pin._id,'4d') for pin in row) for row in self._pins)

  def editLattice(self):
    print '  lattice ' + format(self._id,'3d') + ' 1 1'
    print '    ' + format(self._id,'3d')

class assemblyClass(geomClass):
  _nextID = 0
  _lattices = None
  _nz = 0

  def __init__(self, source=None):
    if source:
      self._id = copy.deepcopy(source._id)
      self._lattices = copy.deepcopy(source._lattices)
      self._nz = copy.deepcopy(source._nz)
      self._height = copy.deepcopy(source._height)
    else:
      self._height = assembly_height
      assemblyClass.addAssembly(self)

  def __eq__(self, other):
    if isinstance(other, assemblyClass):
      if self._lattices != other._lattices:
        return False
      if self._lattices[:] == other._lattices[:] and self._nz == other._nz:
        return True
      else:
        return False
    else:
      return False

  @staticmethod
  def getNextID():
    assemblyClass._nextID += 1
    return assemblyClass._nextID

  @staticmethod
  def addAssembly(assembly):
    if not assemblyClass._list:
      assemblyClass._list = []
    assembly_is_new = True
    for oldassembly in assemblyClass._list:
      if assembly == oldassembly:
        assembly_is_new = False
        del assembly
        assembly = oldassembly

    if assembly_is_new:
      assembly._id = assemblyClass.getNextID()
      assemblyClass._list.append(assembly)
    return assembly

  def setLattice(self,iz,lattice):
    self._lattices[iz-1] = lattice

  def getLattice(self,iz):
    return self._lattices[iz-1]

  def addTopLattice(self,lattice):
    if self._lattices:
      self._lattices.append(lattice)
    else:
      self._lattices = [lattice]
    self._nz += 1

  def addBottomLattice(self,lattice):
    if self._lattices:
      self._lattices.insert(0, lattice)
    else:
      self._lattices = [lattice]
    self._nz += 1

  def getX(self):
    return self._lattices[0].getX()

  def getY(self):
    return self._lattices[0].getY()

  def replaceMaterials(self, radius, material, origin, outerRadius=100000000000.0):
    clone = assemblyClass(source=self)
    for iz in range(self._nz):
      lattice = self.getLattice(iz+1)
      corners = lattice.getCorners(origin)
      if ldebug:
        print 'assembly:', iz, origin, corners, ':', radius, outerRadius, ':', lattice
      if not any(pointsInCircle(corners, outerRadius)) or all(pointsInCircle(corners, radius)):
        newlattice = lattice
      else:
        newlattice = lattice.replaceMaterials(radius, material, origin, outerRadius)
      if ldebug:
        print iz, newlattice
      clone.setLattice(iz,newlattice)
    if ldebug:
      print

    if clone == self:
      del clone
      return self
    else:
      return assemblyClass.addAssembly(clone)

  @staticmethod
  def editAll():
    [assembly.edit() for assembly in assemblyClass._list]
    print

  def edit(self):
    print '  assembly ' + format(self._id,'3d')
    print '    ' + ' '.join(format(lattice._id,'4d') for lattice in self._lattices)

class coreClass:
  _assemblies = []
  _nx = 0
  _ny = 0
  _delx = []
  _dely = []
  _offset = []

  def __init__(self,nx,ny):
    self._nx = nx
    self._ny = ny
    for j in range(ny):
      self._assemblies.append([])
      for i in range(nx):
        self._assemblies[j].append(None)

  def setAssembly(self,ix,iy,assembly):
    self._assemblies[iy-1][ix-1] = assembly

  def getAssembly(self,ix,iy):
    return self._assemblies[iy-1][ix-1]

  def getAssemblyCorners(self,ix,iy):
    corners = []
    for (x, y) in zip([ix-1, ix, ix-1, ix], [iy-1, iy-1, iy, iy]):
      corners.append([sum(self._delx[0:x])-self._offset[0], sum(self._dely[0:y])-self._offset[1]])
    return corners

  def update(self):
    self._delx = []
    for i in range(self._nx):
      assembly = self.getAssembly(i+1,1)
      self._delx.append(assembly.getX())
    self._dely = []
    for i in range(self._ny):
      assembly = self.getAssembly(1,i+1)
      self._dely.append(assembly.getY())
    self._offset = [sum(self._delx)/2.0, sum(self._dely)/2.0]

  def makeJagged(self, radius):
    ystart = -self._offset[1]
    for iy in reversed(range(self._ny)):
      xstart = -self._offset[0]
      for ix in range(self._nx):
        assembly = self.getAssembly(ix+1,iy+1)
        corners = assembly.getLattice(1).getCorners([xstart, ystart])
        if not any(pointsInCircle(corners, radius)):
          self.setAssembly(ix+1,iy+1,None)
        xstart += self._delx[ix]
      ystart += self._dely[iy]

  def replaceMaterials(self, radius, material, outerRadius=1000000000.0):
    ystart = -self._offset[1]
    for iy in reversed(range(self._ny)):
      xstart = -self._offset[0]
      for ix in range(self._nx):
        assembly = self.getAssembly(ix+1,iy+1)
        if assembly:
          corners = assembly.getLattice(1).getCorners([xstart, ystart])
          if ldebug:
            if iy == 0:
              print 'core:', iy, ix, ystart, xstart, ':', radius, outerRadius
          if not any(pointsInCircle(corners, outerRadius)) or all(pointsInCircle(corners, radius)):
              newAssembly = assembly
          else:
            newAssembly = assembly.replaceMaterials(radius, material, [xstart, ystart], outerRadius)
          if ldebug:
            print iy, ix, newAssembly
          self.setAssembly(ix+1,iy+1,newAssembly)
        xstart += self._delx[ix]
        if ldebug:
          print
      ystart += self._dely[iy]

  def edit(self, onlyCore=False):
    if not onlyCore:
      # print the lattice dimensions
      assembly = None
      for iy in range(self._ny):
        for ix in range(self._nx):
          assembly = self.getAssembly(ix+1,iy+1)
          if assembly:
            break
        if assembly:
          break
      print '  mod_dim ' + ' '.join(format(value,float_edit_format) for value in [assembly.getX(), assembly.getY(), assembly_height])
      print

      # Print the pin meshes
      pinmeshClass.editAll()

      # Print the pins
      pinClass.editAll()

      # Print the modules and lattices
      latticeClass.editAll()

      # Print the assemblies
      assemblyClass.editAll()

    # Print the core
    print "  core 360"
    for j in range(self._ny):
      print '    ' + ' '.join(format(assembly._id,'3d') if assembly else '   ' for assembly in self._assemblies[j])

def buildGraphiteStringer():
  newLattice = latticeClass(pins_per_lattice, pins_per_lattice)

  # Useful values
  cell_length_long = channel_length - 2*channel_radius
  cell_length_short = (block_pitch - cell_length_long)/(pins_per_lattice - 1)
  nsub_short = 3 # Needs to be a multiple of 3 for radii to line up
  nsub_long = 2*nsub_short

  # Set the small graphite square pins - 4 corners and 4 diagonal locations (excluding center)
  newPinMesh = pinmeshClass_rect([cell_length_short*(i+1)/nsub_short for i in range(nsub_short)], \
      [cell_length_short*(i+1)/nsub_short for i in range(nsub_short)], [1 for i in range(nsub_short)], \
      [1 for i in range(nsub_short)])
  newPin = pinClass(newPinMesh, [materials['Graphite'] for i in range(nsub_short*nsub_short)])
  for (ix, iy) in zip([1, 2, 4, 5, 1, 2, 4, 5], [1, 2, 2, 1, 5, 4, 4, 5]):
    newLattice.setPin(ix,iy,newPin)

  # Set the center pin cell
  newPinMesh = pinmeshClass_rect([cell_length_long*(i+1)/nsub_long for i in range(nsub_long)], \
      [cell_length_long*(i+1)/nsub_long for i in range(nsub_long)], [1 for i in range(nsub_long)], \
      [1 for i in range(nsub_long)])
  newPin = pinClass(newPinMesh, [materials['Graphite'] for i in range(nsub_long*nsub_long)])
  newLattice.setPin(3,3,newPin)

  # Set the E/W rectangular graphite pieces
  newPinMesh = pinmeshClass_rect([cell_length_short*(i+1)/nsub_short for i in range(nsub_short)], \
      [cell_length_long*(i+1)/nsub_long for i in range(nsub_long)], [1 for i in range(nsub_short)], \
      [1 for i in range(nsub_long)])
  newPin = pinClass(newPinMesh, [materials['Graphite'] for i in range(nsub_short*nsub_long)])
  newLattice.setPin(2,3,newPin)
  newLattice.setPin(4,3,newPin)

  # Set the W/E fuel channel sides
  newPin = pinClass(newPinMesh, [materials[key] for key in ['Fuel Salt','Fuel Salt','Graphite', \
      'Fuel Salt','Fuel Salt','Graphite','Fuel Salt','Fuel Salt','Graphite','Fuel Salt','Fuel Salt', \
      'Graphite','Fuel Salt','Fuel Salt','Graphite','Fuel Salt','Fuel Salt','Graphite']])
  newLattice.setPin(1,3,newPin)
  newPin = pinClass(newPinMesh, [materials[key] for key in ['Graphite','Fuel Salt','Fuel Salt', \
      'Graphite','Fuel Salt','Fuel Salt','Graphite','Fuel Salt','Fuel Salt','Graphite','Fuel Salt', \
      'Fuel Salt','Graphite','Fuel Salt','Fuel Salt','Graphite','Fuel Salt','Fuel Salt']])
  newLattice.setPin(5,3,newPin)

  # Set the N/S rectangular graphite pieces
  newPinMesh = pinmeshClass_rect([cell_length_long*(i+1)/nsub_long for i in range(nsub_long)], \
      [cell_length_short*(i+1)/nsub_short for i in range(nsub_short)], [1 for i in range(nsub_long)], \
      [1 for i in range(nsub_short)])
  newPin = pinClass(newPinMesh, [materials['Graphite'] for i in range(nsub_long*nsub_short)])
  newLattice.setPin(3,2,newPin)
  newLattice.setPin(3,4,newPin)

  # Set the N/S fuel channel sides
  newPin = pinClass(newPinMesh, [materials[key] for key in ['Fuel Salt','Fuel Salt','Fuel Salt', \
      'Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt', \
      'Fuel Salt','Graphite','Graphite','Graphite','Graphite','Graphite','Graphite']])
  newLattice.setPin(3,1,newPin)
  newPin = pinClass(newPinMesh, [materials[key] for key in ['Graphite','Graphite','Graphite','Graphite', \
      'Graphite','Graphite','Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt', \
      'Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt']])
  newLattice.setPin(3,5,newPin)

  # Set the NE quarter pins
  newPinMesh = pinmeshClass_qcyl([cell_length_short*(i+1)/nsub_short for i in range(nsub_short-1)], \
      [1 for i in range(nsub_short-1)], [1 for i in range(nsub_short)], cell_length_short, 1)
  newPin = pinClass(newPinMesh, [materials[key] for key in ['Fuel Salt','Fuel Salt','Graphite']])
  newLattice.setPin(1,2,newPin)
  newLattice.setPin(4,5,newPin)

  # Set the NW quarter pins
  newPinMesh = pinmeshClass_qcyl([cell_length_short*(i+1)/nsub_short for i in range(nsub_short-1)], \
      [1 for i in range(nsub_short-1)], [1 for i in range(nsub_short)], cell_length_short, 2)
  newPin = pinClass(newPinMesh, [materials[key] for key in ['Fuel Salt','Fuel Salt','Graphite']])
  newLattice.setPin(5,2,newPin)
  newLattice.setPin(2,5,newPin)

  # Set the SW quarter pins
  newPinMesh = pinmeshClass_qcyl([cell_length_short*(i+1)/nsub_short for i in range(nsub_short-1)], \
      [1 for i in range(nsub_short-1)], [1 for i in range(nsub_short)], cell_length_short, 3)
  newPin = pinClass(newPinMesh, [materials[key] for key in ['Fuel Salt','Fuel Salt','Graphite']])
  newLattice.setPin(2,1,newPin)
  newLattice.setPin(5,4,newPin)

  # Set the SE quarter pins
  newPinMesh = pinmeshClass_qcyl([cell_length_short*(i+1)/nsub_short for i in range(nsub_short-1)], \
      [1 for i in range(nsub_short-1)], [1 for i in range(nsub_short)], cell_length_short, 4)
  newPin = pinClass(newPinMesh, [materials[key] for key in ['Fuel Salt','Fuel Salt','Graphite']])
  newLattice.setPin(4,1,newPin)
  newLattice.setPin(1,4,newPin)

  newLattice.update()

  return newLattice

def fillBlock(stringer):
  newLattice = latticeClass(source=stringer)

  # Copy non-fuel pins
  for (ix,iy) in zip([1,5,2,3,4,2,3,4,2,3,4,1,5],[1,1,2,2,2,3,3,3,4,4,4,5,5]):
    newLattice.setPin(ix,iy,stringer.getPin(ix,iy))

  # Now copy graphite pins from non-fuel locations to fuel locations
  for (ix1,iy1,ix2,iy2) in zip([3,1,5,3,2,4,1,5,1,5,2,4],[1,3,3,5,1,1,2,2,4,4,5,5],\
      [3,2,4,3,1,1,1,1,1,1,1,1],[2,3,3,4,1,1,1,1,1,1,1,1]):
    newLattice.setPin(ix1,iy1,stringer.getPin(ix2,iy2))

  newLattice.update()
  newLattice = latticeClass.addLattice(newLattice)
  newLattice = newLattice.replaceMaterials(0.0, materials['Cell Gas'], [0.0, 0.0])

  return newLattice

def pointsInCircle(points, radius, origin=[0.0, 0.0]):
  inside = []
  for coordinates in points:
    inside.append((coordinates[0]+origin[0])**2.0 + (coordinates[1]+origin[1])**2.0 <= radius**2.0)
  return inside

# Core Parameters
material_names = ['Fuel Salt', 'INOR-8', 'Graphite', 'Cell Gas', 'Helium Gas', 'Stainlesss Steel', 'Inconel', \
    'Control Rod Poison', 'Insulation', 'Thermal Shield', 'Homogenized Sample Basket']
materials = {key: id for (key, id) in zip(material_names, [1,2,3,4,5,6,7,8,9,10,11])}
reflector_radii = [70.168, 70.485, 71.12, 73.66, 76.2]#, 102.87, 118.11, 120.65, 156.21, 158.75]
reflector_materials = ['Fuel Salt', 'INOR-8', 'Fuel Salt', 'INOR-8', 'Cell Gas', 'Insulation', \
  'Stainlesss Steel', 'Thermal Shield', 'Stainlesss Steel']
reflector_names = ['Graphite Core', 'Core Can Inner Radius', 'Core Can Outer Radius', 'Vessel Inner Radius', \
    'Vessel Outer Radius', 'Insulation Inner Radius', 'Insulation Outer Radius', 'Thermal Shield Inner Radius', \
    'Thermal Shield Outer Radius', 'Model Outer Radius']

# Edit controls
float_edit_format = '9.6f'

# Fuel block parameters
block_pitch = 5.08 #5.07492
channel_length = 3.048
channel_width = 0.508
channel_radius = 0.508
pins_per_lattice = 5
assembly_height = 10.16

# Sample Basket parameters

# Control parameters

ldebug = False
# Calculate how many lattices we need in the core
assemblies_across_core = int(np.ceil(max(reflector_radii)/block_pitch))*2
core = coreClass(assemblies_across_core, assemblies_across_core)

# Build the basic lattices: graphite stringer, solid graphite block
graphiteStringerAssembly = assemblyClass()
graphiteStringerAssembly.addTopLattice(buildGraphiteStringer())

fillAssembly = assemblyClass()
fillAssembly.addTopLattice(fillBlock(graphiteStringerAssembly.getLattice(0)))

# Set all core lattices to the graphite stringer
for iy in range(core._ny):
  for ix in range(core._nx):
    core.setAssembly(ix+1,iy+1,graphiteStringerAssembly)

core.update()

# Now set all the lattices outside the graphite lattice radius
for iy in reversed(range(core._ny)):
  for ix in reversed(range(core._nx)):
    allOutside = True
    for inside in pointsInCircle(core.getAssemblyCorners(ix+1,iy+1), reflector_radii[0]):
      allOutside = allOutside and not inside
    if allOutside:
      core.setAssembly(ix+1,iy+1,fillAssembly)

core.makeJagged(reflector_radii[-1])

for zone in xrange(0,len(reflector_radii)-1):
  radius = reflector_radii[zone]
  material = reflector_materials[zone]
  region = reflector_names[zone]
  if zone == len(reflector_radii)-1:
    core.replaceMaterials(radius, materials[material])
  else:
    core.replaceMaterials(radius, materials[material], reflector_radii[zone+1])

# Extrude the core to the full fuel height

if not ldebug:
  core.edit()
else:
  core.edit(False)