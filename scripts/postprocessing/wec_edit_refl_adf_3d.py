#!/usr/bin/python2

import sys
import h5py
import numpy as np
import itertools
import copy

if len(sys.argv) < 4:
  sys.exit('ADF method, HDF5 file name, and state index required!')

STANDARD_ADFS = 1
EFFECTIVE_ADFS = 2

# Get the method
if sys.argv[1] == 'standard':
  method = STANDARD_ADFS
elif sys.argv[1] == 'effective':
  method = EFFECTIVE_ADFS
else:
  sys.exit('Unrecognized ADF method.  Method must be "standard" or "effective".')

# Open the file
h5 = h5py.File(sys.argv[2])

# Check for existence of nodal data
state = int(sys.argv[3])
stateStr = '/STATE_' + str(state).zfill(4)
nodalStr = stateStr + '/NODAL_XS'
if not stateStr in h5:
  sys.exit(stateStr + ' not found in HDF5 file!')
elif not nodalStr in h5:
  sys.exit(nodalStr + ' not found in HDF5 file!')

# Read HDF5 datasets
adf = h5[nodalStr + '/ADF'].value
sflx = h5[nodalStr + '/SFLX'].value
for (i, j, k, m, n), value in np.ndenumerate(adf):
  if value == 0.0 or np.allclose(sflx[i,j,k,m,n], 0.0):
    sflx[i,j,k,m,n] = 0.0
  else:
    sflx[i,j,k,m,n] /= value
flux = h5[nodalStr + '/FLUX'].value
xstr = h5[nodalStr + '/XSTR'].value
xsrm = h5[nodalStr + '/XSRM'].value
xss = h5[nodalStr + '/XSS'].value
coremap = h5['/CORE/core_map'].value
nodal_coremap = h5['/CORE/computational_core_map'].value
sym = h5['/CORE/core_sym'].value
axial_mesh = h5['/CORE/axial_mesh'].value
computational_axial_mesh = h5[nodalStr + '/AXIALMESH'].value

#Don't handle full core stuff right now
if sym != 4:
  sys.exit('Only quarter core calculations are supported!')

# Set up some more core maps for internal use
nx = len(coremap[0])
ny = len(coremap)
coremap = coremap[ny/2:,nx/2:]
nx = len(coremap[0])
ny = len(coremap)

nx_nodal = len(nodal_coremap[0])
ny_nodal = len(nodal_coremap)
if sym == 1:
  nodal_coremap = nodal_coremap[ny_nodal/2,nx_nodal/2:]

fuel_coremap = nodal_coremap*0
for iy in range(ny):
  for ix in range(nx):
    if coremap[iy,ix] != 0:
      fuel_coremap[iy,ix] = nodal_coremap[iy,ix]

# Identify the range of fuel planes in the computational axial mesh
fuel_min = 0
fuel_max = len(computational_axial_mesh)
for axial in range(len(computational_axial_mesh)):
  if computational_axial_mesh[axial] >= axial_mesh[0]-1.0e-4:
    break
  else:
    fuel_min += 1
for axial in reversed(range(len(computational_axial_mesh))):
  fuel_max -= 1
  if computational_axial_mesh[axial] <= axial_mesh[-1]+1.0e-4:
    break

# Set some useful enumerations
WEST = 1
NORTH = 2
EAST = 3
SOUTH = 4
NORTHWEST = 1
NORTHEAST = 2
SOUTHWEST = 3
SOUTHEAST = 4

# Initialize lists
ix = 0
iy = len(nodal_coremap)-1
nrefl = 0
refl_assem = []
neigh_assem = []
refl_surf_dir = []
refl_node = []

