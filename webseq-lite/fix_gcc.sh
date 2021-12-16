#!/bin/bash
###################################################################
# Script Name	: fix_gcc
# Description	: Has proved to be useful when GCC was not configured properly on MacOS.
# Args        : None.
# Author      : Milind Agarwal
# Lab         : Markle Lab, JHBSPH
# Email       : magarw10@jhu.edu
###################################################################


cd -- "$(dirname "$BASH_SOURCE")"
brew install gcc
cd /usr/local/opt/gcc/lib/gcc
mkdir 8
cp -r 9/ 8/
