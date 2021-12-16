#!/bin/bash

###################################################################
# Script Name	  : push_modify.sh
# Description	  : When 'Push to next stage is clicked', this script rearranges
#               : the temp folder structure to facilitate next step.
# Args          : none.
# Author        : Milind Agarwal
# Lab           : Markle Lab, JHBSPH
# Email         : magarw10@jhu.edu
###################################################################


# The purpose of this bash script is to faciliate pushing results from one stage of the analysis to the next.

# First, clean out only the files in the TEMP directory.
find ./temp/ -maxdepth 1 -type f -exec rm "{}" \;

# Then cd into the TEMP dir
cd temp

# Then, copy results from RES to TEMP.
cp res/* .

# Clean out the contents of the RES folder.
find ./res/ -maxdepth 1 -type f -exec rm "{}" \;

# Clean out any ZIPs because we're not pushing those.
# rm -f *.vcf
rm -f *.zip

# That's it.
