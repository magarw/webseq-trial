#!/bin/bash

###################################################################
# Script Name	  : movegenepanel.sh
# Description	  : Moves files from genepanel folder into res.
# Args          : none.
# Author        : Rayz Ghimire
# Lab           : Markle Lab, VUMC
# Email         : k.ghimire@vumc.org 
###################################################################

mkdir ./temp/res
cd genepanel
mv *.csv ../temp/res
cd ..
