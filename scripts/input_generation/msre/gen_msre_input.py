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

  def __init__(self, height=None, source=None):
    if source:
      self._height = source._height
    elif height:
      if height <= 0.0:
        raise ValueError
      self._height = height

  @staticmethod
  def testCreation(new, ref):
    if new is ref:
      return new
    else:
      del new
      return ref

  @classmethod
  def addObject(cls, newObject):
    class_list = cls.getList()
    object_is_new = True
    for oldObject in class_list:
      if newObject == oldObject:
        return oldObject

    newObject._id = cls.getNextID()
    class_list.append(newObject)
    return newObject

class pinmeshClass(geomClass):
  _nRegions = 0

  def __init__(self, height=None, source=None):
    if source:
      self._nRegions = source._nRegions
    super(pinmeshClass, self).__init__(height=height, source=source)

  def __eq__(self, other):
    if isinstance(other, pinmeshClass):
      if self._nRegions == other._nRegions and self._height == other._height:
        return True
      else:
        return False
    else:
      return False

  @staticmethod
  def getNextID():
    pinmeshClass._nextID += 1
    return pinmeshClass._nextID

  @classmethod
  def getList(cls):
    if not pinmeshClass._list:
      pinmeshClass._list = []
    return pinmeshClass._list

  @staticmethod
  def removePinMesh(id):
    for ipinmesh in range(len(pinmeshClass._list)):
      pinmesh = pinmeshClass._list[ipinmesh]
      if pinmesh._id == id:
        pinmesh = pinmeshClass._list.pop(ipinmesh)
        del pinmesh
        return

  def extrude(self, height):
    if height == self._height:
      return self

    newPinMesh = self.clonePinMesh(self)
    newPinMesh._height = height
    return pinmeshClass.addObject(newPinMesh)

  @staticmethod
  def editAll():
    [pinmesh.edit() for pinmesh in pinmeshClass._list]
    print

class pinmeshClass_cyl(pinmeshClass):
  _radii = []
  _submesh_r = []
  _submesh_azi = []
  _pitch = 0.0

  def __init__(self,radii=None,subr=None,subazi=None,pitch=None,height=None,source=None):
    if source:
      self._radii = source._radii
      self._submesh_r = source._submesh_r
      self._submesh_azi = source._submesh_azi
      self._pitch = source._pitch
      self._nRegions = source._nRegions
    elif radii and subr and subazi and pitch and height:
      if any([radius <= 0.0 for radius in radii]):
        raise ValueError
      elif sorted(radii) != radii:
        raise ValueError
      if len(subr) != len(radii):
        raise ValueError
      elif any([sub < 1 for sub in subr]):
        raise ValueError
      if len(subazi) != sum(subr)+1:
        raise ValueError
      elif any([sub < 1 for sub in subazi]):
        raise ValueError
      if pitch <= 0.0:
        raise ValueError

      self._radii = radii[:]
      self._submesh_r = subr[:]
      self._submesh_azi = subazi[:]
      self._pitch = pitch
      self._nRegions = len(self._radii)+1
    super(pinmeshClass_cyl, self).__init__(height=height, source=source)

  @classmethod
  def create(cls,radii=None,subr=None,subazi=None,pitch=None,height=None,source=None):
    newObject = pinmeshClass_cyl(radii,subr,subazi,pitch,height,source)
    return cls.testCreation(newObject, pinmeshClass.addObject(newObject))

  @classmethod
  def clonePinMesh(cls, source):
    return cls(source=source)

  def __eq__(self, other):
    if isinstance(other, pinmeshClass_cyl):
      if self._radii[:] == other._radii[:] and self._submesh_r[:] == other._submesh_r[:] and \
          self._submesh_azi[:] == other._submesh_azi[:] and self._pitch == other._pitch:
        return (True and super(pinmeshClass_cyl, self).__eq__(other))
      else:
        return False
    else:
      return False

  def getX(self):
    return self._pitch

  def getY(self):
    return self._pitch

  def getRegionCentroid(self, region):
    if region > len(self._radii):
      centroid = [self._radii[-1], self._radii[-1]]
    else:
      centroid = [self._radii[region-1], self._radii[region-1]]

    return centroid

  def edit(self):
    print '  pinmesh ' + format(self._id,'2d') + ' cyl ' + \
        ' '.join(format(radius,float_edit_format) for radius in self._radii) + ' / ' + \
        format(self._pitch,float_edit_format) + ' / ' + format(self._height,float_edit_format) + ' / ' + \
        ' '.join(str(subr) for subr in self._submesh_r) + ' / ' + \
        ' '.join(str(azi) for azi in self._submesh_azi) + ' / 1'

class pinmeshClass_qcyl(pinmeshClass_cyl):
  _quadrant = 0

  def __init__(self,radii=None,subr=None,subazi=None,pitch=None,height=None,quad=None,source=None):
    if source:
      self._quadrant = source._quadrant
    else:
      assert(quad > 0 and quad < 5)
      self._quadrant = quad
    super(pinmeshClass_qcyl, self).__init__(radii=radii,subr=subr,subazi=subazi,pitch=pitch,height=height,source=source)

  @classmethod
  def create(cls,radii=None,subr=None,subazi=None,pitch=None,height=None,quad=None,source=None):
    newObject = pinmeshClass_qcyl(radii,subr,subazi,pitch,height,quad,source)
    return cls.testCreation(newObject, pinmeshClass.addObject(newObject))

  @classmethod
  def clonePinMesh(cls, source):
    return cls(source=source)

  def __eq__(self, other):
    if isinstance(other, pinmeshClass_qcyl):
      if self._quadrant == other._quadrant:
        return (True and super(pinmeshClass_qcyl, self).__eq__(other))
      else:
        return False
    else:
      return False

  def getRegionCentroid(self, region):
    centroid = super(pinmeshClass_qcyl, self).getRegionCentroid(region)

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

