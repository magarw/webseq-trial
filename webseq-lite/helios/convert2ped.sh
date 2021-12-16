#!/bin/bash

###################################################################
# Script Name	  : gen_pcs.sh
# Description	  : Generates binary fileset file from ped/map
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
./plink/plink --file $INFILE --out $INFILE --make-bed
