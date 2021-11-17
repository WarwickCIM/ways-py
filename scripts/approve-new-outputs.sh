#!/bin/bash
# set -xe

cd $(git rev-parse --show-toplevel)
files=$(git ls-files -o --exclude-standard)

# Specific to .json and .png files for now.
# No git add here (currently handled by the git aliases).
for f in $files
do
   if [[ $f == *.new.json ]]
   then
      f_name=${f%%.*}
      f_old="$f_name.json"
      mv $f $f_old
   fi
   if [[ $f == *.new.svg ]]
   then
      f_name=${f%%.*}
      f_old="$f_name.svg"
      mv $f $f_old
   fi
done
