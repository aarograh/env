#!/usr/bin/python2

import sys
import h5py
import numpy as np
import itertools
import copy

if len(sys.argv) < 3:
  sys.exit('HDF5 file name and state index required!')

# Open the file
h5 = h5py.File(sys.argv[1])

# Check for existence of nodal data
state = int(sys.argv[2])
stateStr = '/STATE_' + str(state).zfill(4)
nodalStr = stateStr + '/NODAL_XS'
if not stateStr in h5:
  sys.exit(stateStr + ' not found in HDF5 file!')
elif not nodalStr in h5:
  sys.exit(nodalStr + ' not found in HDF5 file!')

# Read HDF5 datasets
keff = h5[stateStr + '/keff'].value
adf = h5[nodalStr + '/ADF'].value
sflx = h5[nodalStr + '/SFLX'].value
cur = h5[nodalStr + '/CUR'].value
flux = h5[nodalStr + '/FLUX'].value
xss = h5[nodalStr + '/XSS'].value
nxsf = h5[nodalStr + '/NXSF'].value
kxsf = h5[nodalStr + '/KXSF'].value
coremap = h5['/CORE/core_map'].value
nodal_coremap = h5['/CORE/computational_core_map'].value
sym = h5['/CORE/core_sym'].value
axial_mesh = h5[nodalStr + '/AXIALMESH'].value
#axial_mesh = h5['/CORE/computational_axial_mesh'].value

# Calculate the absorption XS
xsab = copy.deepcopy(h5[nodalStr + '/XSRM'].value)
xsab[0, :, :, :] -= xss[0, 1, :, :, :]
xsab[1, :, :, :] -= xss[1, 0, :, :, :]

# Calculate the removal XS and diffusion coefficient
xsD = 3.0*h5[nodalStr + '/XSTR'].value
xsrm = copy.deepcopy(xss[0,1,:,:,:])
for assem in range(flux.shape[3]):
  for level in range(flux.shape[2]):
    for node in range(flux.shape[1]):
      if flux[0,node,level,assem] == 0.0:
        xsrm[node,level,assem] = 0.0
      else:
        xsrm[node,level,assem] -= xss[1,0,node,level,assem]*flux[1,node,level,assem]/flux[0,node,level,assem]
      for ig in range(xsD.shape[0]):
        if xsD[ig,node,level,assem] != 0.0:
          xsD[ig,node,level,assem] = 1.0/xsD[ig,node,level,assem]

# Set up some more core maps for internal use
nx = len(coremap[0])
ny = len(coremap)
if sym == 4:
  coremap = coremap[ny/2:,nx/2:]
nx = len(coremap[0])
ny = len(coremap)

fuel_coremap = nodal_coremap*0
for iy in range(ny):
  for ix in range(nx):
    if coremap[iy,ix] != 0:
      fuel_coremap[iy,ix] = nodal_coremap[iy,ix]

# Print the axial mesh
print 'AXIAL MESH'
print 'AXIAL  DELTA_Z'
for axial in range(len(axial_mesh)-1):
  print "{0:5d}{1:14.6e}".format(axial+1, axial_mesh[axial+1]-axial_mesh[axial])
print

# Set some useful enumerations
WEST = 1
NORTH = 2
EAST = 3
SOUTH = 4
TOP = 5
BOTTOM = 6
ALL_DIRECTIONS = [WEST, EAST, NORTH, SOUTH, TOP, BOTTOM]
DIRECTION_NAMES = ['WEST', 'EAST', 'NORTH', 'SOUTH', 'TOP', 'BOTTOM']
NORTHWEST = 1
NORTHEAST = 2
SOUTHWEST = 3
SOUTHEAST = 4

for (direction, name) in zip(ALL_DIRECTIONS, DIRECTION_NAMES):
  print 'DISCONTINUITY FACTORS - ' + str(name) + ' SURFACE'
  print "AXIAL COLUMN   ROW          DF 1          DF 2"
  for axial in range(adf.shape[3]):
    column = 0
    for iy in range(coremap.shape[1]):
      for side in [0, 1]:
        if iy == 0 and side == 0 and sym == 4:
          continue
        column += 1
        row = 0
        for ix in range(coremap.shape[0]):
          if coremap[ix,iy] == 0:
            continue
          assembly = nodal_coremap[ix,iy]-1
          for level in [NORTHWEST+side, SOUTHWEST+side]:
            if ix == 0 and level == NORTHWEST+side and sym == 4:
              continue
            row += 1
            node = level-1
            print "{0:6d}{1:6d}{2:6d}{3:14.6e}{4:14.6e}".format(axial+1, column, row, adf[direction-1, 0, node, axial, assembly], \
                adf[direction-1, 1, node, axial, assembly])
  print

