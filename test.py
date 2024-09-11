import os
import base64

# Assuming 'generate' and 'play' are functions provided after setting up ElevenLabs API
from elevenlabs import generate, play, set_api_key

text = 'I like to sleep and eat and code'

# Directly setting API key and voice ID
elevenlabs_api_key = "69c2b35dfdec58f90df3c21b20158128"
elevenlabs_voice_id = "p43fx6U8afP2xoq1Ai9f"

# Set API key
set_api_key(elevenlabs_api_key)

# Generate audio from text
audio = generate(text, voice=elevenlabs_voice_id)

# Define the directory for saving the MP3
dir_path = "static"
os.makedirs(dir_path, exist_ok=True)

# Path for the new MP3 file
file_path = os.path.join(dir_path, "beats.mp3")

# Delete existing MP3 files in the directory
for file in os.listdir(dir_path):
    if file.endswith(".mp3"):
        os.remove(os.path.join(dir_path, file))

# Save the audio file (note: conversion to MP3 might be needed if 'generate' does not output MP3 format)
with open(file_path, "wb") as f:
    f.write(audio)

# Optionally, play the audio
play(audio)
