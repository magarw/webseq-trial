#!/bin/bash
###################################################################
# Script Name	  : move_vcf_to_res.sh
# Description	  : Moves files from Sandbox to res.
# Args          : none.
# Author        : Milind Agarwal
# Lab           : Markle Lab, JHBSPH
# Email         : magarw10@jhu.edu
###################################################################
mkdir ./temp/res
cp ../../../webseq_sandbox/forfastqtovcf/fastqfiles/*.vcf /webseq/helios/temp/res/
