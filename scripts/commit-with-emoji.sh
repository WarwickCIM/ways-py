#!/bin/bash
set -xe

prev_msg=$(git log -1 --pretty=%B)
git commit "$@"
git commit --amend -m "${prev_msg}"
