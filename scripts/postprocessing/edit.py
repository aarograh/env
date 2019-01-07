#!/usr/bin/python
import h5py as h5
import numpy as np

input = h5.File('spert_test86_th.h5',"r+")

datasets = ['pin_fueltemps','pin_fueltemps_center','pin_fueltemps_surface','pin_cladtemps_inner','pin_cladtemps_outer']

for dset in datasets:
  temp = input['/' + dset]
  old_data = temp[...]
  new_data = old_data*1.0

  for i in range(0,len(old_data)):
    for j in range(0,len(old_data[i])):
      for k in range(0,len(old_data[i,j])):
        for m in range(0,len(old_data[i,j,k])):
          value = old_data[i,j,k,m]
          if value < -273.0:
            new_data[i,j,k,m] = 0.0
          else:
            new_data[i,j,k,m] = value
  shape = temp.shape
  dtype = temp.dtype
  try:
    del input['/' + dset]
  except:
    print 'argh! on ' + dset

  input.create_dataset(dset,shape,dtype=dtype)
  input[dset].write_direct(new_data)