# We want to store indexing data for the reflector nodes.  The nodes are
# indexed (in quarter symmetry) from the southwest corner of the problem
# counterclockwise to the line of symmetry.
while True:
  # Treat the first node specially
  if ix == 0:
    if sym == 4:
      nrefl += 1
      refl_assem.append(nodal_coremap[iy][ix])
      neigh_assem.append(nodal_coremap[iy-1][ix])
      refl_surf_dir.append(NORTH)
      refl_node.append(NORTHEAST)
  # Treat the case where there are 2 fuel nodes
  elif fuel_coremap[iy][ix-1] != 0 and fuel_coremap[iy-1][ix] != 0:
    nrefl += 2
    refl_assem.append(nodal_coremap[iy][ix])
    neigh_assem.append(nodal_coremap[iy][ix-1])
    refl_surf_dir.append(WEST)
    refl_node.append(SOUTHWEST)
    refl_assem.append(nodal_coremap[iy][ix])
    neigh_assem.append([nodal_coremap[iy][ix-1],nodal_coremap[iy-1][ix]])
    refl_surf_dir.append([WEST,NORTH])
    refl_node.append(NORTHWEST)
    # Treat the northeast node of a corner reflector if we're not on the diagonal yet
    if ix != iy:
      nrefl += 1
      refl_assem.append(nodal_coremap[iy][ix])
      neigh_assem.append(nodal_coremap[iy-1][ix])
      refl_surf_dir.append(NORTH)
      refl_node.append(NORTHEAST)
  # Treat the case where there is a fuel assembly to the west, but not the north
  elif fuel_coremap[iy][ix-1] != 0:
    nrefl += 2
    refl_assem.append(nodal_coremap[iy][ix])
    neigh_assem.append(nodal_coremap[iy][ix-1])
    refl_surf_dir.append(WEST)
    refl_node.append(SOUTHWEST)
    refl_assem.append(nodal_coremap[iy][ix])
    neigh_assem.append(nodal_coremap[iy][ix-1])
    refl_surf_dir.append(WEST)
    refl_node.append(NORTHWEST)
  # Treat the case where there's a fuel assembly to the north, but not the west
  elif fuel_coremap[iy-1][ix] != 0:
    nrefl += 2
    refl_assem.append(nodal_coremap[iy][ix])
    neigh_assem.append(nodal_coremap[iy-1][ix])
    refl_surf_dir.append(NORTH)
    refl_node.append(NORTHWEST)
    refl_assem.append(nodal_coremap[iy][ix])
    neigh_assem.append(nodal_coremap[iy-1][ix])
    refl_surf_dir.append(NORTH)
    refl_node.append(NORTHEAST)
  # Treat the corner case where there is no fuel assembly neighboring
  else:
    nrefl += 1
    refl_assem.append(nodal_coremap[iy][ix])
    neigh_assem.append([nodal_coremap[iy][ix-1],nodal_coremap[iy-1][ix]])
    refl_surf_dir.append([WEST,NORTH])
    refl_node.append(NORTHWEST)

  # If we just treated the nodes on the symmetry line, then we're done
  if ix == iy:
    break

  # Step to the next reflector assembly
  if fuel_coremap[iy-1][ix] != 0:
    ix += 1
  else:
    iy -= 1

# This function returns the periodic direction given an input direction
def periodicDir(dir):
  if dir == WEST:
    return EAST
  if dir == NORTH:
    return SOUTH
  if dir == EAST:
    return WEST
  if dir == SOUTH:
    return NORTH

# This function returns the neighoring node given a node index and direction
def neighborNode(node,dir):
  if node == NORTHWEST:
    if dir == NORTH:
      return SOUTHWEST
    else:
      return NORTHEAST
  if node == NORTHEAST:
    if dir == NORTH:
      return SOUTHEAST
    else:
      return NORTHWEST
  if node == SOUTHWEST:
    if dir == SOUTH:
      return NORTHWEST
    else:
      return SOUTHEAST
  if node == SOUTHEAST:
    if dir == SOUTH:
      return NORTHEAST
    else:
      return SOUTHWEST

# T?his function calculates the standard ADF for a reflector node with 1 neighboring fuel assembly
def calcStandardADF_1neigh(reflassem, refldir, reflnode, axial, weight=None):
  n = len(adf[refldir-1,:,reflnode-1,axial,reflassem-1])
  tmpweight = [1.0 if weight is None else weight[refldir-1,i,reflnode-1,axial,reflassem-1] for i in range(n)]
  return adf[refldir-1,:,reflnode-1,axial,reflassem-1]*tmpweight[:]

# This function calculates the standard ADF for a reflector node with 0 or 2 neighboring fuel assemblies
def calcStandardADF_2neigh(reflassem, refldir, axial, weight=None):
  reflnode = NORTHWEST
  adf_eff = [0.0, 0.0]
  n = len(adf[refldir[0]-1,:,reflnode-1,axial,reflassem-1])
  for dir in refldir:
    tmpweight = [1.0 if weight is None else weight[dir-1,i,reflnode-1,axial,reflassem-1] for i in range(n)]
    adf_eff += adf[dir-1,:,reflnode-1,axial,reflassem-1]*tmpweight[:]
  return adf_eff/len(refldir)

