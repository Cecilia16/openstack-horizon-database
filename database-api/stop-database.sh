#!/bin/bash

pidfile="/opt/stack/horizon/database-api/database-api.pid"

if [ -f "$pidfile" ]; then 
    echo "Found $pidfile"
    pid=$(cat $pidfile)
    kill -9 $pid
    rm -f $pidfile
fi

echo "DONE!"
