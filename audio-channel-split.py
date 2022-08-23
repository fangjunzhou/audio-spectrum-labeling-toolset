import os
import soundfile as sf

# Target file path
TARGET_FILE_NAME = "sample.wav"
targetFilePath = os.path.join(os.getcwd(), "data", TARGET_FILE_NAME)

# Read audio file
data, sampleRate = sf.read(targetFilePath)
print(f"data shape: {data.shape}")

# Check if the audio has multiple channels
if data.shape[1] > 1:
    # Split the audio into multiple channels
    for i in range(data.shape[1]):
        # Create a new file name
        newFileName = f"{TARGET_FILE_NAME}_chan{i}.wav"
        # Create a new file path
        newFilePath = os.path.join(os.getcwd(), "data", newFileName)
        # Write the audio to the new file path
        sf.write(newFilePath, data[:, i], sampleRate)
        print(f"{newFileName} is created")
