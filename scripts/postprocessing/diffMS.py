#!/usr/bin/python
import h5py as h5
import numpy as np
import sys
import os
import subprocess

def copy_group(group,file):
  for name,data in dict(group).iteritems():
    shape = data.shape
    dtype = data.dtype
    file.create_dataset('/' + name,shape,dtype=dtype)
    file[name].write_direct(data[...])

def add_other_data(oldfile,newfile):
  for gname in oldfile.keys():
    item = oldfile[gname]
    if (isinstance(item,h5.Dataset)):
      data = item[...]
      name = item.name
      shape = data.shape
      dtype = data.dtype
      newfile.create_dataset('/' + name,data=data)
  return

def axial_reduce(newmesh,oldmesh,newdata,olddata,div):
  j = 0
  for i in range(0,len(newmesh)-1):
    if np.abs(newmesh[i] - oldmesh[j]) <= 0.1:
      newdata[:,:,i,:] = olddata[:,:,j,:]
    else:
      matching = False
      k = j
      newdata[:,:,i,:] = 0. * newdata[:,:,i,:]
      while not matching:
        delta = oldmesh[k] - oldmesh[k-1]
        newdata[:,:,i,:] = newdata[:,:,i,:] + delta*olddata[:,:,k,:]
        print i,j,k,newmesh[i-1],newmesh[i],oldmesh[k-1],oldmesh[k],delta,olddata[12,13,k,0],newdata[12,13,i,0]
        if np.abs(newmesh[i] - oldmesh[k]) <= 0.001:
          matching = True
          if div:
            delta = newmesh[i] - newmesh[i-1]
            newdata[:,:,i,:] = newdata[:,:,i,:]/delta
            print i,j,k,delta,newdata[12,13,i,0]
        else:
          k = k + 1
      j = k
    j = j + 1
  return

def merge(file1,file2,state,vols):
  mesh1 = file1['/axial_mesh'][...]
  mesh2 = file2['/axial_mesh'][...]
  shape1 = mesh1.shape
  shape2 = mesh2.shape
  if shape1[0] < shape2[0]:
    newpowers = file1['/pin_powers'][...]
    oldpowers = file2['/pin_powers'][...]
    axial_reduce(mesh1,mesh2,newpowers,oldpowers,True)
    grp = file2['/']
    del grp['axial_mesh']
    file2.create_dataset('/axial_mesh', data=mesh1)
    del grp['pin_powers']
    file2.create_dataset('/pin_powers', data=newpowers)
    if vols:
      newvols = file1['/pin_volumes'][...]
#      oldvols = file2['/pin_volumes'][...]
#      axial_reduce(mesh1,mesh2,newvols,oldvols,False)
      del grp['pin_volumes']
      file2.create_dataset('/pin_volumes', data=newvols)
  elif shape1[0] > shape2[0]:
    newpowers = file2['/pin_powers'][...]
    oldpowers = file1['/pin_powers'][...]
    axial_reduce(mesh2,mesh1,newpowers,oldpowers,True)
    grp = file1['/']
    del grp['axial_mesh']
    file1.create_dataset('/axial_mesh', data=mesh2)     
    del grp['pin_powers']
    file1.create_dataset('/pin_powers', data=newpowers)
    if vols:
      newvols = file2['/pin_volumes'][...]
#      oldvols = file1['/pin_volumes'][...]
#      axial_reduce(mesh2,mesh1,newvols,oldvols,False)
      del grp['pin_volumes']
      file1.create_dataset('/pin_volumes', data=newvols)
  else:
    return

# Check number of arguments
if len(sys.argv) < 3:
  print 'Two VERA hdf5 files are required as arguments.'
  sys.exit(1)
elif len(sys.argv) > 3:
  print 'Two VERA hdf5 files are required as arguments.  Extra arguments are being ignored.'
  
