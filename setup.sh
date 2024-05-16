#!/bin/bash

# Download precompiled ffmpeg binary
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-64bit-static.tar.xz -o ffmpeg-release-64bit-static.tar.xz
tar -xvf ffmpeg-release-64bit-static.tar.xz
cp ffmpeg-*-static/ffmpeg ffmpeg-*-static/ffprobe /app/bin/

# Ensure the binaries are executable
chmod +x /app/bin/ffmpeg /app/bin/ffprobe
