#!/bin/bash
# python /home/pi/scripts/github/media_frame/pi3d_demos/PictureFrame2020.py \
#     --blur_edges 1 \
#     --keyboard 1 \
#     --use_mqtt 1 \
#     --blur_amount 5 \
#     --background "(0, 0, 0, 1.0)" \
#     --shuffle 1 \
#     --pic_dir /home/pi/scripts/github/media_frame/data/photos \
#     --fade_time 6 \
#     --time_delay 10 \
#     --show_text_tm 0 \
#     --check_dir_tm 60 \
#     --show_text "" > /dev/null&

# echo $!;






echo "" > /home/pi/scripts/github/media_frame/data/music/current_track.txt 
python /home/pi/scripts/github/media_frame/pi3d_demos/PictureFrame2020.py \
    --blur_edges 1 \
    --keyboard 1 \
    --use_mqtt 1 \
    --blur_amount 5 \
    --background "(0, 0, 0, 1.0)" \
    --shuffle 1 \
    --pic_dir /home/pi/scripts/github/media_frame/data/music/artwork \
    --fade_time 3 \
    --time_delay 9999 \
    --show_text_tm 9999 \
    --check_dir_tm 9999 \
    --show_text "music" \
    --text_width 45 > /dev/null&
echo $!;