# This function calculates the effective ADF for a reflector node with 1 neighboring fuel assembly
def calcEffectiveADF_1neigh(reflassem, fuelassem, refldir, reflnode, axial, weight=None):
  n = len(adf[refldir-1,:,reflnode-1,axial,reflassem-1])
  tmpweight1 = [1.0 if weight is None else weight[refldir-1,i,reflnode-1,axial,reflassem-1] for i in range(n)]
  tmpweight2 = [1.0 if weight is None else weight[periodicDir(refldir)-1,i,neighborNode(reflnode,refldir)-1,axial,fuelassem-1] for i in range(n)]
  return adf[refldir-1,:,reflnode-1,axial,reflassem-1]*tmpweight1[:]\
           /(adf[periodicDir(refldir)-1,:,neighborNode(reflnode,refldir)-1,axial,fuelassem-1]*tmpweight2)

# This function calculates the effective ADF for a reflector node with 0 or 2 neighboring fuel assemblies
def calcEffectiveADF_2neigh(reflassem, neighassem, refldir, norm, axial, weight=None):
  reflnode = NORTHWEST
  adf_eff = norm*0.0
  n = len(adf[refldir[0],:,reflnode-1,axial,reflassem-1])
  for (dir, neigh) in zip(refldir, neighassem):
    tmpweight1 = [1.0 if weight is None else weight[dir-1,i,reflnode-1,axial,reflassem-1] for i in range(n)]
    tmpweight2 = [1.0 if weight is None else weight[periodicDir(dir)-1,i,neighborNode(reflnode,dir)-1,axial,neigh-1] for i in range(n)]
    adf_eff += adf[dir-1,:,reflnode-1,axial,reflassem-1]*tmpweight1[:]\
        /(adf[periodicDir(dir)-1,:,neighborNode(reflnode,dir)-1,axial,neigh-1]*tmpweight2[:])
  return adf_eff/norm

# Calculate the plane thicknesses and midpoints
midpoint = []
dz = []
for axial in xrange(fuel_min,fuel_max):
  dz.append(computational_axial_mesh[axial+1]-computational_axial_mesh[axial])
  midpoint.append(0.5*(computational_axial_mesh[axial+1]+computational_axial_mesh[axial]))

# Initialize empty lists
refl_adfs = []
refl_sflx = []
refl_trans = []
refl_abs = []
refl_scat = []
refl_flux = []
refl_adfs_avg = []
refl_sflx_avg = []
for axial in xrange(fuel_min,fuel_max):
  refl_adfs.append([])
  refl_sflx.append([])
  refl_scat.append([])
  refl_trans.append([])
  refl_abs.append([])
  refl_flux.append([])

# Calculate the height-weight surface fluxes
sflxdz = copy.deepcopy(sflx[:,:,:,:,:])
for axial in xrange(fuel_min,fuel_max):
  sflxdz[:,:,:,axial,:] *= dz[axial-fuel_min]

# Calculate ADFs
for irefl in range(nrefl):
  # Set indexes
  iassem = refl_assem[irefl]
  inode = refl_node[irefl]
  ineighassem = neigh_assem[irefl]
  idir = refl_surf_dir[irefl]

  # Calculate the effective ADFs for reflectors that neighbor a single fuel node, or
  # standard ADFs for all reflectors
  for axial in xrange(fuel_min,fuel_max):
    if method == EFFECTIVE_ADFS:
      if isinstance(idir, list):
        refl_adfs[axial-fuel_min].append(0.0)
      else:
        refl_adfs[axial-fuel_min].append(calcEffectiveADF_1neigh(iassem, ineighassem, idir, inode, axial))
    elif method == STANDARD_ADFS:
      if isinstance(idir, list):
        tmp = calcStandardADF_2neigh(iassem,idir, axial)
        refl_adfs[axial-fuel_min].append(tmp)
      else:
        refl_adfs[axial-fuel_min].append(calcStandardADF_1neigh(iassem,idir,inode, axial))

    # Calculate the surface fluxes
    if isinstance(idir, list):
      refl_sflx[axial-fuel_min].append([0.0 for i in range(len(sflx[0,:,0,0,0]))])
      for dir in idir:
        refl_sflx[axial-fuel_min][-1] += sflx[dir-1,:,inode-1,axial,iassem-1]
      refl_sflx[axial-fuel_min][-1] /= len(idir)
    else:
      refl_sflx[axial-fuel_min].append(sflx[idir-1,:,inode-1,axial,iassem-1])

