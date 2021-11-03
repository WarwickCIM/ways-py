#!/bin/bash
set -xe

cd $(git rev-parse --show-toplevel)
files=$(git ls-files -o --exclude-standard)

for f in $files
do
   if [[ $f == *.new.json ]]
   then
      echo $f
   fi
done
