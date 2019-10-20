#!/usr/bin/python2

import sys
import h5py
import numpy as np
import pylab as plt

if len(sys.argv) > 1:
  file = open(sys.argv[1])
else:
  sys.abort("Need input file!")

counter = {}
fuelCoreMap = []
coreMap = []
zFuelStart = 0
zFuelStop = 0
nStates = 0

# Read in the geometry information
for line in file:
  # Check for special keywords
  if "Assembly Pitch:" in line:
    apitch = float(line.split()[2])

  elif "Axial Mesh:" in line:
    levels = line.split()[2:]
    axialmesh = np.zeros(len(levels))
    for i in xrange(len(levels)):
      axialmesh[i] = float(levels[i])
    print axialmesh

  elif "Fuel Core Map" in line:
    counter['Fuel Core Map'] = 0

  elif "Core Map" in line:
    del counter['Fuel Core Map']
    counter['Core Map'] = 0
    print "Fuel Core Map:", fuelCoreMap

  elif "Fuel Start" in line:
    del counter['Core Map']
    zFuelStart = int(line.split()[4])
    print "Core Map:", coreMap
    print "zFuelStart:",zFuelStart
    zFuelStart -= 1

  elif "Fuel  Stop" in line:
    zFuelStop = int(line.split()[4])
    print "zFuelStop",zFuelStop
    zFuelStop -= 1

  elif "STATE" in line:
    nStates += 1

  # Increment the counters
  if 'Fuel Core Map' in counter:
    counter['Fuel Core Map'] += 1
  if 'Core Map' in counter:
    counter['Core Map'] += 1

  # Fill in the fuel core map
  if 'Fuel Core Map' in counter:
    if counter['Fuel Core Map'] > 1:
      asyx = []
      for asy in line.split():
        asyx.append(int(asy))
      fuelCoreMap.append(asyx)

  # Fill in the core map
  if 'Core Map' in counter:
    if counter['Core Map'] > 1:
      asyx = []
      for asy in line.split():
        asyx.append(int(asy))
      coreMap.append(asyx)

nodeArea = apitch*apitch/4.0
npinx = 17
npiny = 17
nassem = np.max(coreMap)
nz = len(axialmesh)

print "nodeArea=", nodeArea, "  npinx=", npinx, '  npiny=', npiny, '  nz=', nz, '  nassem=', nassem, '  nStates=', nStates

pinPowers = np.zeros([nStates, nassem, nz, npiny, npinx])
nodeFlux = np.zeros([nStates, nassem, nz, 4, 2])
nodeKF = np.zeros([nStates, nassem, nz, 4, 2])

# Store all the cross section and power data
file.close()
file = open(sys.argv[1])
for line in file:
  if "STATE" in line:
    istate = int(line.split()[1])
    istate -= 1

  elif "AXIAL LEVEL" in line:
    iz = int(line.split()[2])
    iz -= 1

  elif "ASSEMBLY" in line:
    iassem = int(line.split()[1])
    iassem -= 1

  elif "FLUX" in line:
    counter['FLUX'] = 0

  elif "Pin Powers" in line:
    counter['Pin Powers'] = 0

  # Fill cross sections
  if 'FLUX' in counter:
    counter['FLUX'] += 1
    if counter['FLUX'] > 2:
      strlist = line.split()
      inode = int(strlist[0])-1
      nodeFlux[istate, iassem, iz, inode, 0] = float(strlist[1])
      nodeFlux[istate, iassem, iz, inode, 1] = float(strlist[2])
      nodeKF[istate, iassem, iz, inode, 0] = float(strlist[11])
      nodeKF[istate, iassem, iz, inode, 1] = float(strlist[12])

    if counter['FLUX'] == 6:
      del counter['FLUX']

  # Fill in Pin Powers
  if 'Pin Powers' in counter:
    counter['Pin Powers'] += 1
    if counter['Pin Powers'] > 1:
      strlist = line.split()
      for ix in xrange(len(strlist)):
        pinPowers[istate, iassem, iz, counter['Pin Powers']-2, ix] = float(strlist[ix])

    if counter['Pin Powers'] > npiny:
      del counter['Pin Powers']

# Calculate the node powers
nodePower = np.sum(nodeFlux*nodeKF, axis=4)
totalPower = 0.0
totalHeight = 0.0
for iz in xrange(nodePower.shape[2]):
  # print "Calculating Level " + str(iz)
  nodePower[:, :, iz, :] = nodePower[:, :, iz, :] * nodeArea
  totalPower += np.sum(nodePower[:, :, iz, :])*axialmesh[iz]
  totalHeight += np.count_nonzero(nodePower[:, :, iz, :])*axialmesh[iz]

normFactor = totalPower/totalHeight
nodePower = nodePower/normFactor
istate = 0
iassem = 0

