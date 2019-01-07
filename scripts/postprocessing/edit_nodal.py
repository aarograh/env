#!/usr/bin/python2

import sys
import h5py
import numpy as np
import pylab as plt

if len(sys.argv) > 1:
  h5=h5py.File(sys.argv[1])
else:
  h5=h5py.File('4a-2d.h5')

#### CORE block
print "CORE"
print "-------------------------------------------------------"

# Get some basic values
axial_mesh = h5["/CORE/axial_mesh"][...]
nodal_axial_mesh = h5["/CORE/computational_axial_mesh"]
coremap = h5["/CORE/core_map"][...]
nodal_coremap = h5["/CORE/computational_core_map"][...]
assembly_pitch = h5["/CORE/apitch"][...]
A = assembly_pitch/2. #Read the assembly pitch from the file
#A=21.5/2.
V=A*A #Get the volume (neglecting z direction)
sym = h5["/CORE/core_sym"][...]

# Number of assemblies in x and y directions (NESTLE input)
#print "NX " + str(len(nodal_coremap[0]))
#print "NY " + str(len(nodal_coremap))
print "Assembly Pitch: " + str(assembly_pitch)

# Mesh thicknesses in x, y, and z directions (NESTLE input)
meshstring = ' '.join(str(assembly_pitch) for i in nodal_coremap[0])
# Toggle line above with lines below to modify mesh to account for partial assemblies
#if sym == 4 and np.mod(len(coremap[0]),2) == 1:
#  meshstring = str(assembly_pitch/2.)
#else:
#  meshstring = str(assembly_pitch)
#for i in xrange(1,len(nodal_coremap[0])):
#  meshstring = ' '.join([meshstring, str(assembly_pitch)])
#print "NSPACEX " + meshstring

meshstring = ' '.join(str(assembly_pitch) for i in nodal_coremap)
# Toggle line above with lines below to modify mesh to account for partial assemblies
#if sym == 4 and np.mod(len(coremap),2) == 1:
#  meshstring = str(assembly_pitch/2.)
#else:
#  meshstring = str(assembly_pitch/2.)
#for i in xrange(1,len(nodal_coremap)):
#  meshstring = ' '.join([meshstring, str(assembly_pitch)])
#print "NSPACEY " + meshstring
meshstring = ' '.join(str(nodal_axial_mesh[i+1]-nodal_axial_mesh[i]) for i in xrange(0,len(nodal_axial_mesh)-1))
print "Axial Mesh: " + meshstring
if sym == 1:
  print "Symmetry: full"
else:
  print "Symmetry: quarter"

# Set the boundary conditions
bcond = []
if sym == 1:
  bcond.append(str(h5["/CORE/bc_rad"][...])[:3])
  bcond.append(str(h5["/CORE/bc_rad"][...])[:3])
  nxoffset = 0
  nyoffset = 0
else:
  bcond.append(str(h5["/CORE/bc_sym"][...])[:3])
  bcond.append(str(h5["/CORE/bc_sym"][...])[:3])
  nxoffset = coremap.shape[0]/2
  nyoffset = coremap.shape[1]/2
bcond.append(str(h5["/CORE/bc_rad"][...])[:3])
bcond.append(str(h5["/CORE/bc_rad"][...])[:3])
bcond.append(str(h5["/CORE/bc_top"][...])[:3])
bcond.append(str(h5["/CORE/bc_bot"][...])[:3])
print "Boundary Conditions:"
print "  Direction: WEST  | NORTH | EAST  | SOUTH | TOP   | BOTTOM"
print "  ---------------------------------------------------------"
print "       Type: " + ' | '.join(["{:5s}".format(i) for i in bcond])
print 'Fuel Core Map\n  ' +\
    '\n  '.join(map(str, ['  '.join([format(assembly,'3d') for assembly in row[nxoffset:]]) for row in coremap[nyoffset:]]))
print 'Core Map\n  ' +\
    '\n  '.join(map(str, ['  '.join([format(assembly,'3d') for assembly in row]) for row in nodal_coremap]))

for i in range(len(nodal_axial_mesh)):
  if nodal_axial_mesh[i] == axial_mesh[0]:
    fuelstartz = i+1
    fuelstopz = i+len(axial_mesh)-1
    break
print "Fuel Start Axial Level: " + str(fuelstartz)
print "Fuel  Stop Axial Level: " + str(fuelstopz)
print ""

# Get array and define function to go to fuel assembly index
def asy2powasy(asy):
    indexes = np.where(nodal_coremap == asy)
    indexes = [indexes[0][0] + nyoffset, indexes[1][0] + nxoffset]
    powasy = 0
    if indexes:
        if indexes[0] < coremap.shape[0] and indexes[1] < coremap.shape[1]:
            powasy = coremap[indexes[0]][indexes[1]]
    return powasy

