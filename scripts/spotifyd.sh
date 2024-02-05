#!/bin/bash
export DISPLAY=:0.0;
#/usr/bin/spotifyd --verbose --no-daemon --config-path /etc/default/spotifyd

# switch to photo view in case of a crash or whatever
script_dir=$(dirname "$0")
eval "${script_dir}/change_media_to_photos.sh"

/usr/bin/spotifyd --no-daemon --config-path /etc/default/spotifyd