# Open input files and setup filename variables
inpname1 = sys.argv[1]
inpname2 = sys.argv[2]
inp1 = h5.File(inpname1,"r+")
inp2 = h5.File(inpname2,"r+")
outpref1, ext = os.path.splitext(sys.argv[1])
outpref2, ext = os.path.splitext(sys.argv[2])
outpref1 = outpref1 + '_'
outpref2 = outpref2 + '_'

# Get core data from both files
# TODO: Add a few lines to make sure they're the same
core1 = inp1['CORE']
if not (isinstance(core1,h5.Group)):
  print 'Error: file ' + inpname1 + ' does not have CORE data group!'
  sys.exit(2)
core2 = inp2['CORE']
if not (isinstance(core2,h5.Group)):
  print 'Error: file ' + inpname2 + ' does not have CORE data group!'
  sys.exit(3)

# Prepare loop controls
reading = True
istate = 0

# Begin looping
while reading:
  # Increment state counter and make sure it's reasonable
  istate = istate + 1
  if istate < 10:
    gname = 'STATE_000' + str(istate)
  elif istate < 100:
    gname = 'STATE_00' + str(istate)
  elif istate < 1000:
    gname = 'STATE_0' + str(istate)
  elif istate < 10000:
    gname = 'STATE_' + str(istate)
  else:
    print 'Error: attempted to access state ' + str(istate) + '!'
    sys.exit(4)

  # Open STATE data groups and make sure they exist
  reading = gname in inp1
  if reading:
    state1 = inp1[gname]
    reading = gname in inp2
    if reading:
      state2 = inp2[gname]
    else:
      print 'Error: data group ' + gname + ' exists in ' + inpname1 + ' but not in ' + inpname2 + '!'
      sys.exit(5)
  else:
    reading = gname in inp2
    if reading:
      print 'Error: data group ' + gname + ' exists in ' + inpname2 + ' but not in ' + inpname1 + '!'
      sys.exit(6)
    
  if not reading:
    print 'No more states found.  Exiting diffMS.py'
  else:
    print 'Now processing state ' + str(istate)
    # Create temporary files
    outname1 = outpref1 + gname + '.h5'
    outname2 = outpref2 + gname + '.h5'
    tmpfile1 = h5.File(outname1,'w')
    tmpfile2 = h5.File(outname2,'w')
 
    # Write CORE data
    copy_group(core1,tmpfile1)
    copy_group(core2,tmpfile2)
 
    # Write STATE data
    copy_group(state1,tmpfile1)
    copy_group(state2,tmpfile2)

    # Write other data to file such as version numbers, name, etc.
    add_other_data(inp1,tmpfile1)
    add_other_data(inp2,tmpfile2)

    # correct for different axial meshes
    if istate == 1:
      diffall = 'Beginning comparison of vera-out hdf5 files ' + outname1 + ' and ' + outname2 + ':\n\n\n'
      merge(tmpfile1,tmpfile2,gname,True)
    else:
      merge(tmpfile1,tmpfile2,gname,False)

    # Close files
    tmpfile1.close()
    tmpfile2.close()
 
    # Call veradiff.exe
    command = '/home/aarograh/scripts/veradiff.exe ' + outname1 + ' ' + outname2
#    command = 'veradiff.exe ' + outname1 + ' ' + outname2
#    print 'Executing: ' + command
    status = subprocess.call(command,shell=True)
 
    # Read in veradiff output
    diffout = open('veradiff.out','r')
 
    # Store in string
    diffall =diffall + 'Diffing state ' + str(istate) + ':\n\n' + diffout.read() + '\n\n\n'
 
    # Remove old files
    os.system('rm veradiff.out')
    os.system('rm veradiff.log')
#    os.system('rm ' + outname1)
#    os.system('rm ' + outname2)

print 'Diff finished with no errors.  Contents being written to veradiff.out.'

# Write all the output to a single veradiff.out file
diffout = open('veradiff.out','w')
diffout.write(diffall)

# Finish
print 'All done! Thank you for using diffMS.py.  It\'s been a pleasure.'
