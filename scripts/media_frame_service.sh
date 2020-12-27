#!/bin/bash


DISABLE_FILE=/home/pi/scripts/github/media_frame/data/disable
PID_FILE=/home/pi/scripts/github/media_frame/data/pid
pid=0

rm -f /home/pi/scripts/github/media_frame/data/music/is_active

while true; do
	if [ -f $PID_FILE ]; then
		pid=$(cat /home/pi/scripts/github/media_frame/data/pid);
	fi;

	if [ $pid -eq 0 ] || [ ! -n "$(ps -p $pid -o pid=)" ]; then
		if [ ! -f $DISABLE_FILE ]; then
			pid=$(/home/pi/scripts/github/media_frame/scripts/start_media_frame.sh)
			echo $pid > /home/pi/scripts/github/media_frame/data/pid;
		else
			echo "disabled";
		fi;
	else
		echo "running on ${pid}";
	fi;

	sleep 15;

done;
