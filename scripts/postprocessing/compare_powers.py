#!/usr/bin/python
import numpy as np
import h5py as h5
import sys

nargs = len(sys.argv)
if nargs == 3:
  reffile = h5.File(sys.argv[1],"r")
  refstate = 1
  altfile = h5.File(sys.argv[2],"r")
  altstate = 1
elif nargs == 5:
  reffile = h5.File(sys.argv[1],"r")
  refstate = int(sys.argv[2])
  altfile = h5.File(sys.argv[3],"r")
  altstate = int(sys.argv[4])
else:
  print 'Requies two hdf 5 files, and optionally a state number after each file.'
  sys.exit(1)

refstatestr = str(refstate)
altstatestr = str(altstate)

order = 1
while True:
  order = order*10
  if refstate < order:
    refstatestr = '0' + refstatestr
  if altstate < order:
    altstatestr = '0' + altstatestr
  if order == 1000:
    break

refpowername = '/STATE_' + refstatestr + '/pin_powers'
altpowername = '/STATE_' + altstatestr + '/pin_powers'
refaxialname = '/CORE/axial_mesh'
altaxialname = '/CORE/axial_mesh'

refpower = reffile[refpowername]
refkeff = reffile['/STATE_' + refstatestr + '/keff']
bool = '/STATE_' + refstatestr + '/outers' in reffile
if bool:
  refouter = reffile['/STATE_' + refstatestr + '/outers']
  reftime = reffile['/STATE_' + refstatestr + '/outer_timer']
else:
  refouter = 0
refaxial = reffile[refaxialname]
altpower = altfile[altpowername]
altkeff = altfile['/STATE_' + altstatestr + '/keff']
bool = '/STATE_' + altstatestr + '/outers' in altfile
if bool:
  altouter = altfile['/STATE_' + altstatestr + '/outers']
  alttime = altfile['/STATE_' + altstatestr + '/outer_timer']
else:
  altouter = 0
altaxial = altfile[altaxialname]

# Check for sigmas
mcref = '/STATE_' + refstatestr + '/keff_sigma' in reffile
if mcref:
  keffsigma = reffile['/STATE_' + refstatestr + '/keff_sigma']
  refpowersigma = reffile['/STATE_' + refstatestr + '/pin_powers_sigma']

# Adjust the meshes so they're aligned (mainly for keno outputs)
refaxial = refaxial + (altaxial[0] - refaxial[0])

if len(refaxial) < len(altaxial):
  print 'Reference mesh is coarser than alternate mesh.  Switch order of inputs.'
  print 'reference mesh:',refaxial
  print 'alternate mesh:',altaxial[...]
  sys.exit(3)

npinx = len(altpower)
npiny = len(altpower[0,...])
nplanes = len(altpower[0,0,...])
nassem = len(altpower[0,0,0,...])
diffpower = np.zeros((npinx,npiny,nplanes,nassem))
if mcref:
  diffpowersigma = np.zeros((npinx,npiny,nplanes,nassem))

kref = 0
for k in range(nplanes-1):
  while refaxial[kref] < altaxial[k+1]:
    if refaxial[kref+1] > altaxial[k+1]:
      height = altaxial[k+1]-refaxial[kref]
    elif refaxial[kref] < altaxial[k]:
      height = refaxial[kref+1]-altaxial[k]
    else:
      height = refaxial[kref+1]-refaxial[kref]
    diffpower[:,:,k,:] += refpower[:,:,kref,:]*height
    if mcref:
      diffpowersigma[:,:,k,:] = np.sqrt(diffpowersigma[:,:,k,:]*diffpowersigma[:,:,k,:] + height*height*refpowersigma[:,:,kref,:]*refpowersigma[:,:,kref,:])
    kref += 1
  height = altaxial[k+1]-altaxial[k]
  diffpower[:,:,k,:] = altpower[:,:,k,:] - diffpower[:,:,k,:]/height
  if mcref:
    diffpowersigma[:,:,k,:] /= height
  if refaxial[kref] > altaxial[k+1]:
    kref -= 1

maxx,maxy,maxz,maxasy = np.unravel_index(np.argmax(np.abs(diffpower)), diffpower.shape)
size = npinx * npiny * nplanes * nassem
max = np.amax(np.abs(diffpower[...]))*100
rms = np.sqrt(np.sum(diffpower[...] * diffpower[...]) / size)*100
diffkeff = (altkeff[...] - refkeff[...])*100000.0
if mcref:
  diffkeffsigma = keffsigma[...]*100000.0
  maxsigma = diffpowersigma[maxx,maxy,maxz,maxasy]
  rmssigma = np.sqrt(np.sum(2.0*2.0*diffpower[...]*diffpower[...]*diffpowersigma[...]*diffpowersigma[...]/(size*size)))
if mcref:
  print ' Reference k-eff: ' + ("%1.6f" % refkeff[...]) + ' +/- ' + ("%1.6f" % diffkeffsigma)
  print ' Alernate k-eff:  ' + ("%1.6f" % altkeff[...])
  print ' Differences:'
  print '           k-eff: ' + ("%.6f" % diffkeff) + ' +/- ' + ("%1.6f" % diffkeffsigma)
  print '           RMS:   ' + ("%.6f" % rms) + ' +/- ' + ("%1.6f" % rmssigma)
  print '           Max:   ' + ("%.6f" % max) + ' +/- ' + ("%1.6f" % maxsigma) + ', Location: pin (' + ("%i" % maxx) + ',' + ("%i" % maxy) + '), axial level ' + ("%i" % maxz) + ' of assembly ' + ("%i" %maxasy)
else:
  print ' Reference k-eff: ' + ("%1.6f" % refkeff[...])
  print ' Alernate k-eff:  ' + ("%1.6f" % altkeff[...])
  print ' Differences:'
  print '           k-eff: ' + ("%.6f" % diffkeff)
  print '           RMS:   ' + ("%.6f" % rms)
  print '           Max:   ' + ("%.6f" % max) + ', Location: pin (' + ("%i" % maxx) + ',' + ("%i" % maxy) + '), axial level ' + ("%i" % maxz) + ' of assembly ' + ("%i" %maxasy)
if refouter > 0:
  print ' Reference  ran in ' + str(reftime[...]) + ' seconds and ' + str(refouter[...]) + ' outers'
if altouter > 0:
  print ' Comparison ran in ' + str(alttime[...]) + ' seconds and ' + str(altouter[...]) + ' outers'
#print maxx,maxy,maxz,maxasy
#print altpower[:,:,maxz,maxasy]
#print diffpower[:,:,maxz,maxasy]
#print altpower[maxx,maxy,:,maxasy]
#print diffpower[maxx,maxy,:,maxasy]
#print refpower[...]
#print altpower[...]

print '\n'
