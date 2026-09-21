import os
from pydub import AudioSegment

# Correct local project path
input_folder = "data/raw_audio"
output_folder = "data/processed_audio"

os.makedirs(output_folder, exist_ok=True)

for file in os.listdir(input_folder):
    if file.endswith(".flac"):
        flac_path = os.path.join(input_folder, file)
        wav_path = os.path.join(output_folder, file.replace(".flac", ".wav"))

        audio = AudioSegment.from_file(flac_path, format="flac")
        audio.export(wav_path, format="wav")

        print(f"Converted {file} -> {wav_path}")
