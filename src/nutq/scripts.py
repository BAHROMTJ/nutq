"""Script codes (ISO 15924) and script detection."""

from typing import Iterable, Optional

_NAMES = {
    "cyrl": "Cyrl", "cyrillic": "Cyrl", "кириллӣ": "Cyrl",
    "latn": "Latn", "latin": "Latn", "лотинӣ": "Latn",
    "arab": "Arab", "arabic": "Arab", "perso-arabic": "Arab", "persian": "Arab",
}


def canonical_script(name: str) -> str:
    """Return the ISO 15924 code for a script name (``latin`` -> ``Latn``)."""
    try:
        return _NAMES[name.strip().lower()]
    except KeyError:
        raise ValueError(f"unknown script {name!r}; use Cyrl, Latn or Arab") from None


def script_of(char: str) -> Optional[str]:
    """Return the script of a single letter, or ``None`` for non-letters."""
    if not char.isalpha() and char not in "ʻʼ":
        return None
    code = ord(char)
    if 0x0400 <= code <= 0x052F:
        return "Cyrl"
    if (0x0600 <= code <= 0x06FF or 0x0750 <= code <= 0x077F
            or 0xFB50 <= code <= 0xFDFF or 0xFE70 <= code <= 0xFEFF):
        return "Arab"
    if code < 0x0250 or char in "ʻʼ" or 0x1E00 <= code <= 0x1EFF:
        return "Latn"
    return None


def detect_script(text: str, candidates: Optional[Iterable[str]] = None) -> Optional[str]:
    """Return the script most letters in ``text`` are written in.

    >>> detect_script("Салом, dunyo!")
    'Cyrl'
    """
    allowed = set(candidates) if candidates is not None else None
    counts = {}
    for char in text:
        script = script_of(char)
        if script and (allowed is None or script in allowed):
            counts[script] = counts.get(script, 0) + 1
    if not counts:
        return None
    return max(counts, key=counts.get)
