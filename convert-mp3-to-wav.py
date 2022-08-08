# This script convert all mp3 files in a directory to wav files.
import os
from pydub import AudioSegment

# Target directory
TARGET_DIR = "data"

# Get all files in target directory
fileList = os.listdir(TARGET_DIR)
# Find all mp3 files
mp3Files = [file for file in fileList if file.endswith(".mp3")]
# Construct full path for each mp3 file
mp3Files = [os.path.join(TARGET_DIR, file) for file in mp3Files]

print(f"Found {len(mp3Files)} mp3 files")

# Convert all mp3 files to wav files
for file in mp3Files:
    print(f"Converting {file} to wav...")
    # Read mp3 file
    audio = AudioSegment.from_mp3(file)
    # Write wav file
    audio.export(file.replace(".mp3", ".wav"), format="wav")
    # Remove mp3 file
    os.remove(file)