class pinmeshClass_gcyl(pinmeshClass):
  _radii = []
  _submesh_r = []
  _submesh_azi = []
  _xMin = 0.0
  _xMax = 0.0
  _yMin = 0.0
  _yMax = 0.0

  def __init__(self,radii=None,subr=None,subazi=None,xMin=None,xMax=None,yMin=None,yMax=None,height=None,source=None):
    if source:
      self._radii = source._radii
      self._submesh_r = source._submesh_r
      self._submesh_azi = source._submesh_azi
      self._xMin = source._xMin
      self._xMax = source._xMax
      self._yMin = source._yMin
      self._yMax = source._yMax
      self._nRegions = source._nRegions
    elif radii and subr and subazi and xMin and xMax and yMin and yMax and height:
      if any([radius <= 0.0 for radius in radii]):
        raise ValueError
      elif sorted(radii) != radii:
        raise ValueError
      if len(subr) != len(radii):
        raise ValueError
      elif any([sub < 1 for sub in subr]):
        raise ValueError
      if len(subazi) != sum(subr)+1:
        raise ValueError
      elif any([sub < 1 for sub in subazi]):
        raise ValueError
      if xMax <= xMin:
        raise ValueError
      if yMax <= yMin:
        raise ValueError

      self._radii = radii[:]
      self._submesh_r = subr[:]
      self._submesh_azi = subazi[:]
      self._xMin = xMin
      self._xMax = xMax
      self._yMin = yMin
      self._yMax = yMax
      self._nRegions = len(self._radii)+1
    super(pinmeshClass_gcyl, self).__init__(height=height, source=source)

  @classmethod
  def create(cls,radii=None,subr=None,subazi=None,xMin=None,xMax=None,yMin=None,yMax=None,height=None,source=None):
    newObject = pinmeshClass_cyl(radii,subr,subazi,xMin,xMax,yMin,yMax,height,source)
    return cls.testCreation(newObject, pinmeshClass.addObject(newObject))

  @classmethod
  def clonePinMesh(cls, source):
    return cls(source=source)

  def __eq__(self, other):
    if isinstance(other, pinmeshClass_cyl):
      if self._radii[:] == other._radii[:] and self._submesh_r[:] == other._submesh_r[:] and \
          self._submesh_azi[:] == other._submesh_azi[:] and self._xMin == other._xMin and \
          self._xMax == other._xMax and self._yMin == other._yMin and self._yMax == other._yMax:
        return (True and super(pinmeshClass_cyl, self).__eq__(other))
      else:
        return False
    else:
      return False

  def getX(self):
    return self._xMax - self._xMin

  def getY(self):
    return self._yMax - self._yMin

  def getRegionCentroid(self, region):
    # Need to implement this properly using MCFR_geomUtils as a base for calculating centroids
    if region > len(self._radii):
      centroid = [self._radii[-1], self._radii[-1]]
    else:
      centroid = [self._radii[region-1], self._radii[region-1]]

    return centroid

  def edit(self):
    print '  pinmesh ' + format(self._id,'2d') + ' gcyl ' + \
        ' '.join(format(radius,float_edit_format) for radius in self._radii) + ' / ' + \
        ' '.join(format(value,float_edit_format) for value in [self._xMin, self._xMax, self._yMin, self._yMax]) + ' / ' + \
        format(self._height,float_edit_format) + ' / ' + \
        ' '.join(str(subr) for subr in self._submesh_r) + ' / ' + \
        ' '.join(str(azi) for azi in self._submesh_azi) + ' / 1'

class pinmeshClass_rect(pinmeshClass):
  _nx = 0
  _ny = 0
  _x = []
  _y = []
  _submesh_x = []
  _submesh_y = []

  def __init__(self,x=None,y=None,subx=None,suby=None,height=None,source=None):
    if source:
      self._x = source._x
      self._y = source._y
      self._nx = source._nx
      self._ny = source._ny
      self._submesh_x = source._submesh_x
      self._submesh_y = source._submesh_y
      self._nRegions = source._nRegions
    else:
      self._x = x[:]
      self._y = y[:]
      self._nx = len(x)
      self._ny = len(y)
      self._submesh_x = subx[:]
      self._submesh_y = suby[:]
      self._nRegions = len(x)*len(y)
    super(pinmeshClass_rect, self).__init__(height=height,source=source)

  @classmethod
  def create(cls, x=None,y=None,subx=None,suby=None,height=None,source=None):
    newObject = pinmeshClass_rect(x=x,y=y,subx=subx,suby=suby,height=height,source=source)
    return cls.testCreation(newObject, pinmeshClass.addObject(newObject))

  @classmethod
  def clonePinMesh(cls, source):
    return cls(source=source)

  def __eq__(self, other):
    if isinstance(other, pinmeshClass_rect):
      if self._nx == other._nx and self._ny == other._ny and self._x[:] == other._x[:] and \
          self._y[:] == other._y[:] and self._submesh_x[:] == other._submesh_x[:] and \
          self._submesh_y[:] == other._submesh_y[:]:
        return (True and super(pinmeshClass_rect, self).__eq__(other))
      else:
        return False
    else:
      return False

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
      for material in materials:
        if isinstance(material, list):
          raise ValueError
    elif source:
      self._id = copy.deepcopy(source._id)
      self._pinmesh = source._pinmesh
      self._materials = copy.deepcopy(source._materials)
    super(pinClass, self).__init__(height=self._pinmesh._height, source=source)

  @classmethod
  def create(cls, pinmesh=None, materials=None, source=None):
    newObject = pinClass(pinmesh, materials, source)
    return cls.testCreation(newObject, pinClass.addObject(newObject))

  def __eq__(self, other):
    if isinstance(other, pinClass):
      if self._materials[:] == other._materials[:] and self._pinmesh == other._pinmesh:
        return True
      else:
        return False
    else:
      return False

  @staticmethod
  def getNextID():
    pinClass._nextID += 1
    return pinClass._nextID

  @classmethod
  def getList(cls):
    if not pinClass._list:
      pinClass._list = []
    return pinClass._list

  @staticmethod
  def removePin(id):
    for ipin in range(len(pinClass._list)):
      pin = pinClass._list[ipin]
      if pin._id == id:
        pin == pinClass._list.pop(ipin)
        del pin
        return

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
      return pinClass.addObject(clone)

  def extrude(self, height):
    if self._height == height:
      return self

    newPinMesh = self._pinmesh.extrude(height)
    newPin = pinClass.create(newPinMesh, self._materials)
    return  self.testCreation(newPin, pinClass.addObject(newPin))

  @staticmethod
  def prune():
    removalIDs = []
    for ipinmesh in range(len(pinmeshClass._list)):
      id = pinmeshClass._list[ipinmesh]._id
      found = False
      for pin in pinClass._list:
        if pin._pinmesh._id == id:
          found = True
          break
      if not found:
        removalIDs.append(id)
    for id in removalIDs:
      pinmeshClass.removePinMesh(id)

  @staticmethod
  def editAll():
    [pin.edit() for pin in pinClass._list]
    print

  def edit(self):
    print '  pin ' + format(self._id,'4d') + ' ' + format(self._pinmesh._id) + ' / ' + \
        ' '.join(str(material) for material in self._materials)

