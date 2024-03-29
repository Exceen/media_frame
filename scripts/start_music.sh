#!/bin/bash
# echo "" > /home/pi/scripts/github/media_frame/data/music/current_track.txt
export DISPLAY=:0.0;
python /home/pi/scripts/github/media_frame/scripts/pi3d/PictureFrame2020.py \
    --blur_edges 1 \
    --keyboard 1 \
    --use_mqtt 1 \
    --blur_amount 5 \
    --background "(0, 0, 0, 1.0)" \
    --shuffle 1 \
    --check_dir_tm 10800 \
    --show_text_tm 10800 \
    --text_width 45 \
    --pic_dir /home/pi/scripts/github/media_frame/data \
    --two_line_track 1 \
    \
    --subdirectory "music/artwork" \
    --fade_time 3 \
    --time_delay 10800 \
    --show_text "music" > /dev/null&
    
echo $!;    
