#!/bin/bash

###################################################################
# Script Name	  : convert.sh
# Description	  : Applies make bed from PLINK to bfiles.
# Args          : PLINK file prefix
# Author        : Milind Agarwal
# Lab           : Markle Lab, JHBSPH
# Email         : magarw10@jhu.edu
###################################################################

# The purpose of this bash script is to ensure that we generate binary files for further downstream analyses.

INFILE=$1

# Default saving is to the same directory as input. We can keep it like this because all this is going to happen on
# the server anyways.

# In case there's issues with the formatting of the files.
./plink/plink --bfile $INFILE --make-bed --out $INFILE

# Then, we would convert it to the FAM PED
./plink/plink --bfile $INFILE --out $INFILE --recode
