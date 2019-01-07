#!/usr/bin/python

import sys
import h5py

filename = sys.argv[1]

h5 = h5py.File(filename,"r+")

i = 0
while True:
  i = i + 1
  statename = '/EXPECTED/STATE_' + str(i).zfill(4)
  print "checking state " + statename
  try:
    state = h5[statename]
  except:
    print "State not found.  Exiting."
    break

  for dataset in ["pin_modtemps","pin_cladtemps","pin_fueltemps","pin_moddens"]:
    datasetname = statename + '/' + dataset
    print "Removing " + datasetname
    try:
      del h5[datasetname]
    except:
      print "Something went wrong"
