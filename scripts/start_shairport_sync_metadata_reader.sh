#!/bin/bash

export DISPLAY=:0.0;
#cat /tmp/shairport-sync-metadata | python3 ~/scripts/github/shairport-sync-metadata-python/bin/output_text.py

script_dir=$(dirname "$0")
eval "${script_dir}/change_media_to_photos.sh"

cat /tmp/shairport-sync-metadata | python3 /home/pi/scripts/github/media_frame/scripts/shairport_sync_pipe_reader.py
