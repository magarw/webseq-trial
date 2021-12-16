###################################################################
# Script Name	: remove_list.py
# Description	: Generate a remove.txt file for given .fam file
# Args          : FAM file.
# Author        : Milind Agarwal
# Lab           : Markle Lab, JHBSPH
# Email         : magarw10@jhu.edu
###################################################################


import argparse
parser = argparse.ArgumentParser(description='Generate a remove.txt file for given .fam file')
parser.add_argument('ifile')
args = parser.parse_args()
INFILE = args.ifile

import pandas as pd
import numpy as np
# PATH = '../data/plink_top'
a = pd.read_csv(INFILE + '.fam', sep = ' ', header = -1)
# First column is the FAM ID column
famid = a.isna()[0]
out = a.loc[famid.values,:1]
out[0] = 'NA'
np.savetxt('./data/remove.txt', out.values, fmt='%s')
