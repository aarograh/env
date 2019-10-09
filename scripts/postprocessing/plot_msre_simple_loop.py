import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from collections import OrderedDict
from PIL import Image
import os
import sys


###############################################
# Reads CTF output data: Returns a dictionary
# with the first line of the text file is
# is the column headers
#
# @param: fname    file name
# @param: results  dictionary
###############################################
def readInput(fname):

    DataKeys =[]

    # Creates an empty ordered dictionary
    results = OrderedDict()

    # Opens the file, reads in the lines, closes the file
    f = open(fname, 'r')
    data = f.readlines()
    f.close()

    # iterates through the lines in thefile
    for i, line in enumerate(data):
        splitline = line.split()
        if i == 0:
            for key in splitline:
                DataKeys.append(str(key))
                results[str(key)] = []
        else:
            # adds the data to the right column
            for k, dat in enumerate(splitline):
                key = DataKeys[k]
                results[key].append(float(dat))

    return results

###############################################
# Builds the folders
#
# @param: listOfChannelIndices list of chans
# @param: directory                              current direct
###############################################
def BuildFolders(listOfChannelIndices,directory):

    # Builds folder for plotting all channels
    # on one plot
    folder = 'continuousPlot'
    cPath = directory+'/'+folder
    if not os.path.exists(cPath):
      os.makedirs(cPath)

    # Builds the plot folder
    #pPath = os.getcwd()+'/plots'
    #if not os.path.exists(pPath):
        #os.makedirs(pPath)


###############################################
# Removes unwanted channels from data frame
#
# @param: dataframe  data
# @param: chans      list of chans to remove
# @param: dfnew      New data frame
###############################################
def removeChans(df,chans):

    dfNew = df

    for i in chans:
        dfNew = dfNew[dfNew['Channel'] != i]
    return dfNew

###############################################
# Returns an array of plot levels and data
#
# @param: df       data
# @param: chan     channel
# @param: key       data key
# @param: plotLvls array of index levels
# @param: plotData the data
###############################################
def getChanData(df,chan,key):

    flowrev = [16,13,11,9,7]
    inCore = [3,4,5,6]

    plotLvls = np.array(df.loc[df['Channel']==chan,'Index'])
    plotData = np.array(df.loc[df['Channel']==chan,key])

    if chan in flowrev:
        plotData = plotData[::-1]
    return plotLvls, plotData

###############################################
# Changes the current directory to the channel
# directory to make plots
#
# @param: chan             channel
# @param: currentDirectory currnent directory
###############################################
def changeDirectory(chan,currentDirectory):

    folder = '/channel'+str(chan)
    newpath = currentDirectory+folder
    os.chdir(newpath)

###############################################
# Calculates the percent increase from the
# first data point in the data
#
# @param: Data
###############################################
def calcPercentChange(Data):

    Data = np.array(Data)

    ogData = Data[0]
    nextData = Data[1]

    # Percent increase
    increase = Data-ogData
    increase = increase/ogData*100.
    return increase

###############################################
# Returns the arrays and source/sink tags
# for species source terms
#
# @param: df            pandas data frame
# @param: spec          species of interest
# @param: chan          the channel
###############################################
def sourceConribution(df,spec,chan):

    ConArray = []
    returnArray = []
    tags = []

    for sor in spec:
        plotLvls, plotData = getChanData(df,chan,sor)
        ConArray.append(plotData)

    length = len(plotLvls)
    total = np.zeros(length)

    for sor in ConArray:
        total = total+sor
    for sor in ConArray:
        if np.sum(sor) < 0.:
            # zero if sor is a sink
            tags.append(0)
        else:
            # one is sor is a source
            tags.append(1)
            percent = np.absolute(sor)
            returnArray.append(percent)

    return returnArray, tags, plotLvls

###############################################
# Calculates the percent of xenon in the
# cicurlating bubbles
#
# @param: df       dataframe
# @param: chanVal channel value
###############################################
def calcPercentXe(df,chanVal):

    plotLvls, Xegas  = getChanData(df,chanVal,'XeGas')
    plotLvls, Xeliq  = getChanData(df,chanVal,'XeLiq')

    tot = Xegas + Xeliq

    return plotLvls,Xegas/tot

