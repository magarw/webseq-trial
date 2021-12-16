#!/bin/bash
###################################################################
# Script Name	  : zipmeup.sh
# Description	  : zip files up
# Args          : none.
# Author        : Rayz Ghimire
# Lab           : Markle Lab, VUMC
# Email         : k.ghimire@vumc.org
###################################################################


cd temp/res
zip fastqtovcfresults.zip *.vcf
cd ..
cd ..