# Calculate the node powers from pin powers
totalpower = 0.0
totalHeight = 0.0
pinNodePowers = np.zeros(nodePower.shape)
avgPinPowers = np.zeros(nodePower.shape)
avgPinCount = np.zeros(nodePower.shape)
midy = int(npiny/2) + np.mod(npiny,2)-1
midx = int(npinx/2) + np.mod(npinx,2)-1
lsplity = (np.mod(npiny,2) == 1)
lsplitx = (np.mod(npinx,2) == 1)
for iz in xrange(pinNodePowers.shape[2]):
  for ipiny in xrange(npiny):
    for ipinx in xrange(npinx):
      # Center pin
      if ipiny ==  midy and lsplity and ipinx == midx and lsplitx:
        inodes = [1, 2, 3, 4]
        factor = 0.25
      # Half, split horizontally
      elif ipiny == midy and lsplity:
        if ipinx <= midx:
          inodes = [1, 3]
        else:
          inodes = [2, 4]
        factor = 0.5
      # Half, split vertically
      elif ipinx == midx and lsplitx:
        if ipiny <= midy:
          inodes = [1, 2]
        else:
          inodes = [3, 4]
        factor = 0.5
      # Whole
      else:
        if ipiny <= midy:
          if ipinx <= midx:
            inodes = [1]
          else:
            inodes = [2]
        else:
          if ipinx <= midx:
            inodes = [3]
          else:
            inodes = [4]
        factor = 1.0

      # Accumulate power
      contribution = pinPowers[:, :, iz, ipiny, ipinx]*factor
      for inode in (int(inodes[i]) for i in xrange(len(inodes))):
        pinNodePowers[:, :, iz, inode-1] += contribution
        avgPinPowers[:,:,iz,inode-1] += contribution
        avgPinCount[:,:,iz,inode-1] += factor

# Normalize the RMS
avgPinPowers = avgPinPowers/avgPinCount
# Normalize the powers
totalHeight = 0.0
totalPower = 0.0
for iz in xrange(pinNodePowers.shape[2]):
  totalPower += np.sum(pinNodePowers[:, :, iz, :])*axialmesh[iz]
  totalHeight += np.count_nonzero(pinNodePowers[:, :, iz, :])*axialmesh[iz]

normFactor = totalPower/totalHeight
pinNodePowers = pinNodePowers/normFactor
istate = 0
iassem = 0

def print_core_comparisons(ref, comp, name, relative=False):
  diff = np.zeros(ref.shape)
  for istate in xrange(ref.shape[0]):
    for iassem in xrange(ref.shape[1]):
      for iz in xrange(ref.shape[2]):
        for inode in xrange(ref.shape[3]):
          if not ref[istate, iassem, iz, inode] == 0.0 and not comp[istate, iassem, iz, inode] == 0:
            diff[istate, iassem, iz, inode] = (comp[istate, iassem, iz, inode] - ref[istate, iassem, iz, inode])
            if relative:
              diff[istate, iassem, iz, inode] = diff[istate, iassem, iz, inode]/ref[istate, iassem, iz, inode]
          else:
            diff[istate, iassem, iz, inode] = 0.0

  for istate in xrange(ref.shape[0]):
    for iz in xrange(ref.shape[2]):
      print name + ', AXIAL LEVEL ' + str(iz+1)
      for iy in coreMap:
        for iynode in [1,2]:
          print '   ' + '   '.join('   '.join(\
            format(ref[istate, ix-1, iz, inode],'6.3f') if ix > 0 else '' \
            for inode in [(iynode-1)*2, (iynode-1)*2+1]) for ix in iy)
          print '   ' + '   '.join('   '.join(\
            format(comp[istate, ix-1, iz, inode],'6.3f') if ix > 0 else '' \
            for inode in [(iynode-1)*2, (iynode-1)*2+1]) for ix in iy)
          print '   ' + '   '.join('   '.join(\
            format(diff[istate, ix-1, iz, inode],'6.3f') if ix > 0 else '' \
            for inode in [(iynode-1)*2, (iynode-1)*2+1]) for ix in iy)
          print
  if np.count_nonzero(diff) == 0:
    printval = 0.0
  else:
    printval = np.sqrt(np.sum(diff*diff)/np.count_nonzero(diff))
  print 'RMS DIFFERENCE FOR ' + str(name) + ' = ' + format(printval,'6.3f')
  print 'MAX DIFFERENCE FOR ' + str(name) + ' = ' + \
      format(np.max(diff),'6.3f')
  print 'MIN DIFFERENCE FOR ' + str(name) + ' = ' + \
      format(np.min(diff),'6.3f')
  print

print_core_comparisons(nodePower, pinNodePowers, 'NODE POWER VS. PIN-NODE POWER')
print_core_comparisons(nodePower, avgPinPowers, 'NODE POWER VS. NODE RMS PIN POWER')