"""
Shared text parsing utilities.
"""

import re


def clean_text(text: str) -> str:
    """Strip extra whitespace and normalize newlines."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip())


def extract_number(text: str) -> int | None:
    """Extract the first integer from a string. e.g. '500+ connections' → 500"""
    match = re.search(r"(\d[\d,]*)", text)
    if match:
        return int(match.group(1).replace(",", ""))
    return None


def truncate(text: str, max_len: int = 80) -> str:
    """Truncate text to max_len characters with ellipsis."""
    if not text:
        return ""
    return text if len(text) <= max_len else text[:max_len - 3] + "..."


def is_likely_name(text: str) -> bool:
    """
    Heuristic: does this look like a person's name?
    (2–4 words, title case, no special characters)
    """
    if not text:
        return False
    words = text.strip().split()
    if not (2 <= len(words) <= 4):
        return False
    if any(c in text for c in ["|", "@", "$", "http", "#"]):
        return False
    return all(w[0].isupper() for w in words if w)