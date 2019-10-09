#!/usr/bin/python2

import sys
import h5py
import numpy as np
import itertools

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
flux = h5[nodalStr + '/FLUX'].value
xstr = h5[nodalStr + '/XSTR'].value
xsrm = h5[nodalStr + '/XSRM'].value
xss = h5[nodalStr + '/XSS'].value
coremap = h5['/CORE/core_map'][...]
nodal_coremap = h5['/CORE/computational_core_map'][...]
sym = h5['/CORE/core_sym'][...]

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
def calcStandardADF_1neigh(reflassem, refldir, reflnode):
  return adf[refldir-1,:,reflnode-1,0,reflassem-1]

# This function calculates the standard ADF for a reflector node with 0 or 2 neighboring fuel assemblies
def calcStandardADF_2neigh(reflassem, refldir):
  reflnode = NORTHWEST
  adf_eff = [0.0, 0.0]
  for dir in refldir:
    adf_eff += adf[dir-1,:,reflnode-1,0,reflassem-1]
  return adf_eff/len(refldir)

# This function calculates the effective ADF for a reflector node with 1 neighboring fuel assembly
def calcEffectiveADF_1neigh(reflassem, fuelassem, refldir, reflnode):
  return adf[refldir-1,:,reflnode-1,0,reflassem-1]\
           /adf[periodicDir(refldir)-1,:,neighborNode(reflnode,refldir)-1,0,fuelassem-1]

# This function calculates the effective ADF for a reflector node with 0 or 2 neighboring fuel assemblies
def calcEffectiveADF_2neigh(reflassem, neighassem, refldir, norm):
  reflnode = NORTHWEST
  adf_eff = norm*0.0
  for (dir, neigh) in zip(refldir, neighassem):
    adf_eff += adf[dir-1,:,reflnode-1,0,reflassem-1]/adf[periodicDir(dir)-1,:,neighborNode(reflnode,dir)-1,0,neigh-1]
  return adf_eff/norm

# Calculate the effective ADFs for reflectors that neighbor a single fuel node
refl_adfs = []
if method == EFFECTIVE_ADFS:
  for irefl in range(nrefl):
    if isinstance(neigh_assem[irefl], list) or neigh_assem[irefl] == 0:
      refl_adfs.append(0.0)
    else:
      refl_adfs.append(calcEffectiveADF_1neigh( \
          refl_assem[irefl], neigh_assem[irefl], refl_surf_dir[irefl], refl_node[irefl]))
elif method == STANDARD_ADFS:
  for irefl in range(nrefl):
    if isinstance(neigh_assem[irefl], list) or neigh_assem[irefl] == 0:
      refl_adfs.append(calcStandardADF_2neigh(refl_assem[irefl],refl_surf_dir[irefl]))
    else:
      refl_adfs.append(calcStandardADF_1neigh(refl_assem[irefl],refl_surf_dir[irefl],refl_node[irefl]))

# Now calculate effective ADFs for reflectors that are at corners and have 2 neighbors
if method == EFFECTIVE_ADFS:
  for irefl in range(nrefl):
    if isinstance(neigh_assem[irefl], list):
      if neigh_assem[irefl][0] in fuel_coremap:
        norm = 2.0
      else:
        norm = refl_adfs[irefl+1] + refl_adfs[irefl-1]
      refl_adfs[irefl] = (calcEffectiveADF_2neigh( \
          refl_assem[irefl], neigh_assem[irefl], refl_surf_dir[irefl], norm))


# Calculate the absorption cross section - xsA = xsR - sum(out-scatter)
# Store xstr, xsrm, and scattering for reflector cross sections at the same time
# Also get the node-averaged fluxes
refl_trans = []
refl_abs = []
refl_scat = []
refl_flux = []
for (iassem, inode) in zip(refl_assem, refl_node):
  refl_scat.append(xss[:,:,inode-1,0,iassem-1])
  refl_trans.append(xstr[:,inode-1,0,iassem-1])
  refl_abs.append([xsrm[0,inode-1,0,iassem-1] - xss[0,1,inode-1,0,iassem-1], \
                   xsrm[1,inode-1,0,iassem-1] - xss[1,0,inode-1,0,iassem-1]])
  refl_flux.append(flux[:,inode-1,0,iassem-1])


# Print the results
print "Refl. Node         ADF 1         ADF 2   TRANSPORT 1   TRANSPORT 2  ABSORPTION 1  ABSORPTION 2   SCATTER 1>1   SCATTER 1>2   SCATTER 2>1   SCATTER 2>2        FLUX 1        FLUX 2"
for irefl in range(nrefl):
  print "{0:10d}{1:14.6e}{2:14.6e}{3:14.6e}{4:14.6e}{5:14.6e}{6:14.6e}{7:14.6e}{8:14.6e}{9:14.6e}{10:14.6e}{11:14.6e}{12:14.6e}".format( \
    irefl+1, refl_adfs[irefl][0], refl_adfs[irefl][1], refl_trans[irefl][0] , refl_trans[irefl][1], \
    refl_abs[irefl][0], refl_abs[irefl][1], refl_scat[irefl][0,0], refl_scat[irefl][0,1], \
    refl_scat[irefl][1,0], refl_scat[irefl][1,1], refl_flux[irefl][0], refl_flux[irefl][1])
