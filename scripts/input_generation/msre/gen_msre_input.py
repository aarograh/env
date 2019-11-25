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

class pinmeshClass_cyls(pinmeshClass):
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
      if len(subazi) != sum(subr):
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
    super(pinmeshClass_cyls, self).__init__(height=height, source=source)

  @classmethod
  def create(cls,radii=None,subr=None,subazi=None,xMin=None,xMax=None,yMin=None,yMax=None,height=None,source=None):
    newObject = pinmeshClass_cyls(radii,subr,subazi,xMin,xMax,yMin,yMax,height,source)
    return cls.testCreation(newObject, pinmeshClass.addObject(newObject))

  @classmethod
  def clonePinMesh(cls, source):
    return cls(source=source)

  def __eq__(self, other):
    if isinstance(other, pinmeshClass_cyls):
      if self._radii[:] == other._radii[:] and self._submesh_r[:] == other._submesh_r[:] and \
          self._submesh_azi[:] == other._submesh_azi[:] and self._xMin == other._xMin and \
          self._xMax == other._xMax and self._yMin == other._yMin and self._yMax == other._yMax:
        return (True and super(pinmeshClass_cyls, self).__eq__(other))
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

  def getRegionIndex(self, location):
    index = 0
    for iradius in range(len(self._radii)):
      radius = self._radii[iradius]
      if location[0]*location[0] + location[1]*location[1] <= radius*radius and \
          location[0] >= self._xMin and location[0] <= self._xMax and \
          location[1] >= self._yMin and location[1] <= self._yMax:
        index = iradius + 1
        break
    return index

  def edit(self):
    print '  pinmesh ' + format(self._id,'2d') + ' cyls ' + ' '.join(str(value) for value in visit_cyls_cells) + ' / ' + \
        ' '.join(format(value,float_edit_format) for value in [self._xMin, self._xMax, self._yMin, self._yMax]) + ' / ' + \
        format(self._height,float_edit_format) + ' / 1 / ' + \
        ' '.join(format(radius,float_edit_format) for radius in self._radii) + ' / 0.000000 0.000000 / ' + \
        ' '.join(format(subr,'2d') for subr in self._submesh_r) + ' / ' + \
        ' '.join(format(azi,'2d') for azi in self._submesh_azi)

