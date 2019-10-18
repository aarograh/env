#!/usr/bin/python2

import sys
import h5py
import numpy as np
import itertools

if len(sys.argv) < 3:
  sys.exit('HDF5 file name, and state index required!')

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
adf = h5[nodalStr + '/ADF'].value
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
      refl_node.append(NORTHEAST)
  # Treat the case where there are 2 fuel nodes
  elif fuel_coremap[iy][ix-1] != 0 and fuel_coremap[iy-1][ix] != 0:
    nrefl += 2
    refl_assem.append(nodal_coremap[iy][ix])
    neigh_assem.append(nodal_coremap[iy][ix-1])
    refl_node.append(SOUTHWEST)
    refl_assem.append(nodal_coremap[iy][ix])
    neigh_assem.append([nodal_coremap[iy][ix-1],nodal_coremap[iy-1][ix]])
    refl_node.append(NORTHWEST)
    # Treat the northeast node of a corner reflector if we're not on the diagonal yet
    if ix != iy:
      nrefl += 1
      refl_assem.append(nodal_coremap[iy][ix])
      neigh_assem.append(nodal_coremap[iy-1][ix])
      refl_node.append(NORTHEAST)
  # Treat the case where there is a fuel assembly to the west, but not the north
  elif fuel_coremap[iy][ix-1] != 0:
    nrefl += 2
    refl_assem.append(nodal_coremap[iy][ix])
    neigh_assem.append(nodal_coremap[iy][ix-1])
    refl_node.append(SOUTHWEST)
    refl_assem.append(nodal_coremap[iy][ix])
    neigh_assem.append(nodal_coremap[iy][ix-1])
    refl_node.append(NORTHWEST)
  # Treat the case where there's a fuel assembly to the north, but not the west
  elif fuel_coremap[iy-1][ix] != 0:
    nrefl += 2
    refl_assem.append(nodal_coremap[iy][ix])
    neigh_assem.append(nodal_coremap[iy-1][ix])
    refl_node.append(NORTHWEST)
    refl_assem.append(nodal_coremap[iy][ix])
    neigh_assem.append(nodal_coremap[iy-1][ix])
    refl_node.append(NORTHEAST)
  # Treat the corner case where there is no fuel assembly neighboring
  else:
    nrefl += 1
    refl_assem.append(nodal_coremap[iy][ix])
    neigh_assem.append([nodal_coremap[iy][ix-1],nodal_coremap[iy-1][ix]])
    refl_node.append(NORTHWEST)

  # If we just treated the nodes on the symmetry line, then we're done
  if ix == iy:
    break

  # Step to the next reflector assembly
  if fuel_coremap[iy-1][ix] != 0:
    ix += 1
  else:
    iy -= 1

# Calculate the effective ADFs for reflectors that neighbor a single fuel node
refl_adfs = []
for irefl in range(nrefl):
  refl_adfs.append([adf[idir-1,:,refl_node[irefl]-1,0,refl_assem[irefl]-1] for idir in [WEST,NORTH,EAST,SOUTH]])

# Print the results
print "Refl. Node          WEST                       NORTH                        EAST                       SOUTH"
print "                 Group 1       Group 2       Group 1       Group 2       Group 1       Group 2       Group 1       Group 2"
for irefl in range(nrefl):
  print "{0:10d}{1:14.6e}{2:14.6e}{3:14.6e}{4:14.6e}{5:14.6e}{6:14.6e}{7:14.6e}{8:14.6e}".format( \
      irefl+1, refl_adfs[irefl][WEST-1][0], refl_adfs[irefl][WEST-1][1], refl_adfs[irefl][NORTH-1][0], refl_adfs[irefl][NORTH-1][1], \
      refl_adfs[irefl][EAST-1][0], refl_adfs[irefl][EAST-1][1], refl_adfs[irefl][SOUTH-1][0], refl_adfs[irefl][SOUTH-1][1] )
