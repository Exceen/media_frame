#!/bin/bash


DISABLE_FILE=/home/pi/scripts/github/media_frame/data/disable
if [ ! -f $DISABLE_FILE ]; then
	rm -f /home/pi/scripts/github/media_frame/data/music/is_active

	old_pid=$(cat /home/pi/scripts/github/media_frame/data/pid);

	new_pid=$(/home/pi/scripts/github/media_frame/scripts/start_photos.sh);
	echo $new_pid > /home/pi/scripts/github/media_frame/data/pid;


	sleep 6;

	if [ -n "$(ps -p $old_pid -o pid=)" ]; then
	    kill $old_pid;
	fi;
fi;