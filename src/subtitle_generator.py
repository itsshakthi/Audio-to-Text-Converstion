"""
Subtitle and Closed Caption generator module.
Supports SubRip (.srt), WebVTT (.vtt), JSON, and Plain Text transcript formatting.
"""

import json
from typing import List, Dict, Any, Optional


def format_timestamp_srt(seconds: float) -> str:
    """
    Format seconds into SubRip (SRT) timestamp format: HH:MM:SS,mmm
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int(round((seconds - int(seconds)) * 1000))
    # Handle rounding overflow
    if milliseconds >= 1000:
        milliseconds -= 1000
        secs += 1
    if secs >= 60:
        secs -= 60
        minutes += 1
    if minutes >= 60:
        minutes -= 60
        hours += 1
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def format_timestamp_vtt(seconds: float) -> str:
    """
    Format seconds into WebVTT timestamp format: HH:MM:SS.mmm
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int(round((seconds - int(seconds)) * 1000))
    if milliseconds >= 1000:
        milliseconds -= 1000
        secs += 1
    if secs >= 60:
        secs -= 60
        minutes += 1
    if minutes >= 60:
        minutes -= 60
        hours += 1
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"


def format_time_display(seconds: float) -> str:
    """
    Format seconds into human-friendly MM:SS or HH:MM:SS for the UI player.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def generate_srt(segments: List[Dict[str, Any]]) -> str:
    """
    Generate SubRip (.srt) subtitle content from Whisper segments.
    """
    srt_lines = []
    for idx, seg in enumerate(segments, start=1):
        start = format_timestamp_srt(seg.get("start", 0.0))
        end = format_timestamp_srt(seg.get("end", 0.0))
        text = seg.get("text", "").strip()
        srt_lines.append(f"{idx}")
        srt_lines.append(f"{start} --> {end}")
        srt_lines.append(f"{text}\n")
    return "\n".join(srt_lines)


def generate_vtt(segments: List[Dict[str, Any]]) -> str:
    """
    Generate WebVTT (.vtt) subtitle content from Whisper segments.
    """
    vtt_lines = ["WEBVTT\n"]
    for idx, seg in enumerate(segments, start=1):
        start = format_timestamp_vtt(seg.get("start", 0.0))
        end = format_timestamp_vtt(seg.get("end", 0.0))
        text = seg.get("text", "").strip()
        vtt_lines.append(f"{idx}")
        vtt_lines.append(f"{start} --> {end}")
        vtt_lines.append(f"{text}\n")
    return "\n".join(vtt_lines)


def generate_plain_text(segments: List[Dict[str, Any]]) -> str:
    """
    Generate plain text transcription from segments.
    """
    return " ".join([seg.get("text", "").strip() for seg in segments if seg.get("text", "").strip()])


def generate_json_transcript(
    segments: List[Dict[str, Any]],
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate structured JSON transcript with metadata and timestamped cues.
    """
    data = {
        "metadata": metadata or {},
        "segments": [
            {
                "id": idx,
                "start": round(seg.get("start", 0.0), 3),
                "end": round(seg.get("end", 0.0), 3),
                "start_formatted": format_time_display(seg.get("start", 0.0)),
                "end_formatted": format_time_display(seg.get("end", 0.0)),
                "text": seg.get("text", "").strip(),
            }
            for idx, seg in enumerate(segments, start=1)
        ],
    }
    return json.dumps(data, indent=2, ensure_ascii=False)