# Now calculate effective ADFs for reflectors that are at corners and have 2 neighbors
if method == EFFECTIVE_ADFS:
  for irefl in range(nrefl):
    if isinstance(ineighassem, list):
      if ineighassem[0] in fuel_coremap:
        norm = 2.0
        snorm = 2.0
      else:
        norm = refl_adfs[axial-fuel_min][irefl+1] + refl_adfs[axial-fuel_min][irefl-1]
        snorm = norm #TODO
      for axial in xrange(fuel_min,fuel_max):
        refl_adfs[axial-fuel_min][irefl] = (calcEffectiveADF_2neigh(iassem, ineighassem, idir, norm, axial))

# Calculate average ADFs and surface fluxes
for irefl in range(nrefl):
  # Set indexes
  iassem = refl_assem[irefl]
  inode = refl_node[irefl]
  ineighassem = neigh_assem[irefl]
  idir = refl_surf_dir[irefl]

  # Extend lengths
  refl_adfs_avg.append([0.0 for group in range(len(adf[0,:,0,0,0]))])
  refl_sflx_avg.append([0.0 for group in range(len(sflx[0,:,0,0,0]))])

  # Tally the surface flux * dz
  for axial in xrange(fuel_min,fuel_max):
    if isinstance(idir, list):
      for dir in idir:
        refl_sflx_avg[irefl] += sflxdz[dir-1,:,inode-1,axial,iassem-1]/len(idir)
    else:
      refl_sflx_avg[irefl] += sflxdz[idir-1,:,inode-1,axial,iassem-1]

  # Tally ADF * surface flux * dz
  for axial in xrange(fuel_min,fuel_max):
    if isinstance(idir, list):
      for dir in idir:
        refl_adfs_avg[irefl] += refl_adfs[axial-fuel_min][irefl]*sflxdz[dir-1,:,inode-1,axial,iassem-1]/len(idir)
    else:
      refl_adfs_avg[irefl] += refl_adfs[axial-fuel_min][irefl]*sflxdz[idir-1,:,inode-1,axial,iassem-1]

  # Normalize ADFs by surface flux * dz, and surface flux by dz
  refl_adfs_avg[irefl] /= refl_sflx_avg[irefl]
  refl_sflx_avg[irefl] /= sum(dz)

# Calculate the absorption cross section - xsA = xsR - sum(out-scatter)
# Store xstr, xsrm, and scattering for reflector cross sections at the same time
# Also get the node-averaged fluxes
for (iassem, inode) in zip(refl_assem, refl_node):
  for axial in xrange(fuel_min,fuel_max):
    refl_scat[axial-fuel_min].append(xss[:,:,inode-1,axial,iassem-1])
    refl_trans[axial-fuel_min].append(xstr[:,inode-1,axial,iassem-1])
    refl_abs[axial-fuel_min].append([xsrm[0,inode-1,axial,iassem-1] - xss[0,1,inode-1,axial,iassem-1], \
                     xsrm[1,inode-1,axial,iassem-1] - xss[1,0,inode-1,axial,iassem-1]])
    refl_flux[axial-fuel_min].append(flux[:,inode-1,axial,iassem-1])

def calcAxialAverage(data, height, weight=None):
  if weight:
    return sum([data[axial]*height[axial]*weight[axial] for axial in range(len(data))])/ \
        sum([height[axial]*weight[axial] for axial in range(len(data))])
  else:
    return sum([data[axial]*height[axial] for axial in range(len(data))])/sum(height)

