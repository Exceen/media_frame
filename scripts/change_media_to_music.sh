#!/bin/bash


DISABLE_FILE=/home/pi/scripts/github/media_frame/data/disable
if [ ! -f $DISABLE_FILE ]; then
    touch /home/pi/scripts/github/media_frame/data/music/is_active


    ###
    mosquitto_pub -h localhost -t "frame/subdirectory" -m "music/artwork"
    mosquitto_pub -h localhost -t "frame/fade_time" -m "3"
    mosquitto_pub -h localhost -t "frame/time_delay" -m "10800"
    mosquitto_pub -h localhost -t "frame/next" -m ""
    ###

    # old_pid=$(cat /home/pi/scripts/github/media_frame/data/pid);

    # new_pid=$(/home/pi/scripts/github/media_frame/scripts/start_music.sh);
    # echo $new_pid > /home/pi/scripts/github/media_frame/data/pid;


    # sleep 15;

    # if [ -n "$(ps -p $old_pid -o pid=)" ]; then
    #     kill $old_pid;
    # fi;
fi;