### STATE blocks
st = 0
while True:
    st = st + 1
    stateStr = '/STATE_' + str(st).zfill(4)
    if not stateStr in h5:
      break

    keff=h5[stateStr + '/keff'].value
    ppw=h5[stateStr + '/pin_powers'].value
    cur=h5[stateStr + '/NODAL_XS/CUR'].value
    sfx=h5[stateStr + '/NODAL_XS/SFLX'].value
    chi=h5[stateStr + '/NODAL_XS/CHI'].value
    flx=h5[stateStr + '/NODAL_XS/FLUX'].value
    xf=h5[stateStr + '/NODAL_XS/XSF'].value
    nxf=h5[stateStr + '/NODAL_XS/NXSF'].value
    kxf=h5[stateStr + '/NODAL_XS/KXSF'].value
    xsr=h5[stateStr + '/NODAL_XS/XSRM'].value
    xstr=h5[stateStr + '/NODAL_XS/XSTR'].value
    xss=h5[stateStr + '/NODAL_XS/XSS'].value

    print "STATE {0:4d}".format(st)
    print "-------------------------------------------------------"
    print "  k-eff: {0:7.5f}".format(keff)
    nasy=flx.shape[0]
    nz=flx.shape[1]
    for az in xrange(nz):
        print "  AXIAL LEVEL {0:4d}".format(az+1)
        print ""

        for asy in xrange(nasy):
            powasy = asy2powasy(asy+1) - 1
            print "    ASSEMBLY {0:4d}".format(asy+1)
            print "        FLUX                  XSTR                  XSRM                  XSF                   NXSF                  KXSF                  CHI                   XSS                    Balance"
            print "  node  1          2          1          2          1          2          1          2          1          2          1          2          1          2          1>2        2>1         1           2"
            for nd in xrange(4):
                col=np.multiply(xsr[asy,0,nd,:],flx[asy,0,nd,:])
                scat=np.transpose(xss[asy,0,nd,:,:]); scat[0,0]=0.0; scat[1,1]=0.0
                ssrc=np.dot(scat,flx[asy,0,nd,:])
                fsrc=chi[asy,0,nd,:]/keff*np.dot(nxf[asy,0,nd,:],flx[asy,0,nd,:])
                print "  {0:1d}     {1:10.4e} {2:10.4e} {3:10.4e} {4:10.4e} {5:10.4e} {6:10.4e} {7:10.4e} {8:10.4e} {9:10.4e} {10:10.4e} {11:10.4e} {12:10.4e} {13:10.4e} {14:10.4e} {15:10.4e} {16:10.4e} {17:11.4e} {18:11.4e}".format(nd+1,flx[asy,az,nd,0],flx[asy,az,nd,1],xstr[asy,az,nd,0],xstr[asy,az,nd,1],xsr[asy,az,nd,0],xsr[asy,az,nd,1],xf[asy,az,nd,0],xf[asy,az,nd,1],nxf[asy,az,nd,0],nxf[asy,az,nd,1],kxf[asy,az,nd,0],kxf[asy,az,nd,1],chi[asy,az,nd,0],chi[asy,az,nd,1],xss[asy,az,nd,0,1],xss[asy,az,nd,1,0],(-col[0]+ssrc[0]+fsrc[0])*V-np.sum(cur[asy,az,nd,0])*A,(-col[1]+ssrc[1]+fsrc[1])*V-np.sum(cur[asy,az,nd,1])*A)
            print ""
            print "Current"
            print "        WEST                  NORTH                 EAST                  SOUTH                 TOP                   BOTTOM"
            print "  node  1          2          1          2          1          2          1          2          1          2          1          2"
            for nd in xrange(4):
                print "  {0:1d}    {1:10.3e} {2:10.3e} {3:10.3e} {4:10.3e} {5:10.3e} {6:10.3e} {7:10.3e} {8:10.3e} {9:10.3e} {10:10.3e} {9:11.3e} {12:10.3e}".format(nd+1,cur[asy,az,nd,0,0],cur[asy,az,nd,1,0],cur[asy,az,nd,0,1],cur[asy,az,nd,1,1],cur[asy,az,nd,0,2],cur[asy,az,nd,1,2],cur[asy,az,nd,0,3],cur[asy,az,nd,1,3],cur[asy,az,nd,0,4],cur[asy,az,nd,1,4],cur[asy,az,nd,0,5],cur[asy,az,nd,1,5])
            print ""
            print "Surface Flux"
            print "        WEST                  NORTH                 EAST                  SOUTH                 TOP                   BOTTOM"
            print "  node  1          2          1          2          1          2          1          2          1          2          1          2"
            for nd in xrange(4):
                print "  {0:1d}     {1:10.4e} {2:10.4e} {3:10.4e} {4:10.4e} {5:10.4e} {6:10.4e} {7:10.4e} {8:10.4e} {9:10.4e} {10:10.4e} {9:11.4e} {12:10.4e}".format(nd+1,sfx[asy,az,nd,0,0],sfx[asy,az,nd,1,0],sfx[asy,az,nd,0,1],sfx[asy,az,nd,1,1],sfx[asy,az,nd,0,2],sfx[asy,az,nd,1,2],sfx[asy,az,nd,0,3],sfx[asy,az,nd,1,3],sfx[asy,az,nd,0,4],sfx[asy,az,nd,1,4],sfx[asy,az,nd,0,5],sfx[asy,az,nd,1,5])
            print ""
            if powasy >= 0 and az >= fuelstartz-1 and az <= fuelstopz-1:
                print "Pin Powers"
                for i in xrange(ppw.shape[0]):
                    print '      '+' '.join('%6.4f' % ppw[i,j,az-fuelstartz,powasy] for j in xrange(ppw.shape[1]))
                print ""
