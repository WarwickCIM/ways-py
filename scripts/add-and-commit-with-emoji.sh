#!/bin/bash
# set -xe

# Ideally, our refactoring aliases would just pass all arguments through unchanged to git commit, and
# then patch the commit message with the appropriate emoji. Unfortunately argument expansion and
# string-valued arguments are a hot mess, and I couldn't get it to work.
# This retains the flavour of how I'd like it work, in case someone eventually figures it out.
git commit -a -m "$1"
prev_msg=$(git log -1 --pretty=%B)
git commit --amend -m "$2 : ${prev_msg}"
