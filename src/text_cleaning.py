"""
Text normalization and cleaning utilities for speech-to-text transcripts.
"""

import re
import unicodedata


def clean_transcript(text: str) -> str:
    """
    Clean and normalize raw speech recognition text.
    Removes extraneous whitespace, normalizes unicode, and fixes punctuation spacing.
    """
    if not text:
        return ""
    
    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)
    
    # Remove multiple spaces / tabs
    text = re.sub(r"[ \t]+", " ", text)
    
    # Fix spacing before common punctuation marks
    text = re.sub(r"\s+([.,!?;:])", r"\1", text)
    
    return text.strip()


def remove_filler_words(text: str, custom_fillers: list = None) -> str:
    """
    Optional filter for common disfluencies/fillers (um, uh, ah, etc.).
    """
    fillers = set(custom_fillers or ["um", "uh", "erm", "ah", "like", "you know"])
    pattern = r"\b(" + "|".join(re.escape(w) for w in fillers) + r")\b"
    cleaned = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return clean_transcript(cleaned)
