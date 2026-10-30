"""Uzbek Cyrillic <-> Latin, following the 1995 official Latin alphabet.

The Latin letters oʻ and gʻ use U+02BB (ʻ) and the tutuq belgisi (ъ) uses
U+02BC (ʼ), as the official standard says. Text typed with ASCII ' or with
‘ ’ ` is accepted on input.
"""

import re

from ...core.case import match_case

OKINA = "ʻ"   # ʻ in oʻ, gʻ
TUTUQ = "ʼ"   # ʼ for ъ

_CYR_TO_LAT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "ё": "yo",
    "ж": "j", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "x", "ч": "ch", "ш": "sh", "ъ": TUTUQ, "ь": "",
    "э": "e", "ю": "yu", "я": "ya", "ў": "o" + OKINA, "қ": "q",
    "ғ": "g" + OKINA, "ҳ": "h",
}
_CYR_VOWELS = set("аеёиоуэюяў")

_APOSTROPHES = "'‘’`ʻʼ"
_AFTER_O_G = re.compile(r"([oOgG])[" + _APOSTROPHES + "]")
_OTHER = re.compile(r"(?<=\w)[" + _APOSTROPHES.replace(OKINA, "") + "]")

# Longest sequences first.
_LAT_TO_CYR = [
    ("s" + TUTUQ + "h", "сҳ"),  # Isʼhoq: the apostrophe separates s and h
    ("o" + OKINA, "ў"), ("g" + OKINA, "ғ"),
    ("sh", "ш"), ("ch", "ч"), ("yo", "ё"), ("yu", "ю"), ("ya", "я"),
    ("ye", "е"), ("ts", "ц"),
    ("a", "а"), ("b", "б"), ("d", "д"), ("e", "е"), ("f", "ф"), ("g", "г"), ("h", "ҳ"),
    ("i", "и"), ("j", "ж"), ("k", "к"), ("l", "л"), ("m", "м"), ("n", "н"),
    ("o", "о"), ("p", "п"), ("q", "қ"), ("r", "р"), ("s", "с"), ("t", "т"),
    ("u", "у"), ("v", "в"), ("x", "х"), ("y", "й"), ("z", "з"),
    (TUTUQ, "ъ"),
]
_LAT_VOWELS = set("aeiou")


def fix_apostrophes(text: str) -> str:
    """Use ʻ after o/g and ʼ elsewhere inside words (o'zbek -> oʻzbek)."""
    text = _AFTER_O_G.sub(lambda m: m.group(1) + OKINA, text)
    return _OTHER.sub(TUTUQ, text)


def to_latin(text: str) -> str:
    """Transliterate Uzbek Cyrillic to Latin.

    >>> to_latin("Ўзбекистон")
    'Oʻzbekiston'
    """
    out = []
    for i, char in enumerate(text):
        lower = char.lower()
        prev = text[i - 1].lower() if i else ""
        next_char = text[i + 1] if i + 1 < len(text) else ""
        if lower == "е":
            # ye at the start of a word and after a vowel, ъ or ь
            starts = not prev.isalpha() or prev in _CYR_VOWELS or prev in "ъь"
            latin = "ye" if starts else "e"
        elif lower == "ц":
            # ts after a vowel, s elsewhere (цирк -> sirk, милиция -> militsiya)
            latin = "ts" if prev in _CYR_VOWELS else "s"
        elif lower in _CYR_TO_LAT:
            latin = _CYR_TO_LAT[lower]
        else:
            out.append(char)
            continue
        out.append(match_case(char, latin, next_char))
    return "".join(out)


def to_cyrillic(text: str) -> str:
    """Transliterate Uzbek Latin to Cyrillic.

    "s" + "ts" is ambiguous in Latin; "ts" always becomes ц.

    >>> to_cyrillic("Oʻzbekiston")
    'Ўзбекистон'
    """
    text = fix_apostrophes(text)
    out = []
    i = 0
    while i < len(text):
        prev = text[i - 1].lower() if i else ""
        for latin, cyrillic in _LAT_TO_CYR:
            chunk = text[i:i + len(latin)]
            if chunk.lower() != latin:
                continue
            if latin == "yo" and text[i + 2:i + 3] == OKINA:
                continue  # yoʻl is y + oʻ, not yo + ʻ
            if latin == "e" and (not prev.isalpha() or prev in _LAT_VOWELS):
                cyrillic = "э"  # word-initial e (ekran -> экран)
            out.append(cyrillic.upper() if chunk[0].isupper() else cyrillic)
            i += len(latin)
            break
        else:
            out.append(text[i])
            i += 1
    return "".join(out)
