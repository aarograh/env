#!/usr/bin/python2

import sys
import h5py
import numpy as np
import pylab as plt

h5=h5py.File('4a-2d.h5')
A=21.5/2.
V=A*A
nstate=1
amap=[[ 0,  1,  2,  3,  4,  5,  6,  7,  8],
      [ 9, 10, 11, 12, 13, 14, 15, 16, 17],
      [18, 19, 20, 21, 22, 23, 24, 25, 26],
      [27, 28, 29, 30, 31, 32, 33, 34, 35],
      [36, 37, 38, 39, 40, 41, 42, 43, 44],
      [45, 46, 47, 48, 49, 50, 51, 52,  0],
      [53, 54, 55, 56, 57, 58, 59, 60,  0],
      [61, 62, 63, 64, 65, 66, 67,  0,  0],
      [68, 69, 70, 71, 72,  0,  0,  0,  0]]

for st in xrange(1,nstate+1):
    keff=h5["/STATE_"+"{0:04d}".format(st)+'/keff'].value
    cur=h5["/STATE_"+"{0:04d}".format(st)+'/NODAL_XS/CUR'].value
    chi=h5["/STATE_"+"{0:04d}".format(st)+'/NODAL_XS/CHI'].value
    flx=h5["/STATE_"+"{0:04d}".format(st)+'/NODAL_XS/FLUX'].value
    nxf=h5["/STATE_"+"{0:04d}".format(st)+'/NODAL_XS/NXSF'].value
    xsr=h5["/STATE_"+"{0:04d}".format(st)+'/NODAL_XS/XSRM'].value
    xss=h5["/STATE_"+"{0:04d}".format(st)+'/NODAL_XS/XSS'].value

    nasy=flx.shape[0]
    for asy in xrange(nasy):
        for nd in xrange(4):
            col=np.multiply(xsr[asy,0,nd,:],flx[asy,0,nd,:])
            scat=np.transpose(xss[asy,0,nd,:,:]); scat[0,0]=0.0; scat[1,1]=0.0
            ssrc=np.dot(scat,flx[asy,0,nd,:])
            fsrc=chi[asy,0,nd,:]/keff*np.dot(nxf[asy,0,nd,:],flx[asy,0,nd,:])
            for g in xrange(2):
                print g, col[g], ssrc[g], fsrc[g], np.sum(cur[asy,0,nd,g,:]),-col[g]*V+ssrc[g]*V+fsrc[g]*V-np.sum(cur[asy,0,nd,g,:])*A 
            print "  "
        print "-------------------------------------------------------"
    
