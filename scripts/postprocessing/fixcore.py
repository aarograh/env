#!/usr/bin/python

import h5py
import sys
import numpy

fname = sys.argv[1]

h5 = h5py.File(fname,"r+")

realcore=numpy.array([[4, 3, 4],
                      [2, 1, 2],
                      [4, 3, 4]])

try:
    del h5['core_map']
except:
    print "argh"

h5.create_dataset("core_map",(3,3),dtype='i')
h5['core_map'].write_direct(realcore)
