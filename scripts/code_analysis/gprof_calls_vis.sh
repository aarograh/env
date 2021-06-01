#!/bin/bash

# Run the executable compilied with gprof first
exe=$1
basename=$2
shift; shift
if [ $# -eq 1 ]
then
  copyname=$1
  cp $copyname $basename.out
fi

gprof $exe $basename.out.* > $basename.gprof
gprof2dot $basename.gprof > $basename.dot
dot $basename.dot -Tpng -o $basename.png
# visualize on ubuntu with eog
