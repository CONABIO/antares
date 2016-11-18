#!/bin/sh
echo `hostname`
source /LUSTRE/MADMEX/code/madmex/resources/gridengine/nodo.txt

echo `hostname`>> /LUSTRE/MADMEX/staging/tester.log
echo $1 >> /LUSTRE/MADMEX/staging/tester.log
echo $2 >> /LUSTRE/MADMEX/staging/tester.log