class latticeClass(geomClass):
  _nextID = 0
  _pins = None
  _nx = 0
  _ny = 0
  _delx = None
  _dely = None

  def __init__(self, nx=None, ny=None, source=None):
    if nx and ny:
      self._nx = nx
      self._ny = ny
      self._pins = []
      for j in range(ny):
        self._pins.append([])
        for i in range(nx):
          self._pins[j].append(None)
      self._delx = [-1.0]*self._nx
      self._dely = [-1.0]*self._ny
      latticeClass.addObject(self)
    elif source:
      self._id = copy.deepcopy(source._id)
      self._pins = copy.deepcopy(source._pins)
      self._nx = copy.deepcopy(source._nx)
      self._ny = copy.deepcopy(source._ny)
      self._delx = copy.deepcopy(source._delx)
      self._dely = copy.deepcopy(source._dely)

  @classmethod
  def create(cls, nx=None, ny=None, source=None):
    newObject = latticeClass(nx, ny, source)
    return cls.testCreation(newObject, latticeClass.addObject(newObject))

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

  @classmethod
  def getList(cls):
    if not latticeClass._list:
      latticeClass._list = []
    return latticeClass._list

  @staticmethod
  def removeLattice(id):
    for ilattice in range(len(latticeClass._list)):
      lattice = latticeClass._list[ilattice]
      if lattice._id ==  id:
        lattice = latticeClass._list.pop(ilattice)
        del lattice
        return

  def setPin(self,ix,iy,pin):
    self._pins[iy-1][ix-1] = pin
    if self._delx[ix-1] > 0.0 and not np.isclose(self._delx[ix-1],pin.getX()):
      raise ValueError
    else:
      self._delx[ix-1] = pin.getX()
    if self._dely[iy-1] > 0.0 and not np.isclose(self._dely[iy-1],pin.getY()):
      raise ValueError
    else:
      self._dely[iy-1] = pin.getY()
    test = np.isclose(pin._height, self._height)
    if self._height > 0.0 and not test:
      raise ValueError
    else:
      self._height = pin._height

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
      return latticeClass.addObject(clone)

  def extrude(self, height):
    if self._height == height:
      return self

    pinIsSet = []
    for iy in range(self._ny):
      pinIsSet.append([])
      for ix in range(self._nx):
        pinIsSet[iy].append(False)

    newLattice = latticeClass(source=self)
    for iy in range(self._ny):
      for ix in range(self._nx):
        if pinIsSet[iy][ix]:
          continue
        pin = self.getPin(ix+1,iy+1)
        newPin = pin.extrude(height)
        for iy2 in range(self._ny):
          for ix2 in range(self._nx):
            if newLattice.getPin(ix2+1,iy2+1)._id == pin._id:
              newLattice.setPin(ix2+1,iy2+1,newPin)
              pinIsSet[iy2][ix2] = True
    return self.testCreation(newLattice, latticeClass.addObject(newLattice))

  @staticmethod
  def prune():
    removalIDs = []
    for ipin in range(len(pinClass._list)):
      id = pinClass._list[ipin]._id
      found = False
      for lattice in latticeClass._list:
        for iy in range(lattice._ny):
          for ix in range(lattice._nx):
            pin = lattice.getPin(ix+1,iy+1)
            if pin._id == id:
              found = True
              break
          if found:
            break
        if found:
          break
      if not found:
        removalIDs.append(id)
    for id in removalIDs:
      pinClass.removePin(id)

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
      self._height = copy.deepcopy(0.0)
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

  @classmethod
  def getList(cls):
    if not assemblyClass._list:
      assemblyClass._list = []
    return assemblyClass._list

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

  @staticmethod
  def removeAssembly(id):
    for iassembly in range(len(assemblyClass._list)):
      assembly = assemblyClass._list[iassembly]
      if assembly._id == id:
        assembly = assemblyClass._list.pop(iassembly)
        del assembly
        return

  def setLattice(self,iz,lattice):
    self._height -= self._lattices[iz-1]._height
    self._lattices[iz-1] = lattice
    self._height += lattice._height

  def getLattice(self,iz):
    return self._lattices[iz-1]

  def addTopLattice(self,lattice):
    if self._lattices:
      self._lattices.append(lattice)
    else:
      self._lattices = [lattice]
    self._nz += 1
    self._height += lattice._height

  def addBottomLattice(self,lattice):
    if self._lattices:
      self._lattices.insert(0, lattice)
    else:
      self._lattices = [lattice]
    self._nz += 1
    self._height += lattice._height

  def getX(self):
    return self._lattices[0].getX()

  def getY(self):
    return self._lattices[0].getY()

  def replaceMaterials(self, radius, material, origin, outerRadius=100000000000.0):
    clone = assemblyClass(source=self)
    lattice = self.getLattice(1)
    corners = lattice.getCorners(origin)
    if ldebug:
      print 'assembly:', iz, origin, corners, ':', radius, outerRadius, ':', lattice
    if not any(pointsInCircle(corners, outerRadius)) or all(pointsInCircle(corners, radius)):
      pass
    else:
      for iz in range(self._nz):
        lattice = self.getLattice(iz+1)
        if iz > 0:
          if lattice is self.getLattice(iz):
            clone.setLattice(iz+1,clone.getLattice(iz))
            continue
        newlattice = lattice.replaceMaterials(radius, material, origin, outerRadius)
        if ldebug:
          print iz, newlattice
        clone.setLattice(iz+1,newlattice)
    if ldebug:
      print

    if clone == self:
      del clone
      return self
    else:
      return assemblyClass.addAssembly(clone)

  def extrudeTop(self, height):
    lattice = self.getLattice(self._nz)
    if lattice._height == height:
      newLattice = lattice
    else:
      newLattice = lattice.extrude(height)
    self.addTopLattice(newLattice)
    self._height += height

  def extrudeBottom(self, height):
    lattice = self.getLattice(1)
    if lattice._height == height:
      newLattice = lattice
    else:
      newLattice = lattice.extrude(height)
    self.addBottomLattice(newLattice)
    self._height += height

  @staticmethod
  def prune():
    removalIDs = []
    for ilattice in range(len(latticeClass._list)):
      id = latticeClass._list[ilattice]._id
      found = False
      for assembly in assemblyClass._list:
        for iz in range(assembly._nz):
          lattice = assembly.getLattice(iz+1)
          if lattice._id == id:
            found = True
            break
        if found:
          break
      if not found:
        removalIDs.append(id)
    for id in removalIDs:
      latticeClass.removeLattice(id)

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
  _delx = None
  _dely = None
  _offset = []

  def __init__(self,nx,ny):
    self._nx = nx
    self._ny = ny
    for j in range(ny):
      self._assemblies.append([])
      for i in range(nx):
        self._assemblies[j].append(None)
    self._delx = [-1.0]*self._nx
    self._dely = [-1.0]*self._ny

  def setAssembly(self,ix,iy,assembly):
    self._assemblies[iy-1][ix-1] = assembly
    if not assembly:
      return
    if self._delx[ix-1] > 0.0 and self._delx[ix-1] != assembly.getX():
      raise ValueError
    else:
      self._delx[ix-1] = assembly.getX()
    if self._dely[iy-1] > 0.0 and self._dely[iy-1] != assembly.getY():
      raise ValueError
    else:
      self._dely[iy-1] = assembly.getY()
    self._offset = [sum(self._delx)/2.0, sum(self._dely)/2.0]

  def getAssembly(self,ix,iy):
    return self._assemblies[iy-1][ix-1]

  def getAssemblyCorners(self,ix,iy):
    corners = []
    for (x, y) in zip([ix-1, ix, ix-1, ix], [iy-1, iy-1, iy, iy]):
      corners.append([sum(self._delx[0:x])-self._offset[0], sum(self._dely[0:y])-self._offset[1]])
    return corners

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

  def extrudeTop(self, height, iterations=1):
    isExtruded = [[False for assembly in range(self._nx)] for row in range(self._ny)]
    for iy in range(self._ny):
      for ix in range(self._nx):
        if isExtruded[iy][ix]:
          continue
        assembly = self.getAssembly(ix+1,iy+1)
        if assembly:
          for iteration in range(iterations):
            assembly.extrudeTop(height)
          for iy2 in range(self._ny):
            for ix2 in range(self._nx):
              assembly2 = self.getAssembly(ix2+1,iy2+1)
              if assembly2:
                if assembly2._id == assembly._id:
                  isExtruded[iy2][ix2] = True

  def extrudeBottom(self, height):
    for iy in range(self._ny):
      for ix in range(self._nx):
        self.getAssembly(ix+1,iy+1),extrudeBottom(height)

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

  def prune(self):
    removalIDs = []
    for iassembly in range(len(assemblyClass._list)):
      id = assemblyClass._list[iassembly]._id
      found = False
      for iy in range(self._ny):
        for ix in range(self._nx):
          assembly = self.getAssembly(ix+1,iy+1)
          if assembly:
            if assembly._id == id:
              found = True
              break
        if found:
          break
      if not found:
        removalIDs.append(id)
    for id in removalIDs:
      assemblyClass.removeAssembly(id)

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
      print '  mod_dim ' + ' '.join(format(value,float_edit_format) for value in \
          [assembly.getX(), assembly.getY()] + list(set([lattice._height \
          for lattice in latticeClass.getList()])))
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

