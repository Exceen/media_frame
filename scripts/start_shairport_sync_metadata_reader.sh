#!/bin/bash

export DISPLAY=:0.0;
#cat /tmp/shairport-sync-metadata | python3 ~/scripts/github/shairport-sync-metadata-python/bin/output_text.py
cat /tmp/shairport-sync-metadata | python3 ~/scripts/github/media_frame/scripts/shairport_sync_pipe_reader.py
