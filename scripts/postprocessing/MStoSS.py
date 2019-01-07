#!/usr/bin/python
import h5py as h5
import numpy as np
import sys

input = h5.File(sys.argv[1],"r+")

for gname in input.keys():
  item = input[gname]

  if (isinstance(item, h5.Group)):
    if gname != 'INPUT':
      for name,data in dict(item).iteritems():
  
        shape = data.shape
        dtype = data.dtype

        input.create_dataset('/' + name,shape,dtype=dtype)
        input[name].write_direct(data[...])
        del input[data.name]

    del input[item.name]

