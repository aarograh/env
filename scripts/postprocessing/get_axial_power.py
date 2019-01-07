#!/usr/bin/python

import h5py
import sys
import numpy as np
import os.path

# Get input and output file names
inpfile = sys.argv[1]
outfile, fileextension = os.path.splitext(inpfile)
outfile = outfile + '_axial_powers.txt'

# Open files
h5 = h5py.File(inpfile,"r+")
txt = open(outfile,"w")

print 'Extracting axial powers from %s and writing to %s...' %(inpfile,outfile)
numstates = 0
state_names = []
axial_powers = []

# Loop over all "STATE_" groups to count them and store names
while (1 == 1):
  numstates = numstates + 1
  subgroupname = "STATE_" + str(numstates)
  # STATE_counter is an exisiting group, so increment counter
  if subgroupname in h5[h5.name].keys():
    ###subgroupname = "pin_powers"
    state_names.append(subgroupname)
  # STATE_counter is not an existing group, so exit
  else:
  	numstates = numstates - 1
  	break

for counter in range(0,numstates):
  # Read in pin_powers dataset
  print "  Processing STATES %s..." %(str(counter+1))
  dset = h5["STATE_" + str(counter+1) + "/pin_powers"]
  ###dset = h5["pin_powers"]
  data = dset[...]

  # Calculate axial power at each level
  axial_powers.append([])
  volumes = h5["pin_volumes"]
  for i in range(0,len(data[0,0,:])):
  	axial_powers[counter].append(np.sum(volumes[:,:,i,:]*data[:,:,i,:])/np.sum(volumes[:,:,i,:]))

  # Normalize axial power
  axial_powers[counter-1] = axial_powers[counter-1]/(np.sum(axial_powers[counter-1])/len(axial_powers[counter-1]))

# Write axial powers to file
txt.write('LEVEL     ')
for i in range(0,len(state_names)):
  txt.write('%12s' %(state_names[i]))

txt.write('\n\n')

for i in range(0,len(axial_powers[0])):
  txt.write('Level %2s: ' %(str(i+1)))
  for j in range(0,len(axial_powers)):
    txt.write('%12.8f' %(axial_powers[j][i]))
  txt.write('\n')

h5.close()
txt.close()