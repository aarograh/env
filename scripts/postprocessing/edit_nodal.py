#!/usr/bin/python2

import sys
import h5py
import numpy as np

def assembliesAreSplit(sym, coremap):
    splitx = False
    splity = False
    if sym == 4:
        if np.mod(coremap.shape[0],2) == 1:
            splitx = True
        if np.mod(coremap.shape[1],2) == 1:
            splity = True
    return [splitx, splity]

def K2F(data):
    for node in xrange(data.shape[0]):
        for level in xrange(data.shape[1]):
            for asy in xrange(data.shape[2]):
                if data[node,level,asy] > np.finfo(float).eps:
                    data[node,level,asy] = (data[node,level,asy]-273.15) * 1.8 + 32

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

axial_deltas = axial_mesh[1:]-axial_mesh[0:-1]
fuelheight = axial_mesh[-1]-axial_mesh[0]

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

# Print the number of nodes in x an dy directions
[splitx, splity] = assembliesAreSplit(sym, coremap)
nx = nodal_coremap.shape[0]*2
ny = nodal_coremap.shape[1]*2
if splitx:
    nx = nx - 1
if splity:
    ny = ny - 1
print "Number of nodes and widths in x direction: " + str(nx) + ' ' + str(A)
print "Number of nodes and widths in y direction: " + str(ny) + ' ' + str(A)
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

    # Read all the state data
    keff     = h5[stateStr + '/keff'].value
    fluxnorm = h5[stateStr + '/NODAL_XS/FLUXNORM'].value
    boron    = h5[stateStr + '/boron'].value
    ppw      = h5[stateStr + '/pin_powers'].value
    adf      = h5[stateStr + '/NODAL_XS/ADF'].value
    cur      = h5[stateStr + '/NODAL_XS/CUR'].value
    sfx      = h5[stateStr + '/NODAL_XS/SFLX'].value
    chi      = h5[stateStr + '/NODAL_XS/CHI'].value
    flx      = h5[stateStr + '/NODAL_XS/FLUX'].value
    xf       = h5[stateStr + '/NODAL_XS/XSF'].value
    nxf      = h5[stateStr + '/NODAL_XS/NXSF'].value
    kxf      = h5[stateStr + '/NODAL_XS/KXSF'].value
    xsr      = h5[stateStr + '/NODAL_XS/XSRM'].value
    xstr     = h5[stateStr + '/NODAL_XS/XSTR'].value
    xss      = h5[stateStr + '/NODAL_XS/XSS'].value #First two axes are [from, to]
    swcpv    = h5[stateStr + '/NODAL_XS/CORNERFLUX'].value
    rhowrefv = h5[stateStr + '/NODAL_XS/COOLDENS'].value # g/cc
    tfrefv   = h5[stateStr + '/NODAL_XS/FUELTEMP'].value # K
    tfsrefv  = h5[stateStr + '/NODAL_XS/FUELSURFTEMP'].value # K
    tcolrefv = h5[stateStr + '/NODAL_XS/COOLTEMP'].value # K
    wtfrrov  = h5[stateStr + '/NODAL_XS/WETVOLFRAC'].value
    fufrv    = h5[stateStr + '/NODAL_XS/FUELVOLFRAC'].value
    dfiv     = h5[stateStr + '/NODAL_XS/I135ND'].value # 1/barn-cm
    dpmv     = h5[stateStr + '/NODAL_XS/PM149ND'].value # 1/barn-cm
    dsmv     = h5[stateStr + '/NODAL_XS/SM149ND'].value # 1/barn-cm
    dxev     = h5[stateStr + '/NODAL_XS/XE135ND'].value # 1/barn-cm
    xxeabv   = h5[stateStr + '/NODAL_XS/XE135XSAB'].value # barns
    xsmabv   = h5[stateStr + '/NODAL_XS/SM149XSAB'].value # barns
    xhidmiv  = h5[stateStr + '/NODAL_XS/CHID'].value
    betav    = h5[stateStr + '/NODAL_XS/BETA'].value
    velocv   = h5[stateStr + '/NODAL_XS/VELOCITY'].value # cm/sec
    burnup   = h5[stateStr + '/NODAL_XS/BURNUP'].value #MWd/kgHM
    ifractv  = h5[stateStr + '/NODAL_XS/RODFRAC'].value #[0.0, 1.0], 0.0 is fully withdrawn, 1.0 is fully inserted

    # Before we do anything convert temperatures from K to F
    K2F(tfrefv)
    K2F(tfsrefv)
    K2F(tcolrefv)

    nasy=flx.shape[3]
    nz=flx.shape[2]

    # Calculate the axial powers - Sum radially, calculate average linear power, then normalize
    axpow = np.sum(np.sum(np.sum(ppw,axis=0),axis=0),axis=1)
    axpow = axpow/(np.sum(axpow*axial_deltas)/fuelheight)

    # Calculate the radial powers - Sum pow*height for each pin and divide by fuel height
    radpow = np.sum(ppw,axis=2)
    for i in range(radpow.shape[0]):
        for j in range(radpow.shape[1]):
            for asy in xrange(nasy):
                powasy = asy2powasy(asy+1)-1
                radpow[i,j,powasy] = np.sum(ppw[i,j,:,powasy]*axial_deltas)/fuelheight

    print "STATE {0:4d}".format(st)
    print "-------------------------------------------------------"
    print "  k-eff: {0:7.5f}".format(keff)
    print "  boron: {0:7.2f} ppm".format(boron)
    print "  Flux Normalization: {0:12.5e}".format(fluxnorm)
    print ""
    print "Axial Power"
    for az in reversed(xrange(nz)):
        if az >= fuelstartz-1 and az <= fuelstopz-1:
            print "  {0:2d}    {1:10.3e}".format(az+1, axpow[az-fuelstartz])
    for az in xrange(nz):
        print "  AXIAL LEVEL {0:4d}".format(az+1)
        print ""
        deltaz = (nodal_axial_mesh[az+1]-nodal_axial_mesh[az])

        for asy in xrange(nasy):
            powasy = asy2powasy(asy+1) - 1

            # Print assembly header
            print "    ASSEMBLY {0:4d}".format(asy+1)

            # Print basic fluxes, cross sections, and balance
            print "        FLUX                  XSTR                  XSRM                  XSF                   NXSF                  KXSF                  CHI                   XSS                    Balance"
            print "  node  1          2          1          2          1          2          1          2          1          2          1          2          1          2          1>2        2>1         1           2"
            for nd in xrange(4):
                col=np.multiply(xsr[:,nd,az,asy],flx[:,nd,az,asy])
                scat=np.transpose(xss[:,:,nd,az,asy]); scat[0,0]=0.0; scat[1,1]=0.0
                ssrc=np.dot(scat,flx[:,nd,az,asy])
                fsrc=chi[:,nd,az,asy]/keff*np.dot(nxf[:,nd,az,asy],flx[:,nd,az,asy])
                source = (ssrc[0] + fsrc[0])*A*A*deltaz
                loss = col[0]*A*A*deltaz
                leakage = np.sum(cur[0:4,0,nd,az,asy])*A*deltaz + np.sum(cur[4:,0,nd,az,asy])*A*A
                bal = [source - loss - leakage]
                source = (ssrc[1] + fsrc[1])*V*deltaz
                loss = col[1]*V*deltaz
                leakage = np.sum(cur[0:4,1,nd,az,asy])*A*deltaz + np.sum(cur[4:,1,nd,az,asy])*A*A
                bal.append(source - loss - leakage)
                # Fluxes and cross sections
                print "  {0:1d}     {1:10.4e} {2:10.4e} {3:10.4e} {4:10.4e} {5:10.4e} {6:10.4e} {7:10.4e} {8:10.4e} {9:10.4e} {10:10.4e} {11:10.4e} {12:10.4e} {13:10.4e} {14:10.4e} {15:10.4e} {16:10.4e} {17:11.4e} {18:11.4e}".format(\
                    nd+1, flx[0,nd,az,asy], flx[1,nd,az,asy], xstr[0,nd,az,asy], xstr[1,nd,az,asy], xsr[0,nd,az,asy], xsr[1,nd,az,asy], xf[0,nd,az,asy], xf[1,nd,az,asy], nxf[0,nd,az,asy], nxf[1,nd,az,asy], kxf[0,nd,az,asy], kxf[1,nd,az,asy], \
                    chi[0,nd,az,asy], chi[1,nd,az,asy], xss[0,1,nd,az,asy], xss[1,0,nd,az,asy], bal[0], bal[1])
            print ""

            ## ADF
            #print "ADF"
            #print "        WEST                  NORTH                 EAST                  SOUTH                 TOP                   BOTTOM"
            #print "  node  1          2          1          2          1          2          1          2          1          2          1          2"
            #for nd in xrange(4):
            #    print "  {0:1d}    {1:10.3e} {2:10.3e} {3:10.3e} {4:10.3e} {5:10.3e} {6:10.3e} {7:10.3e} {8:10.3e} {9:10.3e} {10:10.3e} {11:10.3e} {12:10.3e}".format(\
            #        nd+1, adf[0,0,nd,az,asy], adf[0,1,nd,az,asy], adf[1,0,nd,az,asy], adf[1,1,nd,az,asy], adf[2,0,nd,az,asy], adf[2,1,nd,az,asy], adf[3,0,nd,az,asy], \
            #        adf[3,1,nd,az,asy], adf[4,0,nd,az,asy], adf[4,1,nd,az,asy], adf[5,0,nd,az,asy], adf[5,1,nd,az,asy])
            #print ""

            # Currents
            print "Current"
            print "        WEST                  NORTH                 EAST                  SOUTH                 TOP                   BOTTOM"
            print "  node  1          2          1          2          1          2          1          2          1          2          1          2"
            for nd in xrange(4):
                print "  {0:1d}    {1:10.3e} {2:10.3e} {3:10.3e} {4:10.3e} {5:10.3e} {6:10.3e} {7:10.3e} {8:10.3e} {9:10.3e} {10:10.3e} {11:10.3e} {12:10.3e}".format(\
                    nd+1, cur[0,0,nd,az,asy], cur[0,1,nd,az,asy], cur[1,0,nd,az,asy], cur[1,1,nd,az,asy], cur[2,0,nd,az,asy], cur[2,1,nd,az,asy], cur[3,0,nd,az,asy], \
                    cur[3,1,nd,az,asy], cur[4,0,nd,az,asy], cur[4,1,nd,az,asy], cur[5,0,nd,az,asy], cur[5,1,nd,az,asy])
            print ""

            # Surface Fluxes
            print "Surface Flux"
            print "        WEST                  NORTH                 EAST                  SOUTH                 TOP                   BOTTOM"
            print "  node  1          2          1          2          1          2          1          2          1          2          1          2"
            for nd in xrange(4):
                print "  {0:1d}     {1:10.4e} {2:10.4e} {3:10.4e} {4:10.4e} {5:10.4e} {6:10.4e} {7:10.4e} {8:10.4e} {9:10.4e} {10:10.4e} {11:10.4e} {12:10.4e}".format(\
                    nd+1, sfx[0,0,nd,az,asy], sfx[0,1,nd,az,asy], sfx[1,0,nd,az,asy], sfx[1,1,nd,az,asy], sfx[2,0,nd,az,asy], sfx[2,1,nd,az,asy], sfx[3,0,nd,az,asy], \
                    sfx[3,1,nd,az,asy], sfx[4,0,nd,az,asy], sfx[4,1,nd,az,asy], sfx[5,0,nd,az,asy], sfx[5,1,nd,az,asy])
            print ""

            # Pin Powers
            if powasy >= 0 and az >= fuelstartz-1 and az <= fuelstopz-1:
                print "Pin Powers"
                for i in xrange(ppw.shape[0]):
                    print '      ' + ' '.join('%6.4f' % ppw[i,j,az-fuelstartz+1,powasy] for j in xrange(ppw.shape[1]))
                print ""

            # TH Data
            print "TH"
            print "  node  RHOWREFV   TCOLREFV   TFREFV     TFSREFV    WTFRROV    FUFRV"
            for nd in xrange(4):
                print "  {0:1d}     {1:10.4e} {2:10.4e} {3:10.4e} {4:10.4e} {5:10.4e} {6:10.4e}".format(\
                    nd+1, rhowrefv[nd,az,asy], tcolrefv[nd,az,asy], tfrefv[nd,az,asy], tfsrefv[nd,az,asy], wtfrrov[nd,az,asy], fufrv[nd,az,asy])
            print ""

            # Transient
            print "Transient"
            print "        VELOCV                XHIDMIV               BETAV"
            print "  node  1          2          1          2          1          2          3          4          5          6"
            for nd in xrange(4):
                print "  {0:1d}     {1:10.4e} {2:10.4e} {3:10.4e} {4:10.4e} {5:10.4e} {6:10.4e} {7:10.4e} {8:10.4e} {9:10.4e} {10:10.4e}".format(\
                    nd+1, velocv[0,nd,az,asy], velocv[1,nd,az,asy], xhidmiv[0,nd,az,asy], xhidmiv[1,nd,az,asy], betav[0,nd,az,asy], betav[1,nd,az,asy], \
                    betav[2,nd,az,asy], betav[3,nd,az,asy], betav[4,nd,az,asy], betav[5,nd,az,asy])
            print ""

            # Xe/Sm
            print "Xenon/Samarium"
            print "        DFIV       DXEV       DPMV       DSMV       XXEABV                XSMABV"
            print "  node                                              1          2          1          2"
            for nd in xrange(4):
                print "  {0:1d}     {1:10.4e} {2:10.4e} {3:10.4e} {4:10.4e} {5:10.4e} {6:10.4e} {7:10.4e} {8:10.4e}".format(\
                    nd+1, dfiv[nd,az,asy], dxev[nd,az,asy], dpmv[nd,az,asy], dsmv[nd,az,asy], xxeabv[0,nd,az,asy], xxeabv[1,nd,az,asy], \
                    xsmabv[0,nd,az,asy], xsmabv[1,nd,az,asy])
            print ""

            # Corner point fluxes
            print "SWCPV"
            print "        NORTHWEST             NORTHEAST             SOUTHWEST             SOUTHEAST"
            print "  node  1          2          1          2          1          2          1          2"
            for nd in xrange(4):
                print "  {0:1d}     {1:10.4e} {2:10.4e} {3:10.4e} {4:10.4e} {5:10.4e} {6:10.4e} {7:10.4e} {8:10.4e}".format(\
                    nd+1, swcpv[0,0,nd,az,asy], swcpv[0,1,nd,az,asy], swcpv[1,0,nd,az,asy], swcpv[1,1,nd,az,asy], swcpv[2,0,nd,az,asy], \
                    swcpv[2,1,nd,az,asy], swcpv[3,0,nd,az,asy], swcpv[3,1,nd,az,asy])
            print ""

            # Burnup and Rod fraction
            print "Misc."
            print "  node  BURNUP     IFRACTV"
            for nd in xrange(4):
                print "  {0:1d}     {1:10.4e} {2:10.4e}".format(nd+1, burnup[nd,az,asy], ifractv[nd,az,asy])
            print ""

    print "Radial Powers"
    for asy in xrange(nasy):
        powasy = asy2powasy(asy+1) -1

        # Print assembly header
        if powasy >= 0:
            print "    ASSEMBLY {0:4d}".format(asy+1)
            for i in xrange(radpow.shape[0]):
                print '      ' + ' '.join('%6.4f' % radpow[i,j,powasy] for j in xrange(radpow.shape[1]))
            print ""
