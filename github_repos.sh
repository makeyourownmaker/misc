#!/bin/bash

# Get number of github repos and update beeminder if number has increased

set -euo pipefail

PATH=/usr/local/bin:/usr/bin:/bin:~/bin

GOAL='repos'

github_repos=`curl -s https://api.github.com/users/makeyourownmaker/repos | jq '.[] | {name: .name}' | grep -c name`
#echo $github_repos # DEBUG
#exit

bee_repos=`bmndr $GOAL | awk 'BEGIN { FS=" " } /datapoint/ {print $1}' | head -1`
#echo "github: $github_repos" # DEBUG
#echo "beemnd: $bee_repos"

if [[ $github_repos -gt $bee_repos ]]; then
  inc=$((github_repos-bee_repos))
  bmndr $GOAL $inc > /dev/null
  echo "old: $bee_repos"
  echo "new: $github_repos"
  echo "inc: $inc"
fi

