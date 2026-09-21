"""
Video processing module for burning in / hardcoding closed captions onto video files.
Uses FFmpeg subtitle filter with proper Windows path escaping.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional


def burn_subtitles_to_video(
    video_path: str,
    srt_path: str,
    output_path: Optional[str] = None,
    font_size: int = 18,
    font_color: str = "&H00FFFFFF",
    bg_color: str = "&H80000000",
) -> str:
    """
    Burn subtitles permanently into a video file using FFmpeg.
    
    Args:
        video_path: Path to the input video file.
        srt_path: Path to the .srt subtitle file.
        output_path: Optional path for subtitled output video.
        font_size: Font size for subtitles.
        font_color: Primary font color in ASS format (&HAABBGGRR).
        bg_color: Outline/Background color in ASS format.
        
    Returns:
        Path to the resulting subtitled video file.
    """
    video_path = str(Path(video_path).resolve())
    srt_path = str(Path(srt_path).resolve())

    if output_path is None:
        temp_dir = tempfile.gettempdir()
        file_stem = Path(video_path).stem
        output_path = os.path.join(temp_dir, f"{file_stem}_captioned.mp4")
    else:
        output_path = str(Path(output_path).resolve())

    # Escape SRT path for FFmpeg subtitle filter (especially on Windows)
    # FFmpeg subtitles filter syntax on Windows requires escaped colons and slashes
    escaped_srt = srt_path.replace("\\", "/").replace(":", "\\:")
    
    # Subtitle styling parameters (FontName, FontSize, Outline, BackColour, Alignment)
    force_style = (
        f"FontSize={font_size},"
        f"PrimaryColour={font_color},"
        f"BackColour={bg_color},"
        f"BorderStyle=3,"
        f"Outline=1,"
        f"Shadow=0,"
        f"MarginV=25"
    )
    
    vf_filter = f"subtitles='{escaped_srt}':force_style='{force_style}'"

    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vf", vf_filter,
        "-c:a", "copy",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
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
            raise RuntimeError("FFmpeg subtitle burn-in produced empty output.")
    except subprocess.CalledProcessError as e:
        stderr_msg = e.stderr.decode("utf-8", errors="ignore")
        raise RuntimeError(f"FFmpeg subtitle burn-in failed: {stderr_msg}") from e
