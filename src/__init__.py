"""
Voice to Text & Closed Captioning Package
"""

from src.audio_processor import extract_audio, get_media_info
from src.speech_to_text import load_whisper_model, transcribe_audio
from src.subtitle_generator import generate_srt, generate_vtt, generate_plain_text, generate_json_transcript
from src.video_processor import burn_subtitles_to_video

__all__ = [
    "extract_audio",
    "get_media_info",
    "load_whisper_model",
    "transcribe_audio",
    "generate_srt",
    "generate_vtt",
    "generate_plain_text",
    "generate_json_transcript",
    "burn_subtitles_to_video",
]