class pinmeshClass_msre(pinmeshClass):

  def __init__(self,height=None,source=None):
    self._nRegions = 6
    super(pinmeshClass_msre, self).__init__(height=height,source=source)

  @classmethod
  def create(cls,height=None,source=None):
    newObject = pinmeshClass_msre(height,source)
    return cls.testCreation(newObject, pinmeshClass.addObject(newObject))

  @classmethod
  def clonePinMesh(cls, source):
    return cls(source=source)

  def __eq__(self,other):
    if isinstance(other, pinmeshClass_msre):
      return super(pinmeshClass_msre, self).__eq__(other)
    else:
      return False

  def getX(self):
    return block_pitch

  def getY(self):
    return block_pitch

  def getRegionCentroid(self, region):
    #TODO: make this general
    # Ordering is background, center ring, north, west, south east
    if region == 1 or region == 2:
      centroid = [block_pitch/2.0]*2
    elif region == 3:
      centroid = [block_pitch/2.0, block_pitch-channel_radius/2.0]
    elif region == 4:
      centroid = [channel_radius/2.0, block_pitch/2.0]
    elif region == 5:
      centroid = [block_pitch/2.0, channel_radius/2.0]
    elif region == 6:
      centroid = [block_pitch-channel_radius/2.0, block_pitch/2.0]

    return centroid

  def getRegionIndex(self, location):
    distance_to_channel = (block_pitch - channel_length)/2.0
    index = -1
    if location[0] > channel_radius and location[0] < block_pitch-channel_radius and \
        location[1] > channel_radius and location[1] < block_pitch-channel_radius:
      if location[0]*location[0] + location[1]*location[1] <= 1.0:
        index = 1
      else:
        index = 0
    elif location[1] >= block_pitch-channel_radius:
      if location[0] < distance_to_channel or location[0] > block_pitch-distance_to_channel:
        index = 0
      else:
        index = 2
    elif location[0] < channel_radius:
      if location[1] < distance_to_channel or location[1] > block_pitch-distance_to_channel:
        index = 0
      else:
        index = 3
    elif location[1] < channel_radius:
      if location[0] < distance_to_channel or location[0] > block_pitch-distance_to_channel:
        index = 0
      else:
        index = 4
    else:
      if location[1] < distance_to_channel or location[1] > block_pitch-distance_to_channel:
        index = 0
      else:
        index = 5

    return index-1

  def edit(self):
    print '  pinmesh ' + format(self._id,'2d') + ' msre ' + ' '.join(str(value) for value in visit_cyls_cells) + ' / 3.60 / ' + format(block_pitch,float_edit_format) + ' / ' + \
        format(self._height,float_edit_format) + ' / 5 / 8 8 8 16 16 16 / 1 / ' + \
        format(channel_radius,float_edit_format) + ' / ' + format(flat_length,float_edit_format) + \
        ' / 2 / 4 4 / 6 6'

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
    if isinstance(clone._pinmesh, pinmeshClass_msre) or isinstance(clone._pinmesh, pinmeshClass_cyls):
      xmesh = [self._pinmesh.getX()*(i+1)/10 for i in range(10)]
      ymesh = [self._pinmesh.getY()*(i+1)/10 for i in range(10)]
      clone._pinmesh = pinmeshClass_rect.create(xmesh, ymesh, [1]*10, [1]*10, self._pinmesh._height)
      clone._materials = []
      for region in range(clone._pinmesh._nRegions):
        centroid = clone._pinmesh.getRegionCentroid(region+1)
        shifted_centroid = [centroid[0] + origin[0], centroid[1] + origin[1]]
        inCircle1 = pointsInCircle([shifted_centroid], radius)
        inCircle2 = pointsInCircle([shifted_centroid], outerRadius)
        if inCircle2[0] and not inCircle1[0]:
          clone._materials.append(material)
        else:
          index = self._pinmesh.getRegionIndex(centroid)
          clone._materials.append(self._materials[index])
    else:
      for region in range(self._pinmesh._nRegions):
        centroid = self._pinmesh.getRegionCentroid(region+1)
        centroid[0] += origin[0]
        centroid[1] += origin[1]
        if pointsInCircle([centroid], outerRadius)[0] and not pointsInCircle([centroid], radius)[0]:
          clone._materials[region] = copy.deepcopy(material)

    if clone == self:
      del clone
      return self
    else:
      return pinClass.addObject(clone)

  def addRings(self, radii, ring_materials, fill_material, origin):
    corners = self.getCorners(origin)
    pin_radii = []
    pin_mats = []
    for zone in range(len(radii)-1):
      inCircle1 = pointsInCircle(corners, radii[zone])
      inCircle2 = pointsInCircle(corners, radii[zone+1])
      if zone == 0:
        if any(inCircle1):
          pin_radii.append(radii[zone])
          pin_mats.append(materials[fill_material])
      if not all(inCircle1) and any(inCircle2):
        pin_radii.append(radii[zone+1])
        pin_mats.append(materials[ring_materials[zone]])

    # If any points are outside the last radius, then insert the fill material
    if not any(test for test in inCircle):
      pin_mats.insert(0, materials[fill_material])

    newPinMesh = pinmeshClass_cyls.create(pin_radii, [1]*len(pin_radii), [1]*len(pin_radii), \
        origin[0], origin[0]+self.getX(), origin[1], origin[1]+self.getY(), self._height)
    newPin = pinClass.create(newPinMesh, pin_mats)

    if newPin == self:
      del newPin
      return self
    else:
      return pinClass.addObject(newPin)

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
        test1 = any(pointsInCircle(corners, outerRadius))
        test2 = all(pointsInCircle(corners, radius))
        if not test1 or test2:
          newpin = pin
        else:
          newpin = pin.replaceMaterials(radius, material, [xstart, ystart], outerRadius)
        clone.setPin(ix+1,self._ny-iy,newpin)
        xstart += self._delx[ix]

    if clone == self:
      del clone
      return self
    else:
      return latticeClass.addObject(clone)

  def addRings(self, radii, ring_materials, fill_material, origin):
    clone = latticeClass(source=self)
    ystart = origin[1] + self.getY()
    for iy in reversed(range(self._ny)):
      ystart -= self._dely[iy]
      xstart = origin[0]
      for ix in range(self._nx):
        pin = self.getPin(ix+1,self._ny-iy)
        corners = pin.getCorners([xstart, ystart])
        if not any(pointsInCircle(corners, radii[-1])) or all(pointsInCircle(corners, radii[0])):
          newpin = pin
        else:
          newpin = pin.addRings(radii, ring_materials, fill_material, [xstart, ystart])
        clone.setPin(ix+1,self._ny-iy,newpin)
        xstart += self._delx[ix]

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
        clone.setLattice(iz+1,newlattice)

    if clone == self:
      del clone
      return self
    else:
      return assemblyClass.addAssembly(clone)

  def addRings(self, radii, materials, fill_material, origin):
    clone = assemblyClass(source=self)
    for iz in range(self._nz):
      lattice = self.getLattice(iz+1)
      if iz > 0:
        if lattice is self.getLattice(iz):
          clone.setLattice(iz+1,clone.getLattice(iz))
          continue
      newlattice = lattice.addRings(radii, materials, fill_material, origin)
      clone.setLattice(iz+1,newlattice)

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
    if edit_layer > 0 and edit_layer <= self._nz:
      print '    ' + format(self._lattices[edit_layer-1]._id,'4d')
    else:
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
    if self._delx[ix-1] > 0.0 and not np.isclose(self._delx[ix-1], assembly.getX()):
      raise ValueError
    else:
      self._delx[ix-1] = assembly.getX()
    if self._dely[iy-1] > 0.0 and not np.isclose(self._dely[iy-1], assembly.getY()):
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
          if not any(pointsInCircle(corners, outerRadius)) or all(pointsInCircle(corners, radius)):
            newAssembly = assembly
          else:
            newAssembly = assembly.replaceMaterials(radius, material, [xstart, ystart], outerRadius)
          self.setAssembly(ix+1,iy+1,newAssembly)
        xstart += self._delx[ix]
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

