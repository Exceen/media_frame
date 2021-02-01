#!/bin/bash

export DISPLAY=:0.0;
python /home/pi/scripts/github/media_frame/pi3d_demos/PictureFrame2020.py \
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
    --subdirectory "photos" \
    --fade_time 6 \
    --time_delay 600 \
    --show_text "" > /dev/null&

echo $!;