def buildGraphiteBlockCenter(height, material=None):
  newLattice = latticeClass.create(pins_per_lattice, pins_per_lattice)
  if not material:
    material = materials['Graphite']

  # Useful values
  cell_length_long = channel_length - 2*channel_radius
  cell_length_short = (block_pitch - cell_length_long)/(pins_per_lattice - 1)
  nsub_short = 3 # Needs to be a multiple of 3 for radii to line up
  nsub_long = 2*nsub_short

  # Set the small graphite square pins - 4 corners and 4 diagonal locations (excluding center)
  newPinMesh = pinmeshClass_rect.create([cell_length_short*(i+1)/nsub_short for i in range(nsub_short)], \
      [cell_length_short*(i+1)/nsub_short for i in range(nsub_short)], [1 for i in range(nsub_short)], \
      [1 for i in range(nsub_short)],height)
  newPin = pinClass.create(newPinMesh, [material for i in range(nsub_short*nsub_short)])
  for (ix, iy) in zip([2, 4, 2, 4], [2, 2, 4, 4]):
    newLattice.setPin(ix,iy,newPin)

  # Set the N/S rectangular graphite pieces
  newPinMesh = pinmeshClass_rect.create([cell_length_long*(i+1)/nsub_long for i in range(nsub_long)], \
      [cell_length_short*(i+1)/nsub_short for i in range(nsub_short)], [1 for i in range(nsub_long)], \
      [1 for i in range(nsub_short)],height)
  newPin = pinClass.create(newPinMesh, [material for i in range(nsub_long*nsub_short)])
  newLattice.setPin(3,2,newPin)
  newLattice.setPin(3,4,newPin)

  # Set the E/W rectangular graphite pieces
  newPinMesh = pinmeshClass_rect.create([cell_length_short*(i+1)/nsub_short for i in range(nsub_short)], \
      [cell_length_long*(i+1)/nsub_long for i in range(nsub_long)], [1 for i in range(nsub_short)], \
      [1 for i in range(nsub_long)],height)
  newPin = pinClass.create(newPinMesh, [material for i in range(nsub_short*nsub_long)])
  newLattice.setPin(2,3,newPin)
  newLattice.setPin(4,3,newPin)

  # Set the center pin cell
  newPinMesh = pinmeshClass_rect.create([cell_length_long*(i+1)/nsub_long for i in range(nsub_long)], \
      [cell_length_long*(i+1)/nsub_long for i in range(nsub_long)], [1 for i in range(nsub_long)], \
      [1 for i in range(nsub_long)],height)
  newPin = pinClass.create(newPinMesh, [material for i in range(nsub_long*nsub_long)])
  newLattice.setPin(3,3,newPin)

  return newLattice

