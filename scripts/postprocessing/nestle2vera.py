#!/usr/bin/python2

import sys
import h5py
import numpy as np
import pylab as plt

if len(sys.argv) > 2:
  text = open(sys.argv[1])
  h5 = h5py.File(sys.argv[2])
  if len(sys.argv) > 3:
    istate = int(sys.argv[3])
  else:
    istate = 1
else:
  sys.exit("Usage: 'nestle2vera.py <nestle text file> <vera hdf5 file>")

def readnodexy(line):
  return int(line[29:31]), int(line[33:35])

def readz(line):
  return int(line.split()[3])

# Assume a quarter core for now
# Returns the quadrant (1 to 4) given the x and y node positions (1-based index)
def xy2iquad(inodex, inodey):
  if np.mod(inodey,2) == 1:
    iquad = 3
  else:
    iquad = 1
  if np.mod(inodex,2) == 1:
    iquad += 1
  return iquad

# Assume quarter core for now
# Returns the assembly x and y positions given node x and y positions (1-based index)
def xy2iassemxy(inodex, inodey):
  return 7+(inodex+1)/2+np.mod(inodex+1,2), 7+(inodey+1)/2+np.mod(inodey+1,2)

# Returns the pin start and top x and y positions for a quadrant (1-based index)
def iquad2pinxy(iquad):
  if iquad == 1:
    return 1, 9, 1, 9
  elif iquad == 2:
    return 9, 17, 1, 9
  elif iquad == 3:
    return 1, 9, 9, 17
  elif iquad == 4:
    return 9, 17, 9, 17

# Returns the pin factor based on the position
def getFactor(ipinx, ipiny):
  factor = 1.0
  if ipinx == 9:
    factor *= 0.5
  if ipiny == 9:
    factor *= 0.5
  return factor

izstart = 2
iz = 0
izdata = 0
stateStr = '/STATE_' + str(istate).zfill(4)
coremap = h5['/CORE/core_map'].value
verapow = h5[stateStr + '/pin_powers'].value
nestlepow = np.zeros(verapow.shape)
#print coremap
#print coremap.shape
#print verapow.shape

pinPowLineCount = 20
linenumber = 0
for line in text:
  linenumber += 1
  if 'NODE LOCATED AT' in line:
    inodex, inodey = readnodexy(line)
    iquad = xy2iquad(inodex, inodey)
    iassemx, iassemy = xy2iassemxy(inodex, inodey)
    iassem = coremap[iassemy-1][iassemx-1]
    xstart, xstop, ystart, ystop = iquad2pinxy(iquad)
    izdata = -1

  if 'AXIAL PLANE =' in line:
    iz = readz(line)

  if 'FUEL COLOR AXIAL SUBMESH' in line and iz > 0:
    izdata += 1
    pinPowLineCount = 0

  pinPowLineCount += 1
  if pinPowLineCount == 4:
    powerquad = []
  if pinPowLineCount >= 4 and pinPowLineCount <= 12:
    powerquad.append([float(val) for val in line.split()[1:]])
  if pinPowLineCount == 12:
#    if izdata == 0:
#      print linenumber, istate, iassem, iquad, ':', inodex, inodey, ':', xstart, xstop, ystart, ystop
    for iy in range(ystart,ystop+1):
      for ix in range(xstart,xstop+1):
        nestlepow[iy-1, ix-1, izdata, iassem-1] += powerquad[iy-ystart][ix-xstart]*getFactor(ix, iy)

# Unfold the center assembly
iassem = 1
xstart, xstop, ystart, ystop = iquad2pinxy(4)
for iy in range(ystart,ystop+1):
  # Unfold into the third quadrant
  for ix in range(xstart,xstop+1):
    nestlepow[iy-1,xstop-ix,:,iassem-1] += nestlepow[iy-1,ix-1,:,iassem-1]

# Unfold top row of assemblies
for iassem in range(1,9):
  for iy in range(ystart, ystop+1):
    for ix in range(1,xstop+1):
      nestlepow[ystop-iy,ix-1,:,iassem-1] += nestlepow[iy-1,ix-1,:,iassem-1]

# Unfold left column of assemblies
for iassem in [9, 17, 25, 33, 40, 47, 53]:
  for ix in range(xstart,xstop+1):
    for iy in range(1,ystop+1):
      nestlepow[iy-1,xstop-ix,:,iassem-1] += nestlepow[iy-1,ix-1,:,iassem-1]

def printAssemSlice(dat, iz, iassem):
  return '\n'.join('      ' + '  '.join('%5.3f' % dat[ix,iy,iz,iassem] for iy in xrange(dat.shape[1])) for ix in xrange(dat.shape[0]))


#for iassem in xrange(verapow.shape[3]):
#  print 'ASSEMBLY ' + str(iassem+1)
#  for iz in xrange(verapow.shape[2]):
#    print '  AXIAL LEVEL ' + str(iz+izstart)
#    print '    VERA:'
#    print printAssemSlice(verapow, iz, iassem)
#    print '    NESTLE:'
#    print printAssemSlice(nestlepow, iz, iassem)

if stateStr + '/nestle_pin_powers' in h5:
  del h5[stateStr + '/nestle_pin_powers']
h5[stateStr + '/nestle_pin_powers'] = nestlepow