for (direction, name) in zip(ALL_DIRECTIONS, DIRECTION_NAMES):
  print '         SURFACE FLUX - ' + str(name) + ' SURFACE'
  print "AXIAL COLUMN   ROW        FLUX 1        FLUX 2"
  for axial in range(sflx.shape[3]):
    column = 0
    for iy in range(coremap.shape[1]):
      for side in [0, 1]:
        if iy == 0 and side == 0 and sym == 4:
          continue
        column += 1
        row = 0
        for ix in range(coremap.shape[0]):
          if coremap[ix,iy] == 0:
            continue
          assembly = nodal_coremap[ix,iy]-1
          for level in [NORTHWEST+side, SOUTHWEST+side]:
            if ix == 0 and level == NORTHWEST+side and sym == 4:
              continue
            row += 1
            node = level-1
            print "{0:6d}{1:6d}{2:6d}{3:14.6e}{4:14.6e}".format(axial+1, column, row, sflx[direction-1, 0, node, axial, assembly], \
                sflx[direction-1, 1, node, axial, assembly])
  print

for (direction, name) in zip(ALL_DIRECTIONS, DIRECTION_NAMES):
  print 'SURFACE CURRENTS      - ' + str(name) + ' SURFACE'
  print "AXIAL COLUMN   ROW     CURRENT 1     CURRENT 2"
  for axial in range(cur.shape[3]):
    column = 0
    for iy in range(coremap.shape[1]):
      for side in [0, 1]:
        if iy == 0 and side == 0 and sym == 4:
          continue
        column += 1
        row = 0
        for ix in range(coremap.shape[0]):
          if coremap[ix,iy] == 0:
            continue
          assembly = nodal_coremap[ix,iy]-1
          for level in [NORTHWEST+side, SOUTHWEST+side]:
            if ix == 0 and level == NORTHWEST+side and sym == 4:
              continue
            row += 1
            node = level-1
            print "{0:6d}{1:6d}{2:6d}{3:14.6e}{4:14.6e}".format(axial+1, column, row, cur[direction-1, 0, node, axial, assembly], \
                cur[direction-1, 1, node, axial, assembly])
  print

for (dataset, name) in zip([xsD, xsab, nxsf, kxsf, flux], \
    ['DIFFUSION COEFFICIENT', 'ABSORPTION XS', 'NU-FISSION XS', 'KAPPA-FISSION XS', 'AVERAGE FLUX']):
  print name
  print "AXIAL COLUMN   ROW             1             2"
  for axial in range(dataset.shape[2]):
    column = 0
    for iy in range(coremap.shape[1]):
      for side in [0,1]:
        if iy == 0 and side == 0 and sym == 4:
          continue
        column += 1
        row = 0
        for ix in range(coremap.shape[0]):
          if coremap[ix,iy] == 0:
            continue
          assembly = nodal_coremap[ix,iy]-1
          for level in [NORTHWEST+side, SOUTHWEST+side]:
            if ix == 0 and level == NORTHWEST+side and sym == 4:
              continue
            row += 1
            node = level-1
            print "{0:6d}{1:6d}{2:6d}{3:14.6e}{4:14.6e}".format(axial+1, column, row, dataset[0, node, axial, assembly], \
                dataset[1, node, axial, assembly])
  print

print 'REMOVAL XS'
print "AXIAL COLUMN"
for axial in range(xsrm.shape[1]):
  column = 0
  for iy in range(coremap.shape[1]):
    for side in [0,1]:
      if iy == 0 and side == 0 and sym == 4:
        continue
      column += 1
      row_data = []
      for ix in range(coremap.shape[0]):
        if coremap[ix,iy] == 0:
          continue
        assembly = nodal_coremap[ix,iy]-1
        for level in [NORTHWEST+side, SOUTHWEST+side]:
          if ix == 0 and level == NORTHWEST+side and sym == 4:
            continue
          node = level-1
          row_data.append(xsrm[node, axial, assembly])
      if len(row_data) > 0:
        print "{0:6d}{1:6d}".format(axial+1, column) + ''.join("{0:14.6e}".format(value) for value in row_data)
print

print 'K-EFF = {0:6f}'.format(keff)