def buildGraphiteStringerLattice(height):
  newLattice = buildGraphiteBlockCenter(height)

  newPin = newLattice.getPin(2,2)
  for (ix, iy) in zip([1, 5, 1, 5], [1, 1, 5, 5]):
    newLattice.setPin(ix,iy,newPin)

  # Set the W/E fuel channel sides
  newPinMesh = newLattice.getPin(2,3)._pinmesh
  newPin = pinClass.create(newPinMesh, [materials[key] for key in ['Fuel Salt','Fuel Salt','Graphite', \
      'Fuel Salt','Fuel Salt','Graphite','Fuel Salt','Fuel Salt','Graphite','Fuel Salt','Fuel Salt', \
      'Graphite','Fuel Salt','Fuel Salt','Graphite','Fuel Salt','Fuel Salt','Graphite']])
  newLattice.setPin(1,3,newPin)
  newPin = pinClass.create(newPinMesh, [materials[key] for key in ['Graphite','Fuel Salt','Fuel Salt', \
      'Graphite','Fuel Salt','Fuel Salt','Graphite','Fuel Salt','Fuel Salt','Graphite','Fuel Salt', \
      'Fuel Salt','Graphite','Fuel Salt','Fuel Salt','Graphite','Fuel Salt','Fuel Salt']])
  newLattice.setPin(5,3,newPin)

  # Set the N/S fuel channel sides
  newPinMesh = newLattice.getPin(3,2)._pinmesh
  newPin = pinClass.create(newPinMesh, [materials[key] for key in ['Fuel Salt','Fuel Salt','Fuel Salt', \
      'Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt', \
      'Fuel Salt','Graphite','Graphite','Graphite','Graphite','Graphite','Graphite']])
  newLattice.setPin(3,1,newPin)
  newPin = pinClass.create(newPinMesh, [materials[key] for key in ['Graphite','Graphite','Graphite','Graphite', \
      'Graphite','Graphite','Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt', \
      'Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt','Fuel Salt']])
  newLattice.setPin(3,5,newPin)

  # Set the NE quarter pins
  newPinMesh = pinmeshClass_qcyl.create([cell_length_short*(i+1)/nsub_short for i in range(nsub_short-1)], \
      [1 for i in range(nsub_short-1)], [1 for i in range(nsub_short)], cell_length_short, height, 1)
  newPin = pinClass.create(newPinMesh, [materials[key] for key in ['Fuel Salt','Fuel Salt','Graphite']])
  newLattice.setPin(1,2,newPin)
  newLattice.setPin(4,5,newPin)

  # Set the NW quarter pins
  newPinMesh = pinmeshClass_qcyl.create([cell_length_short*(i+1)/nsub_short for i in range(nsub_short-1)], \
      [1 for i in range(nsub_short-1)], [1 for i in range(nsub_short)], cell_length_short, height, 2)
  newPin = pinClass.create(newPinMesh, [materials[key] for key in ['Fuel Salt','Fuel Salt','Graphite']])
  newLattice.setPin(5,2,newPin)
  newLattice.setPin(2,5,newPin)

  # Set the SW quarter pins
  newPinMesh = pinmeshClass_qcyl.create([cell_length_short*(i+1)/nsub_short for i in range(nsub_short-1)], \
      [1 for i in range(nsub_short-1)], [1 for i in range(nsub_short)], cell_length_short, height, 3)
  newPin = pinClass.create(newPinMesh, [materials[key] for key in ['Fuel Salt','Fuel Salt','Graphite']])
  newLattice.setPin(2,1,newPin)
  newLattice.setPin(5,4,newPin)

  # Set the SE quarter pins
  newPinMesh = pinmeshClass_qcyl.create([cell_length_short*(i+1)/nsub_short for i in range(nsub_short-1)], \
      [1 for i in range(nsub_short-1)], [1 for i in range(nsub_short)], cell_length_short, height, 4)
  newPin = pinClass.create(newPinMesh, [materials[key] for key in ['Fuel Salt','Fuel Salt','Graphite']])
  newLattice.setPin(4,1,newPin)
  newLattice.setPin(1,4,newPin)

  return newLattice.addObject(newLattice)

def buildUniformLattice(material, height):
  newLattice = buildGraphiteBlockCenter(height, material)

  # Copy small graphite blocks
  for (ix,iy) in zip([1, 2, 4, 5, 1, 5, 1, 5, 1, 2, 4, 5], [1, 1, 1, 1, 2, 2, 4, 4, 5, 5, 5, 5]):
    newLattice.setPin(ix,iy,newLattice.getPin(2,2))

  # Copy E/W graphite blocks
  newLattice.setPin(1,3,newLattice.getPin(2,3))
  newLattice.setPin(5,3,newLattice.getPin(2,3))

  # Copy N/S graphite blocks
  newLattice.setPin(3,1,newLattice.getPin(3,2))
  newLattice.setPin(3,5,newLattice.getPin(3,2))

  newLattice = newLattice.replaceMaterials(0.0, material, [0.0, 0.0])

  return newLattice.addObject(newLattice)

def buildSupportLattice1(height):
  newLattice = buildGraphiteBlockCenter(height)

  salt_width = 0.47625

  # Copy the center portions to the N/S edges
  newPin = newLattice.getPin(3,2)
  newLattice.setPin(3,1,newPin)
  newLattice.setPin(3,5,newPin)

  newPin = newLattice.getPin(2,2)
  newLattice.setPin(2,1,newPin)
  newLattice.setPin(2,5,newPin)
  newLattice.setPin(4,1,newPin)
  newLattice.setPin(4,5,newPin)

  # Set the W small salt/graphite squares
  newPinMesh = pinmeshClass_rect.create([salt_width*(i+1)/(nsub_short-1) for i in range(nsub_short-1)] + [cell_length_short], \
      [cell_length_short*(i+1)/nsub_short for i in range(nsub_short)], [1 for i in range(nsub_short)], \
      [1 for i in range(nsub_short)], height)
  newPin = pinClass.create(newPinMesh, [materials['Fuel Salt'] if (i+1)*3 <= 2*nsub_short else materials['Graphite'] for i in range(nsub_short)]*nsub_short)
  for iy in [1, 2, 4, 5]:
    newLattice.setPin(1,iy,newPin)

  # Set the E small salt/graphite squares
  newPinMesh = pinmeshClass_rect.create([cell_length_short - salt_width*i/(nsub_short-1) for i in reversed(range(nsub_short))], \
      [cell_length_short*(i+1)/nsub_short for i in range(nsub_short)], [1 for i in range(nsub_short)], \
      [1 for i in range(nsub_short)], height)
  newPin = pinClass.create(newPinMesh, [materials['Graphite'] if (i+1)*3 <= nsub_short else materials['Fuel Salt'] for i in range(nsub_short)]*nsub_short)
  for iy in [1, 2, 4, 5]:
    newLattice.setPin(5,iy,newPin)

  # Set the W long salt/graphite rectangles
  newPinMesh = pinmeshClass_rect.create([salt_width*(i+1)/(nsub_short-1) for i in range(nsub_short-1)] + [cell_length_short], \
      [cell_length_long*(i+1)/nsub_long for i in range(nsub_long)], [1 for i in range(nsub_short)], \
      [1 for i in range(nsub_long)], height)
  newPin = pinClass.create(newPinMesh, [materials['Fuel Salt'] if (i+1)*3 <= 2*nsub_short else materials['Graphite'] for i in range(nsub_short)]*nsub_long)
  newLattice.setPin(1,3,newPin)

  # Set the E long salt/graphite rectangles
  newPinMesh = pinmeshClass_rect.create([cell_length_short - salt_width*i/(nsub_short-1) for i in reversed(range(nsub_short))], \
      [cell_length_long*(i+1)/nsub_long for i in range(nsub_long)], [1 for i in range(nsub_short)], \
      [1 for i in range(nsub_long)], height)
  newPin = pinClass.create(newPinMesh, [materials['Graphite'] if (i+1)*3 <= nsub_short else materials['Fuel Salt'] for i in range(nsub_short)]*nsub_long)
  newLattice.setPin(5,3,newPin)

  return newLattice.addObject(newLattice)

