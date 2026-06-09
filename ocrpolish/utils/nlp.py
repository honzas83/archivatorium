import re
import string
import unicodedata

import tiktoken


def estimate_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """
    Estimate the number of tokens in a string using tiktoken.
    Falls back to a word-count heuristic if tiktoken fails.
    """
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        return len(encoding.encode(text))
    except Exception:
        # Heuristic: ~1.33 tokens per word
        return int(len(text.split()) * 1.33)


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


def suppress_duplicates(
    conceptual: list[str],
    entities: list[str],
    topics: list[str],
    protected_terms: set[str] | None = None,
) -> list[str]:
    """
    Remove conceptual tags that are already represented as entities or topics.
    Comparison is case-insensitive and ignores the '#' prefix on conceptual tags.
    Protected terms are preferred conceptual vocabulary and are preserved even
    when they overlap with entity names or topic components.
    """
    protected = {term.lstrip("#").lower() for term in protected_terms or set()}

    # Build set of exact "taken" concepts from entity names and topic components.
    taken = set()
    for e in entities:
        parts = e.split("/")
        if parts:
            taken.add(parts[-1].lower())
    for t in topics:
        parts = t.split("/")
        for part in parts:
            taken.add(part.lower())

    filtered = []
    for tag in conceptual:
        clean_tag = tag.lstrip("#").lower()
        if clean_tag in protected or clean_tag not in taken:
            filtered.append(tag)
    return filtered


def normalize_exercise_tag(tag: str) -> str:
    """
    Normalize exercise tags with years into canonical hierarchical year form.
    Example: 'Wintex 71' -> 'WINTEX/71'
    """
    match = re.search(r"([A-Z]+)[- ]?([0-9]{2,4})", tag, re.IGNORECASE)
    if match:
        name = match.group(1).upper()
        year = match.group(2)
        if len(year) == 4:
            year = year[2:]
        return f"{name}/{year}"
    return tag


def filter_low_value_tags(tags: list[str]) -> list[str]:
    """
    Filter out routine administrative labels.
    """
    low_value_words = {"report", "study", "agenda", "notice", "corrigendum"}
    filtered = []
    for tag in tags:
        clean_tag = tag.lstrip("#").lower()
        if clean_tag not in low_value_words:
            filtered.append(tag)
    return filtered


def to_title_case_custom(text: str) -> str:
    """
    Generic Title Case conversion.
    Treats all-uppercase words as acronyms and preserves them.
    """
    words = text.split()
    title_words = []
    for word in words:
        if word.isupper():
            title_words.append(word)
        else:
            title_words.append(word.title())
    return " ".join(title_words)


def normalize_tag_component(component: str) -> str:
    """
    Normalizes a tag component for Obsidian safety.
    - Strips leading '#' characters.
    - Preserves original casing.
    - Replaces spaces and other symbols with hyphens.
    - Collapses multiple hyphens and strips them from ends.
    - Preserves forward slashes for nesting.
    """
    if not component:
        return ""

    # Strip leading hashes
    component = component.lstrip("#")

    # 1. Handle slashes separately if they represent hierarchy
    parts = component.split("/")
    norm_parts = []
    for part in parts:
        # a. Replace non-alphanumeric with hyphen
        s = re.sub(r"[^a-zA-Z0-9]", "-", part)
        # b. Collapse multiple hyphens and strip from ends
        s = re.sub(r"-+", "-", s).strip("-")
        norm_parts.append(s)

    return "/".join(norm_parts)
