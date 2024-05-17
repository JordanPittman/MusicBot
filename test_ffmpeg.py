import subprocess

def test_ffmpeg():
    command = ['/app/vendor/ffmpeg/ffmpeg', '-version']
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_ffmpeg()
