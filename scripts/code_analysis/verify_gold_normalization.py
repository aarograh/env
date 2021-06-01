#!/usr/bin/python2

import sys
import h5py
import numpy as np

if len(sys.argv) < 3 or len(sys.argv) > 4:
  print """
    usage:
      'python verify_gold_normalization.py <hdf5 file> <state index> [<true|false>]'

    If the third argument is 'false', the script will search for 'pin_powers' in
    '/STATE_<state index>/'.  Otherwise, it will search in '/EXPECTED/STATE_<state index>/'.
    """
  sys.exit()

file = h5py.File(sys.argv[1])
state = int(sys.argv[2])
if len(sys.argv) > 3:
  if sys.argv[3] == 'false':
    gold = False
  else:
    gold = True
else:
  gold = True

if gold:
  stateStr = '/EXPECTED/STATE_' + str(state).zfill(4)
else:
  stateStr = '/STATE_' + str(state).zfill(4)

powers = file[stateStr + '/pin_powers'].value
volumes = file['/CORE/pin_volumes'].value


numerator = 0.0
denominator = 0.0
unweighted_averge = 0.0
count = 0
for iassem in range(powers.shape[3]):
  for iz in range(powers.shape[2]):
    for ipiny in range(powers.shape[1]):
      for ipinx in range(powers.shape[0]):
        numerator += powers[ipinx,ipiny,iz,iassem]*volumes[ipinx,ipiny,iz,iassem]
        denominator += volumes[ipinx,ipiny,iz,iassem]
        unweighted_averge += powers[ipinx,ipiny,iz,iassem]
        if powers[ipinx,ipiny,iz,iassem] != 0.0:
          count += 1

print 'Average Pin Power = ' + str(numerator/denominator)
# print numerator
# print denominator
# print 'Unweighted Average Pin Power = ' + str(unweighted_averge/float(count))
# print count