def buildGraphiteStringerLattice(height):
  newLattice = latticeClass.create(pins_per_lattice, pins_per_lattice)

  newPinMesh = pinmeshClass_msre.create(height)
  newPin = pinClass.create(newPinMesh, [materials[key] for key in ['Graphite'] + \
      ['Fuel Salt']*4])
  newLattice.setPin(1,1,newPin)

  return newLattice.addObject(newLattice)

def buildUniformLattice(material, height):
  newLattice = latticeClass.create(pins_per_lattice, pins_per_lattice)

  newPinMesh = pinmeshClass_rect.create([block_pitch*(i+1)/10 for i in range(10)], [block_pitch*(i+1)/10 for i in range(10)], \
      [1 for i in range(10)], [1 for i in range(10)], height)
  newPin = pinClass.create(newPinMesh, [material for i in range(100)])
  newLattice.setPin(1,1,newPin)

  return newLattice.addObject(newLattice)

def buildSupportLattice1(height):
  newLattice = latticeClass.create(pins_per_lattice, pins_per_lattice)

  salt_width = 0.47625
  graphite_width = block_pitch - 2.0*salt_width

  mesh = [salt_width] + [salt_width + graphite_width*(i+1)/8 for i in range(8)] + [block_pitch]
  newPinMesh = pinmeshClass_rect.create(mesh, mesh, [1 for i in range(10)], [1 for i in range(10)], height)
  matlist = [materials['Fuel Salt']] + [materials['Graphite']]*8 + [materials['Fuel Salt']]
  matlist = matlist*10
  newPin = pinClass.create(newPinMesh, matlist)
  newLattice.setPin(1,1,newPin)

  return newLattice.addObject(newLattice)

def buildSupportLattice2(height):
  newLattice = latticeClass.create(pins_per_lattice, pins_per_lattice)

  salt_height = 0.47625
  graphite_height = block_pitch - 2.0*salt_height

  mesh = [salt_height] + [salt_height + graphite_height*(i+1)/8 for i in range(8)] + [block_pitch]
  newPinMesh = pinmeshClass_rect.create(mesh, mesh, [1 for i in range(10)], [1 for i in range(10)], height)
  matlist = [materials['Fuel Salt']]*10 + [materials['Graphite']]*10*8 + [materials['Fuel Salt']]*10
  newPin = pinClass.create(newPinMesh, matlist)
  newLattice.setPin(1,1,newPin)

  return newLattice.addObject(newLattice)

def buildTaperedStringerLattice(height):
  newLattice = latticeClass.create(pins_per_lattice, pins_per_lattice)

  newPinMesh = pinmeshClass_cyls.create([np.sqrt(2.54*2.54/3)], [3], [8]*3, \
      -block_pitch/2.0, block_pitch/2.0, -block_pitch/2.0, block_pitch/2.0, height)
  newPin = pinClass.create(newPinMesh, [materials['Fuel Salt'], materials['Graphite']])
  newLattice.setPin(1,1,newPin)

  return newLattice.addObject(newLattice)

def buildControlLattice(height):
  newLattice = latticeClass.create(pins_per_lattice, pins_per_lattice)

  newPinMesh = pinmeshClass_cyls.create(control_rod_radii, control_rod_submesh, [8]*sum(control_rod_submesh), \
      -block_pitch/2.0, block_pitch/2.0, -block_pitch/2.0, block_pitch/2.0, height)
  newPin = pinClass.create(newPinMesh, [materials[material] for material in control_rod_materials])
  newLattice.setPin(1,1,newPin)

  return newLattice.addObject(newLattice)

