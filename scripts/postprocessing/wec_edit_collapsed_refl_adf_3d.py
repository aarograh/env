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
volumes = h5[nodalStr + '/VOL'].value
coremap = h5['/CORE/core_map'].value
nodal_coremap = h5['/CORE/computational_core_map'].value
sym = h5['/CORE/core_sym'].value
axial_mesh = h5['/CORE/computational_axial_mesh'].value
fuel_axial_mesh = h5['/CORE/axial_mesh'].value

# Set some useful enumerations
WEST = 1
NORTH = 2
EAST = 3
SOUTH = 4
TOP = 5
BOTTOM = 6
ALL_DIRECTIONS = [WEST, EAST, NORTH, SOUTH, TOP, BOTTOM]
DIRECTION_NAMES = ['WEST', 'EAST', 'NORTH', 'SOUTH', 'TOP', 'BOTTOM']
direction_dir = {DIRECTION_NAMES[i]: ALL_DIRECTIONS[i] for i in range(len(ALL_DIRECTIONS))}
NORTHWEST = 1
NORTHEAST = 2
SOUTHWEST = 3
SOUTHEAST = 4

# Find the start and stop fuel planes
for level in range(len(axial_mesh)):
  if np.allclose(fuel_axial_mesh[0], axial_mesh[level]):
    fuelstt = level + 1
  if np.allclose(fuel_axial_mesh[-1], axial_mesh[level]):
    fuelstp = level + 1

def homogenize_axially(volumes, fluxes, level_start, level_stop, XS=None):
  homog_values = fluxes[:,:,0,:]*0.0
  for assem in range(flux.shape[3]):
    for node in range(flux.shape[1]):
      for group in range(flux.shape[0]):
        homog_values[group, node, assem] = 0.0
        flxvolsum = 0.0
        for level in xrange(level_start,level_stop+1):
          flxvol = flux[group, node, level, assem] * volumes[node, level, assem]
          if XS:
            homog_values[group, node, assem] += XS[group, node, level, assem] * flxvol
            flxvolsum += flxvol
          else:
            homog_values[group, node, assem] += flxvol
            flxvolsum += volumes[node, level, assem]
        homog_values[group, node, assem] /= flxvolsum

def homogenize_surface_axially(axial_mesh, values, level_start, level_stop):
  homog_values = values[:,:,:,0,:]*0.0
  for assem in range(values.shape[4]):
    for node in range(values.shape[2]):
      for group in range(values.shape[1]):
        for direction in [WEST, NORTH, EAST, SOUTH]:
          homog_values[direction, group, node, assem] = 0.0
          height_sum = 0.0
          for level in xrange(level_start, level_stop+1):
            homog_values[direction, group,]

# Homogenize bottom reflector
flux_bottom = homogenize_axially(volumes, flux, 0, fuelstt-1)
nxsf_bottom = homogenize_axially(volumes, flux, 0, fuelstt-1, nxsf)
kxsf_bottom = homogenize_axially(volumes, flux, 0, fuelstt-1, kxsf)
xss_bottom = xss[:,:,:,0,:]*0.0
xss_bottom[:,0,:,:] = homogenize_axially(volumes, flux, 0, fuelstt-1, xss[:,0,:,:,:])
xss_bottom[:,1,:,:] = homogenize_axially(volumes, flux, 0, fuelstt-1, xss[:,1,:,:,:])

# Homogenize top reflector
flux_top = homogenize_axially(volumes, flux, fuelstp, len(axial_mesh))
nxsf_top = homogenize_axially(volumes, flux, fuelstp, len(axial_mesh), nxsf)
kxsf_top = homogenize_axially(volumes, flux, fuelstp, len(axial_mesh), kxsf)
xss_top = xss[:,:,:,0,:]*0.0
xss_top[:,0,:,:] = homogenize_axially(volumes, flux, fuelstp, len(axial_mesh), xss[:,0,:,:,:])
xss_top[:,1,:,:] = homogenize_axially(volumes, flux, fuelstp, len(axial_mesh), xss[:,1,:,:,:])

# Reintegrate bottom reflector surface quantities
sflx_bottom = homogenize_surface_axially(axial_mesh, sflx, 0 fuelstt-1)
cur_bottom = homogenize_surface_axially(axial_mesh, cur, 0, fuelstt-1)
sflx_top = homogenize_surface_axially(axial_mesh, sflx, fuelstp, len(axial_mesh))
cur_top = homogenize_surface_axially(axial_mesh, cur, fuelstp, len(axial_mesh))






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