###############################################
# Formats plots for continuous plotting
# function
#
# @param: plt   pyplot object
# @param: ax    axis object
###############################################
def formatplot(plt,ax,labels=False):

    trans = 0.7

    # adds regions to the plot
    ax.axvspan(0,1,alpha=trans,facecolor='#404040') # Lower plenum of core
    ax.axvspan(1,16,alpha=trans,facecolor='#F16745') # core
    ax.axvspan(16,22,alpha=trans,facecolor='#FFC65D') # upper plenum and pump
    ax.axvspan(22,23,alpha=trans,facecolor='#e6e6d4') # HX
    ax.axvspan(23,32,alpha=trans,facecolor='#4CC3D9') # Turn around elbow
    ax.axvspan(32,47,alpha=trans,facecolor='#93648D') # downcomer
    ax.axvspan(47,48,alpha=trans,facecolor='#404040') # Lower plenum of core

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.85, box.height])
    # Adds ledgend
    if labels:
        leg = ax.legend(loc='upper right')
        outlet = ax.axvline(x=19,ls='--',c='k',lw=0.5,label='Bubble removal')
        inlet = ax.axvline(x=20,c='k',lw=0.7,label='Bubble addition')
        legElements = [Patch(facecolor='#F16745',label='Core',alpha=trans),
                   Patch(facecolor='#FFC65D',label='Pump/upper\nplenum',alpha=trans),
                   Patch(facecolor='#e6e6d4',label='HX',alpha=trans),
                   Patch(facecolor='#4CC3D9',label='Turn around\nelbow',alpha=trans),
                   Patch(facecolor='#93648D',label='Downcomer',alpha=trans),
                   Patch(facecolor='#404040',label='Core\ninlet',alpha=trans),
                   outlet,inlet]
        core = ax.legend(handles=legElements,loc='center left',bbox_to_anchor=(1,0.5))
        ax.add_artist(leg)
    else:
        outlet = ax.axvline(x=19,ls='--',c='k',lw=0.5,label='Bubble removal')
        inlet = ax.axvline(x=20,c='k',lw=0.7,label='Bubble addition')
        legElements = [Patch(facecolor='#F16745',label='Core',alpha=trans),
                   Patch(facecolor='#FFC65D',label='Pump/upper\nplenum',alpha=trans),
                   Patch(facecolor='#e6e6d4',label='HX',alpha=trans),
                   Patch(facecolor='#4CC3D9',label='Turn around\nelbow',alpha=trans),
                   Patch(facecolor='#93648D',label='Downcomer',alpha=trans),
                   Patch(facecolor='#404040',label='Core\ninlet',alpha=trans),
                   outlet,inlet]
        ax.legend(handles=legElements,loc='center left',bbox_to_anchor=(1,0.5))

    box = ax.get_position()
    plt.style.use('ggplot')
    plt.xlim(0,48)

