#!/bin/bash

# Get stackoverflow reputation and update beeminder goal if it has increased
# WARNING Watch out for problems with downvoting etc on stackoverflow
# TODO Replace NEG_REP kludge with jq fix
#      Why jq not handling negative numbers properly?

set -euo pipefail

PATH=/usr/local/bin:/usr/bin:/bin:~/bin

SOID=<stackoverflow ID>
GOAL=<beeminder goal>
NEG_REP=0 # downvotes (-1) and closed questions (-10)

# NOTE Can only retreive reputation history in 100 unit pages without authorisation
#      See https://api.stackexchange.com/docs
# WARNING Got to be careful with SO rep
#          Downvoting costs rep points (-1)
#          Answering closed questions costs rep points! (-10)
so_rep_1=`curl -s "https://api.stackexchange.com/2.2/users/$SOID/reputation-history?pagesize=100&site=stackoverflow&page=1" | gunzip | jq '[.items[].reputation_change] | add'`
so_rep_full=$((so_rep_1-NEG_REP))
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

