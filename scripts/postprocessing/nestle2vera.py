#!/usr/bin/python2

import sys
import h5py
import numpy as np
import pylab as plt

def printUsage():
  sys.exit("Usage: 'nestle2vera.py <nestle text file> <vera hdf5 file> [<nestle state> <vera state> ['quarter'|'full']]")

if len(sys.argv) > 2:
  text = open(sys.argv[1])
  h5 = h5py.File(sys.argv[2])
  if len(sys.argv) == 3:
    printUsage()
  if len(sys.argv) > 3:
    nestle_state = int(sys.argv[3])
    vera_state = int(sys.argv[4])
  else:
    nestle_state = 1
    vera_state = 1
  if len(sys.argv) > 5:
    sym = sys.argv[5]
  else:
    sym = "quarter"
else:
  printUsage()

def readnodexy(line):
  return int(line[29:31]), int(line[33:35])

def readz(line):
  return int(line.split()[3])

# Assume a quarter core for now
# Returns the quadrant (1 to 4) given the x and y node positions (1-based index)
def xy2iquad(inodex, inodey):
  if sym == 'full':
    iquad = 1
  else:
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
  if sym == 'full':
    return inodex-1, inodey-1
  else:
    return 7+(inodex+1)/2+np.mod(inodex+1,2), 7+(inodey+1)/2+np.mod(inodey+1,2)

# Returns the pin start and top x and y positions for a quadrant (1-based index)
def iquad2pinxy(iquad):
  if sym == 'full':
    return 1, 17, 1, 17
  else:
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
  if sym == 'quarter':
    if ipinx == 9:
      factor *= 0.5
    if ipiny == 9:
      factor *= 0.5
  return factor

izstart = 2
iz = 0
izdata = 0
stateStr = '/STATE_' + str(vera_state).zfill(4)
coremap = h5['/CORE/core_map'].value
verapow = h5[stateStr + '/pin_powers'].value
nestlepow = np.zeros(verapow.shape)
#print coremap
#print coremap.shape
#print verapow.shape

ystart = 0
ystop = -1
pinPowLineCount = 20
linenumber = 0
current_nestle_state = 0
for line in text:
  linenumber += 1

  # Skip until we're at the correct state
  if 'PIN-POWER RECONSTRUCTION OUTPUT' in line:
    if current_nestle_state == nestle_state:
      print "Finished processing state..."
    current_nestle_state += 1
    print "Identified NESTLE state " + str(current_nestle_state) + " at line " + str(linenumber) + '...'
    if current_nestle_state == nestle_state:
      print "Begin processing state..."
    else:
      print "This state will not be processed..."
  if current_nestle_state != nestle_state:
    continue

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
    #print "Found assembly " + str(iassem), xstart, xstop, ystart, ystop
    powerquad = []
  #print pinPowLineCount
  if pinPowLineCount >= 4 and pinPowLineCount <= 4 + (ystop - ystart):
    powerquad.append([float(val) for val in line.split()[1:]])
    if pinPowLineCount == 4 + (ystop - ystart):
#      if izdata == 0:
#        print linenumber, vera_state, iassem, iquad, ':', inodex, inodey, ':', xstart, xstop, ystart, ystop
      #print "Getting data for assembly " + str(iassem), ':', xstart,xstop,ystart,ystop
      for iy in range(ystart,ystop+1):
        #print powerquad[iy-ystart]
        for ix in range(xstart,xstop+1):
          nestlepow[iy-1, ix-1, izdata, iassem-1] += powerquad[iy-ystart][ix-xstart]*getFactor(ix, iy)

if sym == 'quarter':
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
