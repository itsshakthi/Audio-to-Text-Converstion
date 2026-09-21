"""
Audio extraction and processing module for video and audio files.
Extracts audio from uploaded media and converts to 16kHz mono WAV format for ASR.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple


def is_ffmpeg_available() -> bool:
    """Check if ffmpeg is available in the system PATH."""
    try:
        res = subprocess.run(
            ["ffmpeg", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return res.returncode == 0
    except Exception:
        return False


def extract_audio(
    input_path: str,
    output_path: Optional[str] = None,
    target_sr: int = 16000,
    channels: int = 1,
) -> str:
    """
    Extract audio track from video or convert audio file to 16kHz mono WAV.
    
    Args:
        input_path: Path to the input video or audio file.
        output_path: Optional output path. If None, generates a temporary wav file.
        target_sr: Target sample rate (default: 16000 Hz for optimal Whisper/ASR).
        channels: Target channels (1 = mono).
        
    Returns:
        Path to the output .wav file.
    """
    input_path = str(Path(input_path).resolve())
    
    if output_path is None:
        temp_dir = tempfile.gettempdir()
        file_stem = Path(input_path).stem
        output_path = os.path.join(temp_dir, f"{file_stem}_extracted.wav")
    else:
        output_path = str(Path(output_path).resolve())

    # Build ffmpeg command
    cmd = [
        "ffmpeg",
        "-y",               # Overwrite output without asking
        "-i", input_path,   # Input file
        "-vn",              # Disable video stream
        "-acodec", "pcm_s16le", # Standard 16-bit uncompressed PCM
        "-ar", str(target_sr),  # Sample rate
        "-ac", str(channels),   # Mono
        output_path,
    ]

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return output_path
        else:
            raise RuntimeError(f"Audio extraction created empty file: {output_path}")
    except subprocess.CalledProcessError as e:
        stderr_msg = e.stderr.decode("utf-8", errors="ignore")
        raise RuntimeError(f"FFmpeg extraction failed: {stderr_msg}") from e
    except FileNotFoundError:
        # Fallback to pydub if ffmpeg executable not found directly
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_file(input_path)
            audio = audio.set_frame_rate(target_sr).set_channels(channels)
            audio.export(output_path, format="wav")
            return output_path
        except Exception as pydub_err:
            raise RuntimeError(
                f"FFmpeg not found and pydub fallback failed: {pydub_err}"
            )


def get_media_info(file_path: str) -> dict:
    """
    Get duration and basic properties of media file.
    """
    info = {"duration": 0.0, "size_mb": 0.0, "is_video": False}
    p = Path(file_path)
    if not p.exists():
        return info

    info["size_mb"] = round(p.stat().st_size / (1024 * 1024), 2)
    video_exts = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".flv", ".wmv"}
    info["is_video"] = p.suffix.lower() in video_exts

    # Attempt to probe duration via ffprobe or ffmpeg
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(p),
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        if res.returncode == 0 and res.stdout.strip():
            info["duration"] = round(float(res.stdout.strip()), 2)
    except Exception:
        pass

    return info
