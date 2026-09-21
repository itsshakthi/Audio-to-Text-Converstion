# 🎬 YouTube-Style Closed Caption & Video Subtitle Generator

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io)
[![Whisper](https://img.shields.io/badge/ASR-OpenAI%20Whisper-black.svg)](https://github.com/openai/whisper)
[![FFmpeg](https://img.shields.io/badge/Media-FFmpeg-green.svg)](https://ffmpeg.org)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)]()

A modern, production-ready system for automatic closed-caption generation and video subtitle rendering for gallery video and audio files. Built with OpenAI Whisper, FFmpeg, and Streamlit, featuring a YouTube-style synchronized video/audio player with live caption overlays and interactive transcript seeking.

---

## ✨ Features

- 🎥 **Universal Media Support**: Upload gallery video (`.mp4`, `.mkv`, `.mov`, `.avi`, `.webm`) or audio files (`.wav`, `.mp3`, `.m4a`, `.flac`, `.ogg`, `.aac`).
- ⚡ **Automated Audio Extraction**: Extracts clean 16kHz mono audio on-the-fly using FFmpeg with lossless fallback.
- 🌐 **Multilingual Speech Recognition & Translation**:
  - 50+ languages supported (English, Hindi, Telugu, Tamil, Kannada, Malayalam, Bengali, Spanish, French, German, Japanese, etc.).
  - Transcribe in original language or translate directly into English closed captions.
- 📺 **YouTube-Style Synchronized CC Player**:
  - Live closed caption overlay rendered directly over the video player.
  - Interactive transcript: clicking any timestamp line jumps the video directly to that exact cue.
  - Active line auto-highlighting and smooth scrolling during playback.
  - YouTube-style CC toggle button (`ON`/`OFF`), keyboard shortcut (`C`), and subtitle font size controls.
- ✏️ **Interactive Subtitle Editor**:
  - In-browser editor to modify words, adjust timestamps, and dynamically re-generate all subtitle formats.
- 📥 **Multi-Format Subtitle Export**:
  - SubRip Subtitles (`.srt`)
  - WebVTT Subtitles (`.vtt`)
  - Plain Text Transcript (`.txt`)
  - Structured Metadata & Cues (`.json`)
- 🔥 **Hardcoded Video Export (Burn-in Subtitles)**:
  - Export the final video with permanently hardcoded closed captions via FFmpeg.

---

## 🏗️ Architecture

```
┌────────────────────────────────┐
│  Gallery Video / Audio Upload  │
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│  FFmpeg 16kHz Audio Extractor  │ ◄── src/audio_processor.py
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│   OpenAI Whisper ASR Engine    │ ◄── src/speech_to_text.py
│  (tiny / base / small / med)   │
└───────────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│   Timestamped Segment Parser   │ ◄── src/subtitle_generator.py
└───────────────┬────────────────┘
                │
     ┌──────────┴──────────┐
     ▼                     ▼
┌─────────────────┐  ┌───────────────────────────────┐
│ Synchronized    │  │ Multi-Format Exporter         │
│ YouTube CC      │  │ • .SRT   • .VTT               │
│ HTML5 Player    │  │ • .TXT   • .JSON              │
│ (src/ui_comp)   │  │ • Hardsub MP4 (src/video_proc)│
└─────────────────┘  └───────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Prerequisites
- **Python 3.9+** installed
- **FFmpeg** installed and added to system PATH
  - *Windows*: `winget install Gyan.FFmpeg` or download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
  - *macOS*: `brew install ffmpeg`
  - *Ubuntu/Debian*: `sudo apt install ffmpeg`

### 2. Installation

Clone repository and create a virtual environment:
```bash
git clone https://github.com/itsshakthi/Multilingual-Audio-to-Text-Conversion-System-Using-Speech-Recognition-Techniques.git
cd "voice to text"

python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run Application

```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🐳 Docker Deployment

Build and run using Docker:

```bash
# Build Docker image
docker build -t cc-studio .

# Run container
docker run -p 8501:8501 cc-studio
```

---

## 📂 Project Structure

```
.
├── app.py                      # Main Streamlit web application & CC Studio UI
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Containerization specification
├── .dockerignore               # Docker ignore rules
├── src/
│   ├── __init__.py             # Package init & module exports
│   ├── audio_processor.py      # Video-to-audio extraction & audio normalization
│   ├── speech_to_text.py       # Whisper model loading, inference & multilingual logic
│   ├── subtitle_generator.py   # SubRip (.srt), WebVTT (.vtt), JSON, TXT generation
│   ├── video_processor.py      # FFmpeg video subtitle burn-in / hardsubbing
│   ├── ui_components.py        # YouTube Dark theme & synchronized CC HTML5 player
│   ├── text_cleaning.py        # Text normalization & disfluency cleaning
│   └── summarizer.py           # Key takeaways & summary extractor
└── README.md                   # Project documentation
```

---

## 📜 License

Distributed under the MIT License.
