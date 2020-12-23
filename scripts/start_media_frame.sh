#!/bin/bash

MUSIC_IS_ACTIVE_PATH=/home/pi/scripts/github/media_frame/data/music/is_active

pid=0
if [ ! -f $MUSIC_IS_ACTIVE_PATH ]; then
    pid=$(/home/pi/scripts/github/media_frame/scripts/start_photos.sh);
else
    pid=$(/home/pi/scripts/github/media_frame/scripts/start_music.sh);
fi;
echo $pid;
