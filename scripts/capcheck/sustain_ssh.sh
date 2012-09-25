#!/bin/sh

#This is an SSH-D proxy with auto-reconnect on disconnect

#Created by Liang Sun on 28, Sep, 2011
#Email: i@liangsun.org

#Modified by Joon on 21, Aug, 2012
#ssh <ip_of_ucapserver> -L 54322:localhost:5432 -o ServerAliveInterval=60

i=0
while test 1==1
do
    remote_ip=<ip_of_ucapserver>
    exist=`ps aux | grep $remote_ip | grep 54322`
#    echo $exist
    if test -n "$exist"
    then
        if test $i -eq 0
        then
            echo "I'm alive since $(date)"
        fi
        i=1
    else
        i=0
        echo "I died... Reconnecting..."
        ssh $remote_ip -L 54322:localhost:5432 -o ServerAliveInterval=60
    fi
    sleep 5
done
