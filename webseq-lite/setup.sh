#!/bin/bash

###################################################################
# Script Name	: setup.sh
# Description	: Required for setup on MacOS systems. Can be called via the automator executable.
# Args        : None.
# Author      : Milind Agarwal
# Lab         : Markle Lab, JHBSPH
# Email       : magarw10@jhu.edu
###################################################################

echo '  Step 0/7: Changing location the directory of the bash script.'
cd -- "$(dirname "$BASH_SOURCE")"

echo '  Step 1/7: Setting up ANNOVAR within the web interface.'
find annovar/ -type f -name "*.pl" -exec cp {} helios/annovar/  \;

echo '  Step 2/7: Downloading and installing HomeBrew Package Manager.'
cd /usr/local/
mkdir homebrew >/dev/null 2>&1 && curl -L https://github.com/Homebrew/brew/tarball/master | tar xz --strip 1 -C homebrew >/dev/null 2>&1

echo '  Step 3/7: Installing GCC Compiler through Homebrew.'
brew install gcc

cd -- "$(dirname "$BASH_SOURCE")"
echo '  Step 4/7: Creating virtual environment for Python dependencies.'
python3 -m venv webseq_env/ >/dev/null 2>&1
source webseq_env/bin/activate
cd helios
echo '  Step 5/7: Installing Python dependencies.'
pip3 install -r requirements.txt

chmod +x *.sh
chmod +x tkin.py
cd ..

sh fix_gcc.sh

cd helios
echo '  Step 6/7: Creating base image.'
python3 igvreports/test/igv_reports/report.py ./data/init.bed https://s3.amazonaws.com/igv.broadinstitute.org/genomes/seq/1kg_v37/human_g1k_v37_decoy.fasta --tracks https://s3.amazonaws.com/igv.org.genomes/hg19/refGene.sorted.b37.txt.gz  --output ./static/igvjs_viewer.html

deactivate
cd ..
echo '  Step 7/7: Finished successfully! :) '

echo $'\n'
printf "\033[32mSetup was successful! You can close this window\033[0m\n"
echo $'\n'