# Collapse the upper and lower axial reflectors into a single plane
#   Set all the fuel planes (which won't be collapsed), along with one plane above and below
anc_adf = adf[:,:,:,fuelstt-2:fuelstp+1,:]
anc_sflx = sflx[:,:,:,fuelstt-2:fuelstp+1,:]
anc_cur = cur[:,:,:,fuelstt-2:fuelstp+1,:]
anc_xsD = xsD[:,:,fuelstt-2:fuelstp+1,:]
anc_xsab = xsab[:,:,fuelstt-2:fuelstp+1,:]
anc_nxsf = nxsf[:,:,fuelstt-2:fuelstp+1,:]
anc_kxsf = kxsf[:,:,fuelstt-2:fuelstp+1,:]
anc_flux = flux[:,:,fuelstt-2:fuelstp+1,:]
anc_xsrm = xsrm[:,fuelstt-2:fuelstp+1,:]

anc_adf[:,:,:,0,:]=0.0
anc_sflx[:,:,:,0,:]=0.0
anc_cur[:,:,:,0,:]=0.0
anc_xsD[:,:,0,:]=0.0
anc_xsab[:,:,0,:]=0.0
anc_nxsf[:,:,0,:]=0.0
anc_kxsf[:,:,0,:]=0.0
anc_flux[:,:,0,:]=0.0
anc_xsrm[:,0,:]=0.0

anc_adf[:,:,:,-1,:]=0.0
anc_sflx[:,:,:,-1,:]=0.0
anc_cur[:,:,:,-1,:]=0.0
anc_xsD[:,:,-1,:]=0.0
anc_xsab[:,:,-1,:]=0.0
anc_nxsf[:,:,-1,:]=0.0
anc_kxsf[:,:,-1,:]=0.0
anc_flux[:,:,-1,:]=0.0
anc_xsrm[:,-1,:]=0.0

radial_dirs = []
for dir in ['WEST','NORTH','EAST','SOUTH']:
  radial_dirs.append(direction_dir[dir])

#   Collapse the lower reflector first
hom_flux = anc_sflx[:,:,:,0,:]*0.0
for level in range(fuelstt):
  delta_z = (axial_mesh[level+1]-axial_mesh[level])
  # Surface quantities
  anc_sflx[radial_dirs,:,:,0,:] += sflx[radial_dirs,:,:,0,:] * delta_z
  anc_cur[radial_dirs,:,:,0,:] += cur[radial_dirs,:,:,0,:] * delta_z
  hom_flux[radial_dirs,:,:,:] += delta_z/adf[radial_dirs,:,:,level,:]
  # Node quantities
  anc_xsD[:,:,0,:] += xsD[:,:,level,:] * delta_z * flux[:,:,level,:]
  anc_xsab[:,:,0,:] += xsab[:,:,level,:] * delta_z * flux[:,:,level,:]
  anc_nxsf[:,:,0,:] += nxsf[:,:,level,:] * delta_z * flux[:,:,level,:]
  anc_kxsf[:,:,0,:] += kxsf[:,:,level,:] * delta_z * flux[:,:,level,:]
  anc_flux[:,:,0,:] += flux[:,:,level,:] * delta_z

delta_z = fuel_axial_mesh[0] - axial_mesh[0]
anc_adf[radial_dirs,:,:,0,:] = anc_sflx[radial_dirs,:,:,0,:] / hom_flux[radial_dirs,:,:,:]
anc_adf[direction_dir['TOP']-1,:,:,0,:] = adf[direction_dir['TOP']-1,:,:,fuelstt-1,:]
anc_adf[direction_dir['BOTTOM']-1,:,:,0,:] = adf[direction_dir['BOTTOM']-1,:,:,0,:]
anc_sflx[radial_dirs,:,:,0,:] /= delta_z
anc_cur[radial_dirs,:,:,0,:] /= delta_z
anc_xsD[:,:,0,:] /= anc_flux[:,:,0,:]
anc_xsab[:,:,0,:] /= anc_flux[:,:,0,:]
anc_nxsf[:,:,0,:] /= anc_flux[:,:,0,:]
anc_kxsf[:,:,0,:] /= anc_flux[:,:,0,:]
anc_flux[:,:,0,:] /= delta_z