def buildSupportLattice2(height):
  newLattice = buildGraphiteBlockCenter(height)

  salt_width = 0.47625

  # Copy the center portions to the E/W edges
  newPin = newLattice.getPin(2,3)
  newLattice.setPin(1,3,newPin)
  newLattice.setPin(5,3,newPin)

  newPin = newLattice.getPin(2,2)
  newLattice.setPin(1,2,newPin)
  newLattice.setPin(5,2,newPin)
  newLattice.setPin(1,4,newPin)
  newLattice.setPin(5,4,newPin)

  # Set the N small salt/graphite squares
  newPinMesh = pinmeshClass_rect.create([cell_length_short*(i+1)/nsub_short for i in range(nsub_short)], \
      [cell_length_short - salt_width*i/(nsub_short-1) for i in reversed(range(nsub_short))], \
      [1 for i in range(nsub_short)], [1 for i in range(nsub_short)], height)
  newPin = pinClass.create(newPinMesh, [materials['Fuel Salt'] if (i+1) <= 2*nsub_short else materials['Graphite'] for i in range(nsub_short*nsub_short)])
  for ix in [1, 2, 4, 5]:
    newLattice.setPin(ix,1,newPin)

  # Set the S small salt/graphite squares
  newPinMesh = pinmeshClass_rect.create([cell_length_short*(i+1)/nsub_short for i in range(nsub_short)], \
      [salt_width*(i+1)/(nsub_short-1) for i in range(nsub_short-1)] + [cell_length_short], \
      [1 for i in range(nsub_short)], [1 for i in range(nsub_short)], height)
  newPin = pinClass.create(newPinMesh, [materials['Graphite'] if (i+1) <= nsub_short else materials['Fuel Salt'] for i in range(nsub_short*nsub_short)])
  for ix in [1, 2, 4, 5]:
    newLattice.setPin(ix,5,newPin)

  # Set the N long salt/graphite squares
  newPinMesh = pinmeshClass_rect.create([cell_length_long*(i+1)/nsub_long for i in range(nsub_long)], \
      [cell_length_short - salt_width*i/(nsub_short-1) for i in reversed(range(nsub_short))], \
      [1 for i in range(nsub_long)], [1 for i in range(nsub_short)], height)
  newPin = pinClass.create(newPinMesh, [materials['Fuel Salt'] if (i+1)*3 <= 2*nsub_long*nsub_short else materials['Graphite'] for i in range(nsub_long*nsub_short)])
  newLattice.setPin(3,1,newPin)

  # Set the S long salt/graphite squares
  newPinMesh = pinmeshClass_rect.create([cell_length_long*(i+1)/nsub_long for i in range(nsub_long)], \
      [salt_width*(i+1)/(nsub_short-1) for i in range(nsub_short-1)] + [cell_length_short], \
      [1 for i in range(nsub_long)], [1 for i in range(nsub_short)], height)
  newPin = pinClass.create(newPinMesh, [materials['Graphite'] if (i+1)*3 <= nsub_long*nsub_short else materials['Fuel Salt'] for i in range(nsub_long*nsub_short)])
  newLattice.setPin(3,5,newPin)

  return newLattice.addObject(newLattice)

def buildTaperedStringerLattice(height):
  newLattice = latticeClass.create(3, 3)

  local_long_length = cell_length_short*2.0 + cell_length_long
  local_nsub_long = nsub_short*2 + nsub_long

  # Approximated tapering (cylinder instead of cone)
  newPinMesh = pinmeshClass_cyl.create([np.sqrt(2.54*2.54/3)], [3], [1]*4, \
      local_long_length, height)
  newPin = pinClass.create(newPinMesh, [materials['Graphite'], materials['Fuel Salt']])
  newLattice.setPin(2,2,newPin)

  # Corners
  newPinMesh = pinmeshClass_rect.create([cell_length_short*(i+1)/nsub_short for i in range(nsub_short)], \
      [cell_length_short*(i+1)/nsub_short for i in range(nsub_short)], [1 for i in range(nsub_short)], \
      [1 for i in range(nsub_short)], height)
  newPin = pinClass.create(newPinMesh, [materials['Fuel Salt'] for i in range(nsub_short*nsub_short)])
  newLattice.setPin(1,1,newPin)
  newLattice.setPin(1,3,newPin)
  newLattice.setPin(3,1,newPin)
  newLattice.setPin(3,3,newPin)

  # Top/Bottom
  newPinMesh = pinmeshClass_rect.create([local_long_length*(i+1)/local_nsub_long for i in range(local_nsub_long)], \
      [cell_length_short*(i+1)/nsub_short for i in range(nsub_short)], [1 for i in range(local_nsub_long)], \
      [1 for i in range(nsub_short)], height)
  newPin = pinClass.create(newPinMesh, [materials['Fuel Salt'] for i in range(local_nsub_long*nsub_short)])
  newLattice.setPin(2,1,newPin)
  newLattice.setPin(2,3,newPin)

  # East/West
  newPinMesh = pinmeshClass_rect.create([cell_length_short*(i+1)/nsub_short for i in range(nsub_short)], \
      [local_long_length*(i+1)/local_nsub_long for i in range(local_nsub_long)], \
      [1 for i in range(nsub_short)], [1 for i in range(local_nsub_long)], height)
  newPin = pinClass.create(newPinMesh, [materials['Fuel Salt'] for i in range(nsub_short*local_nsub_long)])
  newLattice.setPin(1,2,newPin)
  newLattice.setPin(3,2,newPin)

  return newLattice.addObject(newLattice)

