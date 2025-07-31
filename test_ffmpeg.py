# FILE: test_ffmpeg.py
import subprocess

# Use the exact path format that you have in your .env file
ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe" 
# The 'r' makes it a raw string, which is safest for Windows paths.

print(f"Attempting to run FFmpeg at: {ffmpeg_path}")

try:
    # We run a simple command: ffmpeg -version
    result = subprocess.run(
        [ffmpeg_path, '-version'],
        capture_output=True,
        text=True,
        check=True  # This will raise an exception on failure
    )
    print("\n--- SUCCESS! ---")
    print(result.stdout)

except FileNotFoundError:
    print("\n--- FAILED: FileNotFoundError ---")
    print("Python could not find the file at the specified path.")
    print("Please double-check that the path is 100% correct and the file exists.")

except subprocess.CalledProcessError as e:
    print("\n--- FAILED: CalledProcessError ---")
    print("FFmpeg was found and executed, but it returned an error.")
    print("STDOUT:", e.stdout)
    print("STDERR:", e.stderr)
    
except Exception as e:
    print(f"\n--- FAILED: An unexpected error occurred ---")
    print(e)