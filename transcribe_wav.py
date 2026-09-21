import whisper
import os

# Load Whisper model
model = whisper.load_model("base")

input_folder = "data/processed_audio"
output_folder = "data/transcripts"

os.makedirs(output_folder, exist_ok=True)

for file in os.listdir(input_folder):
    if file.endswith(".wav"):
        wav_path = os.path.join(input_folder, file)

        print(f"Transcribing {file}...")

        result = model.transcribe(wav_path)

        text = result["text"]

        output_path = os.path.join(output_folder, file.replace(".wav", ".txt"))

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

        print(f"Saved transcript to {output_path}")
