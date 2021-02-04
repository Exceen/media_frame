#!/bin/bash

X="$1"
# if [[ -z "$X" ]]; then
# 	echo Enter song ": " 
# 	read X
# fi	

youtube-dl -f worst -o - $(python play_youtube.py "$X") |  mplayer -fs -nosound -