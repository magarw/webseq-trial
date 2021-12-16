#!/bin/bash
###################################################################
# Script Name	  : zipmeup.sh
# Description	  : zip files up
# Args          : none.
# Author        : Milind Agarwal
# Lab           : Markle Lab, JHBSPH
# Email         : magarw10@jhu.edu
###################################################################


cd temp/res
zip annovar_results.zip *.csv
cd ..
cd ..
