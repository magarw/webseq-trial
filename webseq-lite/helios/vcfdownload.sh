#!/bin/bash
###################################################################
# Script Name	  : vcfdownload.sh
# Description	  : It copies and moves the intermediate files generated during the fastq to vcf generation. bam and bai files are moved to fastqfiles folder on desktop. All others are deleted.
# Args          : none.
# Author        : Rayz Ghimire
# Lab           : Markle Lab, VUMC
# Email         : k.ghimire@vumc.org
###################################################################




cd ../../../webseq_sandbox/forfastqtovcf/fastqtovcf
directory=`pwd`

rm *.dedup.*
rm *.txt
rm *.recal.*
rm *.g.vcf
mv *.bam /webseq_sandbox/forfastqtovcf/fastqfiles
mv *.bai /webseq_sandbox/forfastqtovcf/fastqfiles
#
mv SNPdb.vcf .SNPdb.vcf
mv SNPdb.vcf.idx .SNPdb.vcf.idx
#
mv *.vcf /webseq_sandbox/forfastqtovcf/fastqfiles
rm *.vcf*
#
mv .SNPdb.vcf SNPdb.vcf
mv .SNPdb.vcf.idx SNPdb.vcf.idx
