#!/bin/bash
touch /home/pi/scripts/github/media_frame/data/disable;
pid=$(cat /home/pi/scripts/github/media_frame/data/pid);

if [ -n "$(ps -p $pid -o pid=)" ]; then
    kill $pid;
fi;

