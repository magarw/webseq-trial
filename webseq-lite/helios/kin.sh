#!/bin/bash

###################################################################
# Script Name	  : kin.sh
# Description	  : Controller script to generate sex and kinship analyses through KING.
# Args          : PLINK file prefix
# Author        : Milind Agarwal
# Lab           : Markle Lab, JHBSPH
# Email         : magarw10@jhu.edu
###################################################################


INFILE=$1

# Default saving is to the same directory as input. We can keep it like this because all this is going to happen on
# the server anyways.

./plink/plink --file $INFILE --make-bed --out $INFILE

# This generates a list of data points we need to remove if we are to use the relationship check.
python3 remove_list.py $INFILE

# Now we'll remove those individuals
./plink/plink --file $INFILE --remove ./data/remove.txt --make-bed -out $INFILE

# Now we'll run the kinship analysis pipeline
./king -b "${INFILE}.bed" --kinship --prefix $INFILE
# ./king -b "${INFILE}.bed" --kinship --prefix $INFILE

# Now we'll start doing the sex pipeline as well.
./plink/plink --file $INFILE --out $INFILE --check-sex

# --------------- FORMATTING ----------
# Now we'll format the kinship output and expose it as a CSV

python3 gen_csv_kin_sex.py $INFILE
rm "${INFILE}_SEXCHECK.csv"
