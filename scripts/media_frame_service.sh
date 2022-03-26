#!/bin/bash
export DISPLAY=:0.0;

MUSIC_IS_ACTIVE_FILE=/home/pi/scripts/github/media_frame/data/music/is_active
PID_FILE=/home/pi/scripts/github/media_frame/data/pid
pid=0

rm -f $MUSIC_IS_ACTIVE_FILE

while true; do
    if [ -f $PID_FILE ]; then
        pid=$(cat /home/pi/scripts/github/media_frame/data/pid);
    fi;

    if [ $pid -eq 0 ] || [ ! -n "$(ps -p $pid -o pid=)" ]; then
        pid=$(/home/pi/scripts/github/media_frame/scripts/start_media_frame.sh)
        echo $pid > /home/pi/scripts/github/media_frame/data/pid;
        echo "started new frame on $pid"
    else
        echo "running on ${pid}";

        if [ -f $MUSIC_IS_ACTIVE_FILE ]; then
            echo "music view is active, checking playback status"
            /home/pi/scripts/github/media_frame/scripts/check_playback_status.py
        fi;
    fi;

    sleep 15;

done;
