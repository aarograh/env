#!/usr/bin/python2

import sys
import os
import subprocess
import h5py

raw = os.popen('find /users/ag6/master/MPACT/MPACT_* -print | grep .h5.gold').read()

files = raw.split('\n')
for name in files:
  file = h5py.File(name)
  for state in xrange(1,10000):
    if '/EXPECTED/STATE_' + str(state).zfill(4) in file:
      command = 'python /users/ag6/env/scripts/code_analysis/verify_gold_normalization.py ' + name + ' ' + str(state)
      print command
      print os.popen(command).read()
    else:
      break
  print ""