#!/bin/bash

# Get stackoverflow reputation and update beeminder goal if it has increased
# WARNING: Watch out for problems with downvoting on stackoverflow

set -euo pipefail

PATH=/usr/local/bin:/usr/bin:/bin:~/bin

SOID=<stackoverflow ID>
GOAL=<beeminder goal>

# WARNING: Got to be careful with SO rep
#          Downvoting costs rep points
so_rep_full=`curl -s "https://api.stackexchange.com/2.2/users/$SOID/reputation-history?pagesize=100&site=stackoverflow" | gunzip | jq '[.items[].reputation_change] | add'`
#echo $so_rep_full # DEBUG
#exit

bee_rep=`bmndr $GOAL | awk 'BEGIN { FS=" " } /datapoint/ {print $1}' | head -1`
#echo $bee_rep # DEBUG
#exit

if [[ $so_rep_full -gt $bee_rep ]]; then
  bmndr $GOAL $so_rep_full > /dev/null
  echo "old: $bee_rep"
  echo "new: $so_rep_full"
  echo "inc: $((so_rep_full-bee_rep))"
fi

