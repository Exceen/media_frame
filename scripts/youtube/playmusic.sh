#!/bin/bash
export DISPLAY=:0.0;


URL=''
X="$1"
if [[ -z "$X" ]]; then
	echo Enter URL ": " 
	read X
    URL=$X
else
    URL=$(python get_music_video_url.py "$X")
fi	

# "https://www.youtube.com/watch?v=NxLYJJnlGs8"
#youtube-dl -f worst -o - "https://www.youtube.com/watch?v=NxLYJJnlGs8" | vlc -f --play-and-exit -
youtube-dl -f best -o - $URL | vlc -f --play-and-exit -

