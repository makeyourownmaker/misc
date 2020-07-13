#!/bin/bash

# Get stackoverflow 'Strunk & White' edits and possibly update beeminder goal

set -euo pipefail

PATH=/usr/local/bin:/usr/bin:/bin:~/bin
SOID=<stackoverflow ID>
GOAL=<beeminder goal>
EDITS="$HOME/tmp/remaining_edits.txt"

curl -s "https://data.stackexchange.com/stackoverflow/csv/1554923?UserId=$SOID" -o $EDITS
re_edits=`tail -1 $EDITS | sed 's/"//g'` # remaining edits
so_edits=$((80-re_edits))
#echo "re_edits:   $re_edits" # DEBUG
#echo "so_edits:   $so_edits" # DEBUG
#exit

bee_edits=`bmndr $GOAL | awk 'BEGIN { FS=" " } /datapoint/ {print $1}' | head -1`
#echo "bee_edits:  $bee_edits" # DEBUG
#exit

if [[ $so_edits -gt $bee_edits ]]; then
  bmndr $GOAL $so_edits > /dev/null
  echo "old: $bee_edits"
  echo "new: $so_edits"
  echo "inc: $((so_edits-bee_edits))"
fi

