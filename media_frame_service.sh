#!/bin/bash


FILE=/home/pi/scripts/github/media_frame/data/disable
pid=0
while true; do

	if [ $pid -eq 0 ] || [ ! -n "$(ps -p $pid -o pid=)" ]; then
		if [ ! -f $FILE ]; then
			pid=$(/home/pi/scripts/github/media_frame/scripts/start_media_frame.sh)
			echo $pid > /home/pi/scripts/github/media_frame/data/pid;
		else
			echo "surpressing";
		fi;
	else
		echo "already running";
	fi;

	sleep 15;

done;