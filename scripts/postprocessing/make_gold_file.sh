#!/bin/bash
CLIST=$@

for CASE in $CLIST; do
echo "============================================="
echo " Running CASE = $CASE"
echo "============================================="
cp $CASE $CASE.old
rm $CASE
NEWCASE=$CASE
CASE=$CASE.old
STATES=`h5ls $CASE | grep STATE | cut -d' ' -f1`
for STATE in $STATES; do
echo $STATE
h5copy -i $CASE -o $NEWCASE -s /${STATE} -d /EXPECTED/${STATE} -p
done
h5copy -i $CASE -o $NEWCASE -s /CORE -d /CORE -p
rm $CASE
done