def buildDowelLattice(height):
  newLattice = latticeClass.create(pins_per_lattice, pins_per_lattice)

  newPinMesh = pinmeshClass_cyls.create([dowel_radius], [3], [8]*3, -block_pitch/2.0, block_pitch/2.0, -block_pitch/2.0, block_pitch/2.0, height)
  newPin = pinClass.create(newPinMesh, [materials['Fuel Salt'], materials['Graphite']])
  newLattice.setPin(1,1,newPin)

  return newLattice.addObject(newLattice)

def buildSampleBasketLattice(height):
  newLattice = latticeClass.create(pins_per_lattice, pins_per_lattice)

  newPinMesh = pinmeshClass_cyls.create(sample_basket_radius, sample_basket_submesh, [8]*sum(sample_basket_submesh), \
      -block_pitch/2.0, block_pitch/2.0, -block_pitch/2.0, block_pitch/2.0, height)
  newPin = pinClass.create(newPinMesh, [materials['Fuel Salt'], materials['Homogenized Sample Basket'], materials['Inconel']])
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

def buildGraphiteStringerAssembly_NoTaper():
  newAssembly = assemblyClass()

  # Add the standard lattice
  newLattice = buildGraphiteStringerLattice(active_fuel_height)
  for i in range(n_fuel_planes):
    newAssembly.addTopLattice(newLattice)

  # Add the non-tapered top
  newAssembly.extrudeTop(stringer_top_taper_height)

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

  # Add level of salt above graphite
  newLattice = buildUniformLattice(materials['Fuel Salt'], upper_plenum_height)
  newAssembly.addTopLattice(newLattice)

  # Add upper head
  newLattice = newLattice.extrude(upper_head_height)
  for i in range(upper_head_levels):
    newAssembly.addTopLattice(newLattice)

  return newAssembly.addObject(newAssembly)

def buildGraphiteStringerAssembly_Center():
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

  # Add the non-tapered top
  newLattice = buildUniformLattice(materials['Fuel Salt'], stringer_top_taper_height)
  newAssembly.addTopLattice(newLattice)

  # Add level of salt above graphite
  newLattice = newLattice.extrude(upper_plenum_height)
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

  # Tapered top level
  newLattice = newLattice.extrude(stringer_top_taper_height)
  newAssembly.addTopLattice(newLattice)

  # Plenum
  newLattice = newLattice.extrude(upper_plenum_height)
  newAssembly.addTopLattice(newLattice)

  # Add upper head
  for i in range(upper_head_levels):
    newAssembly.extrudeTop(upper_head_height)

  # Add bottom support lattices
  newLattice = buildSupportLattice1(support_lattice_height)
  newAssembly.addBottomLattice(newLattice)
  newLattice = buildSupportLattice2(support_lattice_height)
  newAssembly.addBottomLattice(newLattice)

  # Add dowel section
  newLattice = buildUniformLattice(materials['Fuel Salt'], dowel_section_height)
  newAssembly.addBottomLattice(newLattice)

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

  # Add the tapered top
  newAssembly.extrudeTop(stringer_top_taper_height)

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

  newLattice = buildUniformLattice(materials[fill_material], active_fuel_height)
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
    'Control Rod Poison', 'Insulation', 'Thermal Shield', 'Homogenized Sample Basket', 'Lower Head', \
    'Control Inconel', 'Control Helium Gas']
materials = {key: id for (key, id) in zip(material_names, [1,2,3,4,5,6,7,8,9,10,11,12,13,14])}
reflector_radii = [70.168, 70.485, 71.12, 73.66, 76.2] #, 102.87, 118.11, 120.65, 156.21, 158.75]
reflector_materials = ['Fuel Salt', 'INOR-8', 'Fuel Salt', 'INOR-8'] #, 'Cell Gas', 'Insulation', \
  # 'Stainlesss Steel', 'Thermal Shield', 'Stainlesss Steel']
reflector_names = ['Graphite Core', 'Core Can Inner Radius', 'Core Can Outer Radius', 'Vessel Inner Radius', \
    'Vessel Outer Radius', 'Insulation Inner Radius', 'Insulation Outer Radius', 'Thermal Shield Inner Radius', \
    'Thermal Shield Outer Radius', 'Model Outer Radius']
fill_material = 'Helium Gas'

