#!/bin/bash
set -xe

cd $(git rev-parse --show-toplevel)
files=$(git ls-files -o --exclude-standard)

# Specific to .json files for now.
for f in $files
do
   if [[ $f == *.new.json ]]
   then
      f_name=${f%%.*}
      f_old="$f_name.json"
      mv $f $f_old
      git add $f_old
   fi
done
