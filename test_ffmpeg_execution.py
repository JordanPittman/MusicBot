import subprocess

ffmpeg_path = '/app/vendor/ffmpeg/ffmpeg'

# Test ffmpeg command with a simple operation
command = [ffmpeg_path, '-version']
try:
    result = subprocess.run(command, capture_output=True, text=True)
    print("FFmpeg command executed successfully.")
    print("Output:", result.stdout)
except Exception as e:
    print(f"Error executing FFmpeg command: {e}")
