#!/bin/bash
###################################################################
# Script Name	  : movefiles.sh
# Description	  : Moves files from temp folder into res.
# Args          : none.
# Author        : Milind Agarwal
# Lab           : Markle Lab, JHBSPH
# Email         : magarw10@jhu.edu
###################################################################


mkdir ./temp/res
cd temp
mv *.csv res/
cd ..
