#!/bin/bash

###################################################################
# Script Name	  : gen_pcs.sh
# Description	  : Generates PCs for ancestry visualziation
# Args          : PLINK file prefix
# Author        : Milind Agarwal
# Lab           : Markle Lab, JHBSPH
# Email         : magarw10@jhu.edu
###################################################################



## First, we need to use the common markers generated by the python script
## to extract the markers in sample from all three reference files.

INFILE=$1

./plink/plink --bfile ./Datasets/ancestry_data/chr1-4 --extract ./data/common_markers.txt --make-bed --out ./Datasets/ancestry_data/chr1-4_extr
./plink/plink --bfile ./Datasets/ancestry_data/chr5-8 --extract ./data/common_markers.txt --make-bed --out ./Datasets/ancestry_data/chr5-8_extr
./plink/plink --bfile ./Datasets/ancestry_data/chr9-X --extract ./data/common_markers.txt --make-bed --out ./Datasets/ancestry_data/chr9-X_extr

## Then, we will attempt to merge these reduced files one by one.
./plink/plink --bfile ./Datasets/ancestry_data/chr1-4_extr --bmerge ./Datasets/ancestry_data/chr5-8_extr.bed ./Datasets/ancestry_data/chr5-8_extr.bim ./Datasets/ancestry_data/chr5-8_extr.fam --make-bed --out ./Datasets/ancestry_data/chr1-8_extr
./plink/plink --bfile ./Datasets/ancestry_data/chr1-8_extr --bmerge ./Datasets/ancestry_data/chr9-X_extr.bed ./Datasets/ancestry_data/chr9-X_extr.bim ./Datasets/ancestry_data/chr9-X_extr.fam --make-bed --out ./Datasets/ancestry_data/chr1-X_extr

## USE BASH IF THEN STATMENTS---- UP---I should probably build in functionality in the above merges for handling merge MISSNP failures.

## Next, we will try to merge the sample with the reference...
./plink/plink --bfile ./Datasets/ancestry_data/chr1-X_extr --bmerge "${INFILE}.bed" "${INFILE}.bim" "${INFILE}.fam" --make-bed --out ./Datasets/ancestry_data/merge
./plink/plink --bfile $INFILE --flip ./Datasets/ancestry_data/merge-merge.missnp --make-bed --out "${INFILE}_flip"
./plink/plink --bfile ./Datasets/ancestry_data/chr1-X_extr --bmerge "${INFILE}_flip.bed" "${INFILE}_flip.bim" "${INFILE}_flip.fam" --make-bed --out ./Datasets/ancestry_data/merge2

./plink/plink --bfile "${INFILE}_flip" --exclude ./Datasets/ancestry_data/merge2-merge.missnp --make-bed --out "${INFILE}_flip_exclude"
./plink/plink --bfile ./Datasets/ancestry_data/chr1-X_extr --exclude ./Datasets/ancestry_data/merge2-merge.missnp --make-bed --out ./Datasets/ancestry_data/chr1-X_extr_exclude

## Reattempt the merge
./plink/plink --bfile ./Datasets/ancestry_data/chr1-X_extr_exclude --bmerge "${INFILE}_flip_exclude.bed" "${INFILE}_flip_exclude.bim" "${INFILE}_flip_exclude.fam" --make-bed --out ./Datasets/ancestry_data/merge3
./plink/plink --bfile ./Datasets/ancestry_data/merge3 --pca --out ./Datasets/ancestry_data/merge3_pca