def buildControlLattice(height):
  newLattice = latticeClass.create(1, 1)
  newPinMesh = pinmeshClass_cyl.create(control_rod_radii, control_rod_submesh, [1]*(sum(control_rod_submesh)+1), \
      block_pitch, height)
  newPin = pinClass.create(newPinMesh, [materials[material] for material in control_rod_materials])
  newLattice.setPin(1,1,newPin)

  return newLattice.addObject(newLattice)

def buildDowelLattice(height):
  newLattice = latticeClass.create(3, 3)

  local_long_length = cell_length_short*2.0 + cell_length_long
  local_nsub_long = nsub_short*2 + nsub_long

  # Dowel
  newPinMesh = pinmeshClass_cyl.create([dowel_radius], [1], [1, 1], local_long_length, height)
  newPin = pinClass.create(newPinMesh, [materials['Graphite'], materials['Fuel Salt']])
  newLattice.setPin(2,2,newPin)

  # Corners
  newPinMesh = pinmeshClass_rect.create([cell_length_short*(i+1)/nsub_short for i in range(nsub_short)], \
      [cell_length_short*(i+1)/nsub_short for i in range(nsub_short)], [1 for i in range(nsub_short)], \
      [1 for i in range(nsub_short)], height)
  newPin = pinClass.create(newPinMesh, [materials['Fuel Salt'] for i in range(nsub_short*nsub_short)])
  newLattice.setPin(1,1,newPin)
  newLattice.setPin(1,3,newPin)
  newLattice.setPin(3,1,newPin)
  newLattice.setPin(3,3,newPin)

  # Top/Bottom
  newPinMesh = pinmeshClass_rect.create([local_long_length*(i+1)/local_nsub_long for i in range(local_nsub_long)], \
      [cell_length_short*(i+1)/nsub_short for i in range(nsub_short)], [1 for i in range(local_nsub_long)], \
      [1 for i in range(nsub_short)], height)
  newPin = pinClass.create(newPinMesh, [materials['Fuel Salt'] for i in range(local_nsub_long*nsub_short)])
  newLattice.setPin(2,1,newPin)
  newLattice.setPin(2,3,newPin)

  # East/West
  newPinMesh = pinmeshClass_rect.create([cell_length_short*(i+1)/nsub_short for i in range(nsub_short)], \
      [local_long_length*(i+1)/local_nsub_long for i in range(local_nsub_long)], \
      [1 for i in range(nsub_short)], [1 for i in range(local_nsub_long)], height)
  newPin = pinClass.create(newPinMesh, [materials['Fuel Salt'] for i in range(nsub_short*local_nsub_long)])
  newLattice.setPin(1,2,newPin)
  newLattice.setPin(3,2,newPin)

  return newLattice.addObject(newLattice)

def buildSampleBasketLattice(height):
  newLattice = latticeClass.create(1, 1)

  newPinMesh = pinmeshClass_cyl.create(sample_basket_radius, sample_basket_submesh, [1]*(sum(sample_basket_submesh)+1), block_pitch, height)
  newPin = pinClass.create(newPinMesh, [materials['Homogenized Sample Basket'], materials['Inconel']])
  newLattice.setPin(1,1,newPin)

  return newLattice.addObject(newLattice)

def buildGraphiteStringerAssembly_Standard():
  newAssembly = assemblyClass()

  # Add the standard lattice
  newLattice = buildGraphiteStringerLattice(active_fuel_height)
  for i in range(n_fuel_planes):
    newAssembly.addTopLattice(newLattice)

  # Add bottom support lattices
  newLattice = buildSupportLattice1(support_lattice_height)
  newAssembly.addBottomLattice(newLattice)
  newLattice = buildSupportLattice2(support_lattice_height)
  newAssembly.addBottomLattice(newLattice)

  # Add dowel section
  newLattice = buildDowelLattice(dowel_section_height)
  newAssembly.addBottomLattice(newLattice)

  # Add lower head
  newLattice = buildUniformLattice(materials['Lower Head'], lower_head_height)
  for i in range(lower_head_levels):
    newAssembly.addBottomLattice(newLattice)

  # Add the tapered top
  newLattice = buildTaperedStringerLattice(stringer_top_taper_height)
  newAssembly.addTopLattice(newLattice)

  # Add level of salt above graphite
  newLattice = buildUniformLattice(materials['Fuel Salt'], upper_plenum_height)
  newAssembly.addTopLattice(newLattice)

  # Add upper head
  newLattice = newLattice.extrude(upper_head_height)
  for i in range(upper_head_levels):
    newAssembly.addTopLattice(newLattice)

  return newAssembly.addObject(newAssembly)

def buildControlAssembly():
  newAssembly = assemblyClass()

  # Active core reigon
  newLattice = buildControlLattice(active_fuel_height)
  for i in range(n_fuel_planes):
    newAssembly.addTopLattice(newLattice)

  # Add bottom support lattices
  newLattice = buildSupportLattice1(support_lattice_height)
  newAssembly.addBottomLattice(newLattice)
  newLattice = buildSupportLattice2(support_lattice_height)
  newAssembly.addBottomLattice(newLattice)

  # Add dowel section
  newLattice = buildUniformLattice(materials['Fuel Salt'], dowel_section_height)
  newAssembly.addBottomLattice(newLattice)

  # Tapered top level
  newLattice = newLattice.extrude(stringer_top_taper_height)
  newAssembly.addTopLattice(newLattice)

  # Plenum
  newLattice = newLattice.extrude(upper_plenum_height)
  newAssembly.addTopLattice(newLattice)

  # Add upper head
  newLattice = newLattice.extrude(upper_head_height)
  for i in range(upper_head_levels):
    newAssembly.addTopLattice(newLattice)

  # Add lower head
  newLattice = buildUniformLattice(materials['Lower Head'], lower_head_height)
  for i in range(lower_head_levels):
    newAssembly.addBottomLattice(newLattice)

  return newAssembly.addObject(newAssembly)

