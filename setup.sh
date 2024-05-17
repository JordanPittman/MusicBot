#!/bin/bash

# Create the /app/bin directory
mkdir -p /app/bin

# Download precompiled ffmpeg binary
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-64bit-static.tar.xz -o ffmpeg-release-64bit-static.tar.xz
tar -xJf ffmpeg-release-64bit-static.tar.xz

# Find the extracted directory name dynamically and copy the binaries
extracted_dir=$(tar -tf ffmpeg-release-64bit-static.tar.xz | head -1 | cut -f1 -d"/")
cp "$extracted_dir"/ffmpeg "$extracted_dir"/ffprobe /app/bin/

# Ensure the binaries are executable
chmod +x /app/bin/ffmpeg /app/bin/ffprobe
