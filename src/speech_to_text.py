"""
Speech-to-Text inference engine using OpenAI Whisper.
Extracts segment-level timestamps, detects language, and performs multilingual transcription / translation.
"""

import os
import tempfile
from typing import Dict, Any, List, Optional, Tuple

try:
    import torch
except (ImportError, OSError, Exception):
    torch = None

try:
    import whisper
except (ImportError, OSError, Exception):
    whisper = None



# Supported ASR Engines
AVAILABLE_MODELS = [
    "whisper-tiny",
    "whisper-base",
    "whisper-small",
    "whisper-medium",
    "google-cloud-sr",
]

# Common language codes with human-readable names
LANGUAGE_OPTIONS = {
    "Auto-Detect": None,
    "English": "en",
    "Hindi (हिन्दी)": "hi",
    "Telugu (తెలుగు)": "te",
    "Tamil (தமிழ்)": "ta",
    "Kannada (ಕನ್ನಡ)": "kn",
    "Malayalam (മലയാളം)": "ml",
    "Bengali (বাংলা)": "bn",
    "Gujarati (ગુજરાતી)": "gu",
    "Marathi (मराठी)": "mr",
    "Punjabi (ਪੰਜਾਬੀ)": "pa",
    "Urdu (اردو)": "ur",
    "Spanish (Español)": "es",
    "French (Français)": "fr",
    "German (Deutsch)": "de",
    "Japanese (日本語)": "ja",
    "Korean (한국어)": "ko",
    "Chinese (中文)": "zh",
    "Arabic (العربية)": "ar",
    "Russian (Русский)": "ru",
    "Portuguese (Português)": "pt",
    "Italian (Italiano)": "it",
}


def get_device() -> str:
    """Return 'cuda' if GPU is available else 'cpu'."""
    try:
        import torch
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"


def load_whisper_model(model_name: str = "whisper-base"):
    """
    Load a Whisper model onto the best available device, or return indicator for Google SR.
    """
    if model_name == "google-cloud-sr":
        return "google-cloud-sr"
    
    clean_name = model_name.replace("whisper-", "")
    try:
        import whisper
        device = get_device()
        model = whisper.load_model(clean_name, device=device)
        return model
    except Exception as e:
        print(f"Whisper load warning: {e}. Falling back to Google Speech Recognition.")
        return "google-cloud-sr"


def transcribe_with_google_sr(
    audio_path: str,
    language: Optional[str] = "en-IN",
) -> Dict[str, Any]:
    """
    Transcribe audio file using Google Speech Recognition API with chunked timestamps.
    """
    import speech_recognition as sr
    from pydub import AudioSegment
    from pydub.silence import split_on_silence

    r = sr.Recognizer()
    
    # Map simple language codes to full locales
    locale_map = {
        "en": "en-US",
        "hi": "hi-IN",
        "te": "te-IN",
        "ta": "ta-IN",
        "kn": "kn-IN",
        "ml": "ml-IN",
        "bn": "bn-IN",
        "gu": "gu-IN",
        "mr": "mr-IN",
        "pa": "pa-IN",
        "ur": "ur-IN",
        "es": "es-ES",
        "fr": "fr-FR",
        "de": "de-DE",
        "ja": "ja-JP",
        "ko": "ko-KR",
        "zh": "zh-CN",
    }
    target_locale = locale_map.get(language, language or "en-US")

    # Load audio using pydub
    sound = AudioSegment.from_file(audio_path)
    total_len_sec = len(sound) / 1000.0

    # Split audio on silence to get timed chunks
    chunks = split_on_silence(
        sound,
        min_silence_len=500,
        silence_thresh=sound.dBFS - 14 if sound.dBFS else -30,
        keep_silence=250,
    )

    segments = []
    full_text_list = []
    current_time = 0.0

    if not chunks:
        # Fallback to single recording
        with sr.AudioFile(audio_path) as source:
            audio_data = r.record(source)
            try:
                text = r.recognize_google(audio_data, language=target_locale)
                segments.append({
                    "id": 1,
                    "start": 0.0,
                    "end": total_len_sec,
                    "text": text,
                })
                full_text_list.append(text)
            except Exception:
                pass
    else:
        temp_dir = tempfile.gettempdir()
        for idx, chunk in enumerate(chunks):
            chunk_duration = len(chunk) / 1000.0
            chunk_path = os.path.join(temp_dir, f"sr_chunk_{idx}.wav")
            chunk.export(chunk_path, format="wav")
            
            with sr.AudioFile(chunk_path) as source:
                audio_data = r.record(source)
                try:
                    text = r.recognize_google(audio_data, language=target_locale)
                    if text.strip():
                        segments.append({
                            "id": len(segments) + 1,
                            "start": round(current_time, 2),
                            "end": round(current_time + chunk_duration, 2),
                            "text": text.strip(),
                        })
                        full_text_list.append(text.strip())
                except Exception:
                    pass
                finally:
                    if os.path.exists(chunk_path):
                        try:
                            os.remove(chunk_path)
                        except Exception:
                            pass
            current_time += chunk_duration

    # If silence chunking failed to extract any speech, try full audio
    if not segments:
        with sr.AudioFile(audio_path) as source:
            audio_data = r.record(source)
            try:
                text = r.recognize_google(audio_data, language=target_locale)
                segments.append({
                    "id": 1,
                    "start": 0.0,
                    "end": total_len_sec,
                    "text": text,
                })
                full_text_list.append(text)
            except Exception:
                text = ""

    return {
        "text": " ".join(full_text_list),
        "segments": segments,
        "language": language or "auto",
        "task": "transcribe",
    }


def transcribe_audio(
    model,
    audio_path: str,
    language: Optional[str] = None,
    task: str = "transcribe",
    temperature: float = 0.0,
    word_timestamps: bool = False,
) -> Dict[str, Any]:
    """
    Transcribe or translate an audio file with timestamped segments.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    if model == "google-cloud-sr" or isinstance(model, str):
        return transcribe_with_google_sr(audio_path, language=language)

    try:
        import torch
        options = {
            "task": task,
            "temperature": temperature,
            "fp16": torch.cuda.is_available(),
        }
        if language:
            options["language"] = language

        result = model.transcribe(audio_path, **options)

        cleaned_segments = []
        for idx, seg in enumerate(result.get("segments", [])):
            cleaned_segments.append({
                "id": idx + 1,
                "start": float(seg["start"]),
                "end": float(seg["end"]),
                "text": seg["text"].strip(),
            })

        return {
            "text": result.get("text", "").strip(),
            "segments": cleaned_segments,
            "language": result.get("language", language or "unknown"),
            "task": task,
        }
    except Exception as err:
        print(f"Whisper inference error: {err}. Falling back to Google Speech Recognition.")
        return transcribe_with_google_sr(audio_path, language=language)

