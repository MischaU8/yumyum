#!/bin/bash

DATA_DIR="_data"

# Plasticity playlist by William V
URL="https://www.youtube.com/playlist?list=PLv8HciXoFYX-VGc-zqYQNLaWl8PuwIelI"

yt-dlp --paths $DATA_DIR --force-write-archive --download-archive $DATA_DIR/archive.txt $URL --write-info-json --write-auto-sub --skip-download --sub-format ttml/vtt/best 
