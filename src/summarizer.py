"""
Text summarization utility for transcripts.
"""

from typing import List


def extract_key_points(text: str, max_sentences: int = 3) -> List[str]:
    """
    Extract key sentences from transcript for a quick summary.
    """
    if not text:
        return []
    
    # Split by sentence enders
    import re
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if len(s.strip()) > 10]
    return sentences[:max_sentences]
