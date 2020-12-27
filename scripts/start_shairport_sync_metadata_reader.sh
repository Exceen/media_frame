#!/bin/bash

export DISPLAY=:0.0;
cat /tmp/shairport-sync-metadata | python3 ~/scripts/github/shairport-sync-metadata-python/bin/output_text.py

