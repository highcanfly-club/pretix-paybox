#!/bin/bash
NS=pretix
DBFILE="db.sqlite3"
DB="/data/$DBFILE"
POD=$(kubectl -n $NS get pods | grep "pretix-" | cut -d' ' -f1)
if [ "$1" == "RESTORE" ]; then
    kubectl cp $DBFILE $NS/$POD:$DB
    kubectl -n $NS exec $POD -- chown -R pretixuser $DB
    kubectl -n $NS exec $POD -- supervisorctl -s unix:///tmp/supervisor.sock restart pretixweb
else
    kubectl cp $NS/$POD:$DB $DBFILE
fi
