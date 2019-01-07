#!/usr/bin/python2
import sys
import h5py
import numpy as np
import pylab as plt
import matplotlib.tri as mtri

A=21.5/2.
V=A*A
nstate=1
h5=h5py.File('5a-2d.h5')
amap=[[ 0,  1,  2,  3,  4,  5,  6,  7,  8],
      [ 9, 10, 11, 12, 13, 14, 15, 16, 17],
      [18, 19, 20, 21, 22, 23, 24, 25, 26],
      [27, 28, 29, 30, 31, 32, 33, 34, 35],
      [36, 37, 38, 39, 40, 41, 42, 43, 44],
      [45, 46, 47, 48, 49, 50, 51, 52, -1],
      [53, 54, 55, 56, 57, 58, 59, 60, -1],
      [61, 62, 63, 64, 65, 66, 67, -1, -1],
      [68, 69, 70, 71, 72, -1, -1, -1, -1]]
nxy=9
nnode=257

#h5=h5py.File('4a-2d.h5')
#amap=[[0,1],[2,3]]
#nxy=2
#nnode=9

grp=0

for st in xrange(1,nstate+1):
    keff=h5["/STATE_"+"{0:04d}".format(st)+'/keff'].value
    cur=h5["/STATE_"+"{0:04d}".format(st)+'/NODAL_XS/CUR'].value
    adf=h5["/STATE_"+"{0:04d}".format(st)+'/NODAL_XS/ADF'].value
    sfx=h5["/STATE_"+"{0:04d}".format(st)+'/NODAL_XS/SFLX'].value
    chi=h5["/STATE_"+"{0:04d}".format(st)+'/NODAL_XS/CHI'].value
    flx=h5["/STATE_"+"{0:04d}".format(st)+'/NODAL_XS/FLUX'].value
    nxf=h5["/STATE_"+"{0:04d}".format(st)+'/NODAL_XS/NXSF'].value
    xsr=h5["/STATE_"+"{0:04d}".format(st)+'/NODAL_XS/XSRM'].value
    xss=h5["/STATE_"+"{0:04d}".format(st)+'/NODAL_XS/XSS'].value

    def plotval(asy,nz,nd,g,f):
        #if(f==0 or f==1):
        #  return -cur[asy,nz,nd,g,f] #/sfx[asy,nz,nd,g,f]
        #return cur[asy,nz,nd,g,f]  /sfx[asy,nz,nd,g,f]
        return adf[asy,nz,nd,g,f]
        #return sfx[asy,nz,nd,g,f]
        #return flx[asy,nz,nd,g]
        #return xsr[asy,nz,nd,g]

    ind=0
    pltval=np.zeros(nnode*4)
    xval=np.zeros(nnode*5)
    yval=np.zeros(nnode*5)
    triag=[]
    for ay in xrange(nxy):
        for ax in xrange(nxy):
            asy=amap[ay][ax]
            if(asy>=0):
                #node 1
                if(ax>0 and ay>0):
                  xval[ind*5:(ind+1)*5]=ax+np.array([0.0,0.0,0.25,0.5,0.5])
                  yval[ind*5:(ind+1)*5]=ay+np.array([0.0,0.5,0.25,0.0,0.5])
                  triag.append([ind*5  ,ind*5+1,ind*5+2])
                  triag.append([ind*5  ,ind*5+2,ind*5+3])
                  triag.append([ind*5+2,ind*5+3,ind*5+4])
                  triag.append([ind*5+1,ind*5+2,ind*5+4])
                  pltval[ind*4  ]=plotval(asy,0,0,grp,0)
                  pltval[ind*4+1]=plotval(asy,0,0,grp,1)
                  pltval[ind*4+2]=plotval(asy,0,0,grp,2)
                  pltval[ind*4+3]=plotval(asy,0,0,grp,3)
                  ind+=1
                #node 2
                if(ay>0):
                  xval[ind*5:(ind+1)*5]=ax+np.asarray([0.5,0.5,0.75,1.0,1.0])
                  yval[ind*5:(ind+1)*5]=ay+np.asarray([0.0,0.5,0.25,0.0,0.5])
                  triag.append([ind*5  ,ind*5+1,ind*5+2])
                  triag.append([ind*5  ,ind*5+2,ind*5+3])
                  triag.append([ind*5+2,ind*5+3,ind*5+4])
                  triag.append([ind*5+1,ind*5+2,ind*5+4])
                  pltval[ind*4  ]=plotval(asy,0,1,grp,0)
                  pltval[ind*4+1]=plotval(asy,0,1,grp,1)
                  pltval[ind*4+2]=plotval(asy,0,1,grp,2)
                  pltval[ind*4+3]=plotval(asy,0,1,grp,3)
                  ind+=1
                #node 3
                if(ax>0):
                  xval[ind*5:(ind+1)*5]=ax+np.asarray([0.0,0.0,0.25,0.5,0.5])
                  yval[ind*5:(ind+1)*5]=ay+np.asarray([0.5,1.0,0.75,0.5,1.0])
                  triag.append([ind*5  ,ind*5+1,ind*5+2])
                  triag.append([ind*5  ,ind*5+2,ind*5+3])
                  triag.append([ind*5+2,ind*5+3,ind*5+4])
                  triag.append([ind*5+1,ind*5+2,ind*5+4])
                  pltval[ind*4  ]=plotval(asy,0,2,grp,0)
                  pltval[ind*4+1]=plotval(asy,0,2,grp,1)
                  pltval[ind*4+2]=plotval(asy,0,2,grp,2)
                  pltval[ind*4+3]=plotval(asy,0,2,grp,3)
                  ind+=1
                #node 4
                xval[ind*5:(ind+1)*5]=ax+np.array([0.5,0.5,0.75,1.0,1.0])
                yval[ind*5:(ind+1)*5]=ay+np.array([0.5,1.0,0.75,0.5,1.0])
                triag.append([ind*5  ,ind*5+1,ind*5+2])
                triag.append([ind*5  ,ind*5+2,ind*5+3])
                triag.append([ind*5+2,ind*5+3,ind*5+4])
                triag.append([ind*5+1,ind*5+2,ind*5+4])
                pltval[ind*4  ]=plotval(asy,0,3,grp,0)
                pltval[ind*4+1]=plotval(asy,0,3,grp,1)
                pltval[ind*4+2]=plotval(asy,0,3,grp,2)
                pltval[ind*4+3]=plotval(asy,0,3,grp,3)
                ind+=1

    T=mtri.Triangulation(xval,-yval,triag)
    fig = plt.figure()
    ax = fig.gca()
    ax.set_xticks(np.arange(0, nxy, 1.))
    ax.set_yticks(np.arange(0, -nxy, -1.))
    plt.tripcolor(T,pltval,shading='flat')
    plt.colorbar()
    plt.grid()
    plt.show()
