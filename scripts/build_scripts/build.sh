#!/bin/bash

ARGS=$*
DIR=$PWD
BUILD=${DIR%MPACT_libs/*}
if [ -z "$BUILD" ]
then
  BUILD=${DIR%MPACT_Drivers/*}
elif [ $BUILD == $DIR ]
then
  BUILD=${DIR%MPACT_Drivers/*}
fi
STATUS=0

if [ $1 == 'all' ]
then
  echo "Cleaning entire build in directory $BUILD..."
  cd $BUILD/
  make clean
elif [ $1 == '.' ]
then
  echo "Cleaning only current directory $DIR..."
  make clean
else
  for CLEAN in $ARGS
  do
    if [ $CLEAN == 'Driver' ]
    then
      echo "Cleaning directory $BUILD/MPACT_Drivers..."
      cd $BUILD/MPACT_Drivers
    elif [ $CLEAN == 'Helios' ]
    then
      echo "Cleaning directory $BUILD/MAPCT_HELIOSXS..."
      cd $BUILD/MPACT_HELIOSXS
    else
      echo "Cleaning directory $BUILD/MPACT_libs/$CLEAN..."
      cd $BUILD/MPACT_libs/$CLEAN
    fi
    NEWSTATUS=$?
    if [ $STATUS == 0 ]
    then
      STATUS=$NEWSTATUS
    fi
    if [ $STATUS == 0 ]
    then
      make clean
    fi
  done
fi

if [ $STATUS == 0 ]
then
  echo "Building in directory $DIR..."
  cd $DIR
  make -j16
else
  echo "Error when cleaning directory $BUILD/MPACT_libs/$CLEAN: Build will not proceed..."
fi
