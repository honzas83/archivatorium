import string
import unicodedata


def normalize_text(text: str) -> str:
    """Remove diacritics and punctuation, but preserve case."""
    # Remove diacritics
    text = "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")
    # Remove punctuation
    text = text.translate(str.maketrans("", "", string.punctuation))
    return text


def get_word_set(text: str) -> frozenset[str]:
    """Normalize text and return a frozenset of unique words (case-insensitive)."""
    normalized = normalize_text(text)
    words = [w.lower() for w in normalized.split()]
    return frozenset(words)


def overlap_coefficient(set1: frozenset[str], set2: frozenset[str]) -> float:
    """Calculate overlap coefficient between two sets."""
    if not set1 or not set2:
        return 0.0
    intersection = len(set1.intersection(set2))
    return intersection / min(len(set1), len(set2))
