#!/bin/bash
# set -xe

cd $(git rev-parse --show-toplevel)
files=$(git ls-files -o --exclude-standard)

# Specific to .json files for now.
for f in $files
do
   if [[ $f == *.new.json ]]
   then
      rm $f $f_old
   fi
done