###############################################
# Plots the continuous data
#
# @param: df    pandas data frame
###############################################
def plotChansConnectedfunct(df):

    # change directory
    os.chdir(baseDirectory+'/continuousPlot')

    dataframe = removeChans(df,[3,5,6])
    xaxis = [i for i in xrange(len(dataframe['Channel']))]

    # Plots the normal non-source term data
    plotStuff = list(dataframe)[2:]
    for i,key in enumerate(plotStuff):
        if key in precursors:
            pass
        else:
            yaxis = []
            for chan in chanOrder:
                plotLvls, plotData = getChanData(dataframe,chan,key)
                for j, data in enumerate(plotData):
                    yaxis.append(data)
            fig, ax = plt.subplots(figsize=(8.0,5.0))
            plt.title(key+' vs regions')
            try:
                plt.ylabel(key+' ['+DataUnits[i]+']')
            except:
                plt.ylabel(key)
            plt.xlabel('region')
            formatplot(plt,ax)
            plt.plot(xaxis,yaxis)
            plt.savefig(key+'.png',dpi=500)
            plt.close(fig)

    # Plots the percet xe in bubbles
    yaxis = []
    for chan in chanOrder:
        plotLvls, percentXeInGas = calcPercentXe(dataframe,chan)
        for j, data in enumerate(percentXeInGas):
            yaxis.append(data)
    fig, ax = plt.subplots(figsize=(8.0,5.0))
    plt.title('Fraction Xe in bubbles vs regions')
    plt.ylabel('Fraction Xe in bubbles')
    formatplot(plt,ax)
    plt.plot(xaxis,yaxis)
    plt.savefig('percentXeInBubbles.png',dpi=500)
    plt.close(fig)

    # Plots the precursors
    fig, ax = plt.subplots(figsize=(8.0,5.0))
    for j,key in enumerate(precursors):
        yaxis = []
        for chan in chanOrder:
            plotLvls, plotData = getChanData(dataframe,chan,key)
            for data in plotData:
                yaxis.append(data)
        plt.plot(xaxis,yaxis, label=labels[j],color=colors[j])
    formatplot(plt,ax,labels=True)
    plt.title('Neutron precursors vs regions')
    plt.ylabel('Atoms/$m^3$')
    plt.grid()
    plt.savefig('neutronPrecursors.png',dpi=500)
    plt.close(fig)

###############################################
# Makes a single image of data
#
# @param: files         A list of file names
# @param: vertical      # of images in the
#                                                       vertical direction
# @param: horizontal # of images in the
#                                                       horizontal direction
#
# Note: vertical*horizontal must equal number
#       of files
###############################################
def buildImage(files,vertical,horizontal):
    # sets the number of images in the horizontal and vertical directions
    imgVert = vertical
    imgHori = horizontal

    # single image size
    imgSize = np.array([800,500])

    resultSize = tuple([imgHori*imgSize[0],imgVert*imgSize[1]])

    result = Image.new('RGB', (resultSize),color=(255,255,255))

    for index, file in enumerate(files):
        path = os.path.expanduser(file)
        img = Image.open(path)
        img.thumbnail(tuple((imgSize)), Image.ANTIALIAS)
        w, h = img.size
        x = index/imgVert * imgSize[0]
        y = index%imgVert * imgSize[1]
        result.paste(img, (x, y, x + w, y + h))

    result.save('simple_loop_results.png')
###############################################################################
###############################################################################

# Reads data
fname = sys.argv[1]
data = readInput(fname)

# Converts to data frame
df = pd.DataFrame.from_dict(data)

# Gets the current working directory
#baseDirectory = os.getcwd() + '/plots'
baseDirectory = os.getcwd()

# List of channels
chanList = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]

# Order of channels starting from bottom plenum (channel 1)
chanOrder = [1,3,4,5,6,8,12,14,15,16,13,11,10,9,7,2]

# Builds the folders for each channel
BuildFolders(chanList,baseDirectory)

# Species and their named source term variables
#I = ['IFlux','IDecay']
#XeGas = ['XeGasTransLiq']
#XeLiq = ['XeLiqFlux','XeLiqDecayI','XeLiqDecay','XeLiqTransGas']
#species = [I,XeGas,XeLiq]
#speciesNames = ['Iodine','Xenon gas','Xenon liquid']

# List of data keys to plot
#PlottingData = list(data)[2:17]
PlottingData = list(data)[2:]

# Units for those data keys
DataUnits = ['C','bar','Fraction','cm','1/m','kg/$m^3$','kg/$m^3$',
   'kg/$m^3$','kg/$m^3$','kg/$m^3$','atoms/$m^3$','atoms/$m^3$','atoms/$m^3$',
   'atoms/$m^3$','atoms/$m^3$','atoms/$m^3$','Unitless','Unitless']

# Precursors
precursors = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6']

# Plot title
plotTitle = 'Steady State'

# Labels for precursors plot
labels = precursors
colors = ['b','g','r','c','m','y']

# Plots continuous data
plotChansConnectedfunct(df)

os.chdir(baseDirectory + '/continuousPlot')

files = ['simple_loop.png','XeGas.png',
        'IntArea.png','XeLiq.png']

#buildImage(files,2,2)