# Edit controls
float_edit_format = '9.6f'
visit_cyls_cells = [50, 50]
# 0 = All
# 1 = lower head
# 4 = dowel
# 5 = support 1
# 6 = support 2
# 22 = stringers
# 23 = taper
# 26 = upper head
edit_layer = 0

# Fuel block parameters
block_pitch = 5.08
channel_length = 3.048
channel_width = 0.508
channel_radius = 0.508
flat_length = channel_length - 2.0*channel_radius
pins_per_lattice = 1
n_fuel_planes = 16
dowel_radius = 2.54/2.0

# Sample Basket parameters
sample_basket_radius = [2.605, 2.685]
sample_basket_submesh = [5, 1]

# Control parameters
control_rod_radii = [0.2245, 0.79375, 0.9525, 1.0033, 1.0541, 1.0668, 1.3716, 1.397, 1.4478, 2.3749, 2.540]
control_rod_submesh = [1, 1, 1, 1, 1, 3, 1, 1, 1, 3, 1]
control_rod_materials = ['Fuel Salt', 'Inconel', 'Cell Gas', 'Stainlesss Steel', 'Cell Gas', 'Control Inconel', \
    'Control Helium Gas', 'Control Rod Poison', 'Control Helium Gas', 'Control Inconel', 'Cell Gas', 'Inconel']

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

ldebug = False
# Calculate how many lattices we need in the core
assemblies_across_core = 1
while assemblies_across_core*block_pitch < 2.0*reflector_radii[-1]:
  assemblies_across_core += 2
core = coreClass(assemblies_across_core, assemblies_across_core)

# Build the basic assemblies
graphiteStringerAssembly_Standard = buildGraphiteStringerAssembly_Standard()
graphiteStringerAssembly_NoTaper = buildGraphiteStringerAssembly_NoTaper()
graphiteStringerAssembly_Center = buildGraphiteStringerAssembly_Center()
ControlAssembly = buildControlAssembly()
SampleBasketAssembly = buildSampleBasketAssembly()
fillAssembly = buildFillAssembly()

# Need the center location for special assemblies
center_assem = assemblies_across_core/2+1

# Set all core lattices to the graphite stringer
for iy in range(core._ny):
  for ix in range(core._nx):
    # Set the center row
    if iy+1 == center_assem and (ix+1 < center_assem-2 or ix+1 > center_assem+2):
      core.setAssembly(ix+1,iy+1,graphiteStringerAssembly_NoTaper)
    # Set the center column
    elif ix+1 == center_assem and (iy+1 < center_assem-2 or iy+1 > center_assem+2):
      core.setAssembly(ix+1,iy+1,graphiteStringerAssembly_NoTaper)
    # Set the center 3x3 cross
    elif any([ix+1,iy+1] == test for test in [[center_assem, center_assem], \
        [center_assem+1, center_assem], [center_assem-1, center_assem], \
        [center_assem, center_assem+1], [center_assem, center_assem-1]]):
      core.setAssembly(ix+1,iy+1,graphiteStringerAssembly_Center)
    else:
      core.setAssembly(ix+1,iy+1,graphiteStringerAssembly_Standard)

# Set the control rod locations
core.setAssembly(center_assem-1,center_assem-1,ControlAssembly)
core.setAssembly(center_assem+1,center_assem-1,ControlAssembly)
core.setAssembly(center_assem-1,center_assem+1,ControlAssembly)
# Set the sample basket location
core.setAssembly(center_assem+1,center_assem+1,SampleBasketAssembly)

# Make the core jagged
core.makeJagged(reflector_radii[-1])

# Now set all the lattices outside the graphite lattice radius
for iy in reversed(range(core._ny)):
  for ix in range(core._nx):
    assembly = core.getAssembly(ix+1,iy+1)
    if assembly:
      inCircle = pointsInCircle(core.getAssemblyCorners(ix+1,iy+1), reflector_radii[0])
      if all(test for test in inCircle):
        newassembly = assembly
      elif any(test for test in inCircle):
        pass
        newassembly = assembly
        for zone in xrange(0,len(reflector_radii)-1):
          radius = reflector_radii[zone]
          outerRadius = reflector_radii[zone+1]
          material = reflector_materials[zone]
          region = reflector_names[zone]
          newassembly = newassembly.replaceMaterials(radius, materials[material], core.getAssemblyCorners(ix+1,core._ny-iy)[0], outerRadius)
      else:
        newassembly = fillAssembly.addRings(reflector_radii, reflector_materials, fill_material, \
            core.getAssemblyCorners(ix+1,core._ny-iy)[0])
      core.setAssembly(ix+1,iy+1,newassembly)
pruneUnusedObjects(core)

if not ldebug:
  core.edit()
else:
  core.edit(False)
