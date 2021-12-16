
###################################################################
# Script Name	  : gen_csv_kin_sex.py
# Description	  : Generates CSV files ready for download with right formatting
#                    for sex and kinship infernece.
# Args          : PLINK file prefix
# Author        : Milind Agarwal
# Lab           : Markle Lab, JHBSPH
# Email         : magarw10@jhu.edu
###################################################################



import pandas as pd
from os import path
import argparse
parser = argparse.ArgumentParser(description='Generate a the kinship CSV output ready for download')
parser.add_argument('ifile')
args = parser.parse_args()
INFILE = args.ifile

check_a = path.exists(INFILE + '.kin')
check_b = path.exists(INFILE + '.kin0')

if not check_a and check_b:
    b = pd.read_csv(INFILE + '.kin0', sep = '\t')
    out = pd.concat([b]).sort_values(by=['FID1', 'FID2', 'ID1', 'ID2'])

elif  not check_b and check_a:
    a = pd.read_csv(INFILE + '.kin', sep = '\t')

    cols_a = list(a.columns)
    cols_a[0] = 'FID1'
    a.columns = cols_a
    a['FID2'] = a['FID1']
    cols = ['FID1', 'ID1', 'FID2', 'ID2', 'N_SNP', 'HetHet', 'IBS0', 'Kinship']
    a = a[cols]

    out = pd.concat([a]).sort_values(by=['FID1', 'FID2', 'ID1', 'ID2'])
else:
# both are available.
    a = pd.read_csv(INFILE + '.kin', sep = '\t')
    b = pd.read_csv(INFILE + '.kin0', sep = '\t')

    cols_a = list(a.columns)
    cols_a[0] = 'FID1'
    a.columns = cols_a
    a['FID2'] = a['FID1']
    cols = ['FID1', 'ID1', 'FID2', 'ID2', 'N_SNP', 'HetHet', 'IBS0', 'Kinship']
    a = a[cols]

    out = pd.concat([a, b]).sort_values(by=['FID1', 'FID2', 'ID1', 'ID2'])

out = out.reset_index(drop=True)
out.to_csv(INFILE + '_kinshipScores.csv')

fp = open(INFILE + '.sexcheck')
line = fp.readline()
header = line.strip().split()
data = []
while True:
    # read a single line
    line = fp.readline()
    if not line:
        break
    line_info = line.strip().split()
    data.append(line_info)
fp.close()
out = pd.DataFrame(data, columns=header)
out.to_csv(INFILE + '_SEXCHECK.csv')
