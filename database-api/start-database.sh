#!/bin/bash

databaseapi_dir="/opt/stack/horizon/database-api"
databaseapi="$databaseapi_dir/database-api.py"
address="127.0.0.1:9192"
cnt=1
pid="UNKNOWN"
__is__=0
__logs__="/opt/stack/horizon/database-api/logs"
__conf__="/opt/stack/horizon/horizon-database-config.conf"
today=$(date)

python=$(which python | awk '{print $1}' | tail -n 1)
if [ -f "$python" ]; then 

    ret=`$python -c 'import sys; print("%i" % (sys.hexversion>0x02070000 and sys.hexversion<0x03000000))'`
    if [ $ret -eq 0 ]; then
        echo "we require python version 2.7"
        exit 1
    else 
        echo "python version is acceptable."
    fi
else
    echo "Cannot find python. Aborting."
    exit 1
fi

if [ -d "$__logs__" ]; then 
    echo "$__logs__ exists."
else
    echo "$__logs__ does not exist, so making the directory."
    mkdir $__logs__
fi

if [ -f "$databaseapi" ]; then 
    echo "starting $databaseapi"
    nohup $python $databaseapi -a $address -c "$__conf__" -p "$__logs__" >$__logs__/database-api.out  &
    touch /opt/stack/horizon/database-api/database-api.pid
    echo $! >/opt/stack/horizon/database-api/database-api.pid
else
    echo "$today -- $databaseapi does not exist so there is nothing to do."
    exit 1
fi

echo "DONE!"