#   Now collapse upper reflector
hom_flux[:] = 0.0
for level in xrange(fuelstp,len(axial_mesh)-1):
  delta_z = (axial_mesh[level+1]-axial_mesh[level])
  # Surface quantities
  anc_sflx[radial_dirs,:,:,-1,:] += sflx[radial_dirs,:,:,-1,:] * delta_z
  anc_cur[radial_dirs,:,:,-1,:] += cur[radial_dirs,:,:,-1,:] * delta_z
  hom_flux[radial_dirs,:,:,:] += delta_z/adf[radial_dirs,:,:,level,:]
  # Node quantities
  anc_xsD[:,:,-1,:] += xsD[:,:,level,:] * delta_z * flux[:,:,level,:]
  anc_xsab[:,:,-1,:] += xsab[:,:,level,:] * delta_z * flux[:,:,level,:]
  anc_nxsf[:,:,-1,:] += nxsf[:,:,level,:] * delta_z * flux[:,:,level,:]
  anc_kxsf[:,:,-1,:] += kxsf[:,:,level,:] * delta_z * flux[:,:,level,:]
  anc_flux[:,:,-1,:] += flux[:,:,level,:] * delta_z

delta_z = axial_mesh[-1] - fuel_axial_mesh[-1]
anc_adf[radial_dirs,:,:,-1,:] = anc_sflx[radial_dirs,:,:,-1,:] / hom_flux[radial_dirs,:,:,:]
anc_adf[direction_dir['TOP']-1,:,:,-1,:] = adf[direction_dir['TOP']-1,:,:,fuelstt-1,:]
anc_adf[direction_dir['BOTTOM']-1,:,:,0,:] = adf[direction_dir['BOTTOM']-1,:,:,0,:]
anc_sflx[radial_dirs,:,:,-1,:] /= delta_z
anc_cur[radial_dirs,:,:,-1,:] /= delta_z
anc_xsD[:,:,-1,:] /= anc_flux[:,:,-1,:]
anc_xsab[:,:,-1,:] /= anc_flux[:,:,-1,:]
anc_nxsf[:,:,-1,:] /= anc_flux[:,:,-1,:]
anc_kxsf[:,:,-1,:] /= anc_flux[:,:,-1,:]
anc_flux[:,:,-1,:] /= delta_z

# Print the axial mesh
anc_axial_mesh = [axial_mesh[0]]
for level in range(len(fuel_axial_mesh)):
  anc_axial_mesh.append(fuel_axial_mesh[level])
anc_axial_mesh.append(axial_mesh[-1])
print anc_axial_mesh
print 'AXIAL MESH'
print 'AXIAL  DELTA_Z'
for axial in range(len(anc_axial_mesh)-1):
  print "{0:5d}{1:14.6e}".format(axial+1, anc_axial_mesh[axial+1]-anc_axial_mesh[axial])
print

for name, direction in direction_dir.items():
  print 'DISCONTINUITY FACTORS - ' + str(name) + ' SURFACE'
  print "AXIAL COLUMN   ROW          DF 1          DF 2"
  for axial in range(anc_adf.shape[3]):
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
            print "{0:6d}{1:6d}{2:6d}{3:14.6e}{4:14.6e}".format(axial+1, column, row, anc_adf[direction-1, 0, node, axial, assembly], \
                anc_adf[direction-1, 1, node, axial, assembly])
  print

for name, direction in direction_dir.items():
  print '         SURFACE FLUX - ' + str(name) + ' SURFACE'
  print "AXIAL COLUMN   ROW        FLUX 1        FLUX 2"
  for axial in range(anc_sflx.shape[3]):
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
            print "{0:6d}{1:6d}{2:6d}{3:14.6e}{4:14.6e}".format(axial+1, column, row, anc_sflx[direction-1, 0, node, axial, assembly], \
                anc_sflx[direction-1, 1, node, axial, assembly])
  print

for name, direction in direction_dir.items():
  print 'SURFACE CURRENTS      - ' + str(name) + ' SURFACE'
  print "AXIAL COLUMN   ROW     CURRENT 1     CURRENT 2"
  for axial in range(anc_cur.shape[3]):
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
            print "{0:6d}{1:6d}{2:6d}{3:14.6e}{4:14.6e}".format(axial+1, column, row, anc_cur[direction-1, 0, node, axial, assembly], \
                anc_cur[direction-1, 1, node, axial, assembly])
  print

for (dataset, name) in zip([anc_xsD, anc_xsab, anc_nxsf, anc_kxsf, anc_flux], \
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
