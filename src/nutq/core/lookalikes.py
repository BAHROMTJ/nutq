"""Fix Latin letters hidden inside Cyrillic words (Тoҷик -> Тоҷик)."""

import re

_LATIN_IN_CYRILLIC = str.maketrans({
    "a": "а", "c": "с", "e": "е", "o": "о", "p": "р", "x": "х", "y": "у",
    "A": "А", "B": "В", "C": "С", "E": "Е", "H": "Н", "K": "К", "M": "М",
    "O": "О", "P": "Р", "T": "Т", "X": "Х", "Y": "У",
})

_WORD = re.compile(r"\w+")
_CYRILLIC = re.compile(r"[Ѐ-ԯ]")


def _fix_word(match):
    word = match.group(0)
    if _CYRILLIC.search(word):
        return word.translate(_LATIN_IN_CYRILLIC)
    return word


def fix_latin_in_cyrillic(text: str) -> str:
    """Replace Latin look-alikes inside words that contain Cyrillic letters.

    Words written fully in Latin script are left untouched.
    """
    return _WORD.sub(_fix_word, text)