def buildSampleBasketAssembly():
  newAssembly = assemblyClass()

  # Active core region
  newLattice = buildSampleBasketLattice(active_fuel_height)
  for i in range(n_fuel_planes):
    newAssembly.addTopLattice(newLattice)

  # Add bottom support lattices
  newLattice = buildSupportLattice1(support_lattice_height)
  newAssembly.addBottomLattice(newLattice)
  newLattice = buildSupportLattice2(support_lattice_height)
  newAssembly.addBottomLattice(newLattice)

  # Add dowel section
  newLattice = buildDowelLattice(dowel_section_height)
  newAssembly.addBottomLattice(newLattice)

  # Add lower head
  newLattice = buildUniformLattice(materials['Lower Head'], lower_head_height)
  for i in range(lower_head_levels):
    newAssembly.addBottomLattice(newLattice)

  # Add the tapered top
  newLattice = buildTaperedStringerLattice(stringer_top_taper_height)
  newAssembly.addTopLattice(newLattice)

  # Add level of salt above graphite
  newLattice = buildUniformLattice(materials['Fuel Salt'], upper_plenum_height)
  newAssembly.addTopLattice(newLattice)

  # Add upper head
  newLattice = newLattice.extrude(upper_head_height)
  for i in range(upper_head_levels):
    newAssembly.addTopLattice(newLattice)

  return newAssembly.addObject(newAssembly)

def buildFillAssembly():
  newAssembly = assemblyClass()

  newLattice = buildUniformLattice(materials['Cell Gas'], active_fuel_height)
  for i in range(n_fuel_planes):
    newAssembly.addTopLattice(newLattice)

  # Add more lattices for support plane
  newLattice = newLattice.extrude(support_lattice_height)
  for i in range(2):
    newAssembly.addBottomLattice(newLattice)

  # Add fill for dowel section
  newLattice = newLattice.extrude(dowel_section_height)
  newAssembly.addBottomLattice(newLattice)

  # Add lower head
  newLattice = newLattice.extrude(lower_head_height)
  for i in range(lower_head_levels):
    newAssembly.addBottomLattice(newLattice)

  # Tapered top level
  newLattice = newLattice.extrude(stringer_top_taper_height)
  newAssembly.addTopLattice(newLattice)

  # Add level of salt above graphite
  newLattice = newLattice.extrude(upper_plenum_height)
  newAssembly.addTopLattice(newLattice)

  # Add upper head
  newLattice = newLattice.extrude(upper_head_height)
  for i in range(upper_head_levels):
    newAssembly.addTopLattice(newLattice)

  return newAssembly.addObject(newAssembly)

def pointsInCircle(points, radius, origin=[0.0, 0.0]):
  inside = []
  for coordinates in points:
    inside.append((coordinates[0]+origin[0])**2.0 + (coordinates[1]+origin[1])**2.0 <= radius**2.0)
  return inside

# Remove unused entries of things
def pruneUnusedObjects(core):
  core.prune()
  assemblyClass.prune()
  latticeClass.prune()
  pinClass.prune()

# Core Parameters
material_names = ['Fuel Salt', 'INOR-8', 'Graphite', 'Cell Gas', 'Helium Gas', 'Stainlesss Steel', 'Inconel', \
    'Control Rod Poison', 'Insulation', 'Thermal Shield', 'Homogenized Sample Basket', 'Lower Head']
materials = {key: id for (key, id) in zip(material_names, [1,2,3,4,5,6,7,8,9,10,11,12])}
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
n_fuel_planes = 16
dowel_radius = 2.54/2.0

# Sample Basket parameters
# sample_basket_radius = [2.605, 2.685]
sample_basket_radius = [2.539] #approximated due to MPACT standard input limitations
sample_basket_submesh = [5]

# Control parameters
control_rod_radii = [0.2245, 0.79375, 0.9525, 1.0033, 1.0541, 1.0668, 1.3716, 1.397, 1.4478, 2.3749, 2.539] #approximated down from 2.54
control_rod_submesh = [1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1]
control_rod_materials = ['Inconel', 'Cell Gas', 'Stainlesss Steel', 'Cell Gas', 'Inconel', 'Helium Gas', \
    'Control Rod Poison', 'Helium Gas', 'Inconel', 'Cell Gas', 'Inconel', 'Fuel Salt']

# mesh heights
lower_head_levels = 3
lower_head_height = 30.3911/float(lower_head_levels)
dowel_section_height = 3.5814
support_lattice_height = 2.54
active_fuel_height = 10.16
stringer_top_taper_height = 2.387
upper_plenum_height = 9.487
upper_head_levels = 2
upper_head_height = 23.997/float(upper_head_levels)

# Radial mesh parameters
cell_length_long = channel_length - 2*channel_radius
cell_length_short = (block_pitch - cell_length_long)/(pins_per_lattice - 1)
nsub_short = 3 # Needs to be a multiple of 3 for radii to line up
nsub_long = 2*nsub_short

ldebug = False
# Calculate how many lattices we need in the core
assemblies_across_core = 1
while assemblies_across_core*block_pitch < 2.0*reflector_radii[-1]:
  assemblies_across_core += 2
core = coreClass(assemblies_across_core, assemblies_across_core)

# Build the basic assemblies
graphiteStringerAssembly_Standard = buildGraphiteStringerAssembly_Standard()
ControlAssembly = buildControlAssembly()
SampleBasketAssembly = buildSampleBasketAssembly()
fillAssembly = buildFillAssembly()

# Set all core lattices to the graphite stringer
for iy in range(core._ny):
  for ix in range(core._nx):
    core.setAssembly(ix+1,iy+1,graphiteStringerAssembly_Standard)

# Set the control rod locations
center_assem = assemblies_across_core/2+1
# core.setAssembly(center_assem-1,center_assem-1,ControlAssembly)
# core.setAssembly(center_assem+1,center_assem-1,ControlAssembly)
# core.setAssembly(center_assem-1,center_assem+1,ControlAssembly)
# Set the sample basket location
# core.setAssembly(center_assem+1,center_assem+1,SampleBasketAssembly)

# Now set all the lattices outside the graphite lattice radius
for iy in reversed(range(core._ny)):
  for ix in range(core._nx):
    if all([not inCircle for inCircle in pointsInCircle(core.getAssemblyCorners(ix+1,iy+1), reflector_radii[0])]):
      core.setAssembly(ix+1,iy+1,fillAssembly)

core.makeJagged(reflector_radii[-1])

for zone in xrange(0,len(reflector_radii)-1):
  radius = reflector_radii[zone]
  material = reflector_materials[zone]
  region = reflector_names[zone]
  # core.replaceMaterials(radius, materials[material], reflector_radii[zone+1])
pruneUnusedObjects(core)

if not ldebug:
  core.edit()
else:
  core.edit(False)