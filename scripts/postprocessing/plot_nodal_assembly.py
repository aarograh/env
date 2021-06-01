#!/usr/bin/python2
import sys
import h5py
import numpy as np
import pylab as plt
import matplotlib.tri as mtri

A=21.5/2.
V=A*A
nstate=1
h5=h5py.File(sys.argv[1])
if len(sys.argv) > 2:
  dataset = sys.argv[2]
else:
  dataset='ADF'

#5a
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
nnode=73

#2a
# amap = [[0]]
# nxy=1
# nnode=1

#4a
# amap=[[0,1],[2,3]]
# nxy=2
# nnode=9

grp=0
axial=0

for st in xrange(1,nstate+1):
    keff=h5["/STATE_"+"{0:04d}".format(st)+'/keff'].value
    cur=h5["/STATE_"+"{0:04d}".format(st)+'/ASSEMBLY_XS/CUR'].value
    adf=h5["/STATE_"+"{0:04d}".format(st)+'/ASSEMBLY_XS/ADF'].value
    sfx=h5["/STATE_"+"{0:04d}".format(st)+'/ASSEMBLY_XS/SFLX'].value
    chi=h5["/STATE_"+"{0:04d}".format(st)+'/ASSEMBLY_XS/CHI'].value
    flx=h5["/STATE_"+"{0:04d}".format(st)+'/ASSEMBLY_XS/FLUX'].value
    nxf=h5["/STATE_"+"{0:04d}".format(st)+'/ASSEMBLY_XS/NXSF'].value
    xsr=h5["/STATE_"+"{0:04d}".format(st)+'/ASSEMBLY_XS/XSRM'].value
    xss=h5["/STATE_"+"{0:04d}".format(st)+'/ASSEMBLY_XS/XSS'].value
    data_plot=h5["/STATE_"+"{0:04d}".format(st)+'/ASSEMBLY_XS/'+dataset].value

    def plotval(asy,nz,nd,g,f):
        #if(f==0 or f==1):
        #  return -cur[asy,nz,nd,g,f] #/sfx[asy,nz,nd,g,f]
        #return cur[asy,nz,nd,g,f]  /sfx[asy,nz,nd,g,f]
        #return adf[f,g,nd,nz,asy]
        #return sfx[asy,nz,nd,g,f]
        #return flx[asy,nz,nd,g]
        #return xsr[asy,nz,nd,g]
        return data_plot[f,g,nd,nz,asy]

    ind=0
    pltval=np.zeros(nnode*4)
    xval=np.zeros(nnode*5)
    yval=np.zeros(nnode*5)
    triag=[]
    for ay in xrange(nxy):
        for ax in xrange(nxy):
            asy=amap[ay][ax]
            if(asy>=0):
                #xval[ind*5:(ind+1)*5]=ax+np.array([0.0,0.0,0.25,0.5,0.5])
                #yval[ind*5:(ind+1)*5]=ay+np.array([0.0,0.5,0.25,0.0,0.5])
                xval[ind*5:(ind+1)*5]=ax+np.array([0.0,0.0,0.5,1.0,1.0])
                yval[ind*5:(ind+1)*5]=ay+np.array([0.0,1.0,0.5,0.0,1.0])
                triag.append([ind*5  ,ind*5+1,ind*5+2])
                triag.append([ind*5  ,ind*5+2,ind*5+3])
                triag.append([ind*5+2,ind*5+3,ind*5+4])
                triag.append([ind*5+1,ind*5+2,ind*5+4])
                pltval[ind*4  ]=plotval(asy,axial,0,grp,0)
                pltval[ind*4+1]=plotval(asy,axial,0,grp,1)
                pltval[ind*4+2]=plotval(asy,axial,0,grp,2)
                pltval[ind*4+3]=plotval(asy,axial,0,grp,3)
                ind+=1

    T=mtri.Triangulation(xval,-yval,triag)
    fig = plt.figure()
    ax = fig.gca()
    ax.set_xticks(np.arange(0, nxy, 1.))
    ax.set_yticks(np.arange(0, -nxy, -1.))
    plt.tripcolor(T,pltval,shading='flat',vmin=-1,vmax=2)
    #plt.tripcolor(T,pltval,shading='flat')
    plt.colorbar()
    plt.grid()
    plt.show()

