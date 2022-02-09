#!/bin/bash -x

# Run the executable compilied with gprof first
exe=$1
basename=$2
shift; shift

gprof $exe $basename* > $basename.gprof
gprof2dot $basename.gprof > $basename.dot
dot $basename.dot -Tpng -o $basename.png
# visualize on ubuntu with eog
