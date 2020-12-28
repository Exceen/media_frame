#!/bin/bash


DISABLE_FILE=/home/pi/scripts/github/media_frame/data/disable
if [ ! -f $DISABLE_FILE ]; then
	touch /home/pi/scripts/github/media_frame/data/music/is_active

	old_pid=$(cat /home/pi/scripts/github/media_frame/data/pid);

	new_pid=$(/home/pi/scripts/github/media_frame/scripts/start_music.sh);
	echo $new_pid > /home/pi/scripts/github/media_frame/data/pid;


	sleep 15;

	if [ -n "$(ps -p $old_pid -o pid=)" ]; then
	    kill $old_pid;
	fi;
fi;