# Calculate averages
refl_trans_avg = []
refl_abs_avg = []
refl_scat_avg = []
refl_flux_avg = []
for irefl in range(nrefl):
  # Set indexes
  iassem = refl_assem[irefl]
  inode = refl_node[irefl]

  # Prepare some temporary lists
  tmpflux = []
  tmpflux.append([refl_flux[axial][irefl][0] for axial in range(fuel_max-fuel_min)])
  tmpflux.append([refl_flux[axial][irefl][1] for axial in range(fuel_max-fuel_min)])
  tmpsflx = []
  tmpsflx.append([refl_sflx[axial][irefl][0] for axial in range(fuel_max-fuel_min)])
  tmpsflx.append([refl_sflx[axial][irefl][1] for axial in range(fuel_max-fuel_min)])

  # Calculate averages
  refl_trans_avg.append( [ \
      calcAxialAverage([refl_trans[axial][irefl][0] for axial in range(fuel_max-fuel_min)], dz, weight=tmpflux[0]), \
      calcAxialAverage([refl_trans[axial][irefl][1] for axial in range(fuel_max-fuel_min)], dz, weight=tmpflux[1])])
  refl_abs_avg.append( [ \
      calcAxialAverage([refl_abs[axial][irefl][0] for axial in range(fuel_max-fuel_min)], dz, weight=tmpflux[0]), \
      calcAxialAverage([refl_abs[axial][irefl][1] for axial in range(fuel_max-fuel_min)], dz, weight=tmpflux[1])])
  refl_scat_avg.append( [[ \
      calcAxialAverage([refl_scat[axial][irefl][0,0] for axial in range(fuel_max-fuel_min)], dz, weight=tmpflux[0]), \
      calcAxialAverage([refl_scat[axial][irefl][0,1] for axial in range(fuel_max-fuel_min)], dz, weight=tmpflux[0])], [\
      calcAxialAverage([refl_scat[axial][irefl][1,0] for axial in range(fuel_max-fuel_min)], dz, weight=tmpflux[1]), \
      calcAxialAverage([refl_scat[axial][irefl][1,1] for axial in range(fuel_max-fuel_min)], dz, weight=tmpflux[1])]])
  refl_flux_avg.append([calcAxialAverage(tmpflux[0], dz), calcAxialAverage(tmpflux[1], dz)])

for irefl in range(nrefl):
  print "Reflector Node " + str(irefl+1)
  print " Axial Level      Midpoint        DeltaZ         ADF 1         ADF 2   TRANSPORT 1   TRANSPORT 2  ABSORPTION 1  ABSORPTION 2   SCATTER 1>1   SCATTER 1>2   SCATTER 2>1   SCATTER 2>2        FLUX 1        FLUX 2  SURF. FLUX 1  SURF. FLUX 2"
  for axial in xrange(fuel_min,fuel_max):
    print "{1:12d}{2:14.6e}{3:14.6e}{4:14.6e}{5:14.6e}{6:14.6e}{7:14.6e}{8:14.6e}{9:14.6e}{10:14.6e}{11:14.6e}{12:14.6e}{13:14.6e}{14:14.6e}{15:14.6e}{16:14.6e}{17:14.6e}".format( \
      irefl+1, axial-fuel_min+1, midpoint[axial-fuel_min], dz[axial-fuel_min], \
      refl_adfs[axial-fuel_min][irefl][0], refl_adfs[axial-fuel_min][irefl][1], \
      refl_trans[axial-fuel_min][irefl][0] , refl_trans[axial-fuel_min][irefl][1], \
      refl_abs[axial-fuel_min][irefl][0], refl_abs[axial-fuel_min][irefl][1], \
      refl_scat[axial-fuel_min][irefl][0,0], refl_scat[axial-fuel_min][irefl][0,1], \
      refl_scat[axial-fuel_min][irefl][1,0], refl_scat[axial-fuel_min][irefl][1,1], \
      refl_flux[axial-fuel_min][irefl][0], refl_flux[axial-fuel_min][irefl][1], \
      refl_sflx[axial-fuel_min][irefl][0], refl_sflx[axial-fuel_min][irefl][1])
  # print '-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'
  print "     Average  ------------  ------------{0:14.6e}{1:14.6e}{2:14.6e}{3:14.6e}{4:14.6e}{5:14.6e}{6:14.6e}{7:14.6e}{8:14.6e}{9:14.6e}{10:14.6e}{11:14.6e}{12:14.6e}{13:14.6e}".format( \
    refl_adfs_avg[irefl][0], refl_adfs_avg[irefl][1], \
    refl_trans_avg[irefl][0], refl_trans_avg[irefl][1], \
    refl_abs_avg[irefl][0], refl_abs_avg[irefl][1], \
    refl_scat_avg[irefl][0][0], refl_scat_avg[irefl][0][1], \
    refl_scat_avg[irefl][1][0], refl_scat_avg[irefl][1][1], \
    refl_flux_avg[irefl][0], refl_flux_avg[irefl][1], \
    refl_sflx_avg[irefl][0], refl_sflx_avg[irefl][1])
  print