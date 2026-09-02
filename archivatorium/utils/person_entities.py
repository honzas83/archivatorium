"""Normalization helpers for hierarchical Person entity paths."""

import re

from archivatorium.utils.nlp import normalize_tag_component

_ROLE_OR_TITLE_COMPONENTS = {
    "admiral",
    "ambassador",
    "captain",
    "chairman",
    "chairwoman",
    "commander",
    "doctor",
    "dr",
    "general",
    "general-secretary",
    "lord",
    "major",
    "minister",
    "mr",
    "mrs",
    "ms",
    "president",
    "prof",
    "professor",
    "secretary",
    "secretary-general",
    "sir",
}


def _normalize_name_component(component: str) -> str:
    """Normalize punctuation while keeping initials visibly uppercase."""

    component = re.sub(
        r"\b[A-Za-z](?:\.[A-Za-z])+\.?",
        lambda match: "-".join(re.findall(r"[A-Za-z]", match.group())).upper(),
        component,
    )
    normalized = normalize_tag_component(component)
    return "-".join(part.upper() if len(part) == 1 else part for part in normalized.split("-"))


def _is_role_or_title(component: str) -> bool:
    return component.lower() in _ROLE_OR_TITLE_COMPONENTS


def normalize_person_path(raw_path: str) -> str | None:
    """Return a canonical ``Person/surname[/given-name]`` path.

    Malformed paths, missing surnames, non-Person entities, and paths deeper
    than the supported hierarchy are rejected. A role or title in the optional
    given-name position is removed, leaving the surname-only identity.
    """

    if not raw_path or not isinstance(raw_path, str):
        return None

    parts = raw_path.split("/")
    if len(parts) not in {2, 3} or parts[0].lower() != "person":
        return None

    surname = _normalize_name_component(parts[1])
    if not surname or _is_role_or_title(surname):
        return None

    if len(parts) == 2:
        return f"Person/{surname}"

    given_name = _normalize_name_component(parts[2])
    if not given_name or _is_role_or_title(given_name):
        return f"Person/{surname}"

    return f"Person/{surname}/{given_name}"
