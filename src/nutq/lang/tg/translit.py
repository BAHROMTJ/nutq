"""Transliteration between Tajik Cyrillic and Latin script.

The Latin scheme follows the common BGN/PCGN-style romanization of Tajik
(ҷ -> j, қ -> q, ғ -> gh, х -> kh, ҳ -> h, ӣ -> ī, ӯ -> ū).
"""

from ...core.case import match_case

_CYR_TO_LAT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "ғ": "gh", "д": "d",
    "е": "e", "ё": "yo", "ж": "zh", "з": "z", "и": "i", "ӣ": "ī",
    "й": "y", "к": "k", "қ": "q", "л": "l", "м": "m", "н": "n",
    "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ӯ": "ū", "ф": "f", "х": "kh", "ҳ": "h", "ч": "ch", "ҷ": "j",
    "ш": "sh", "ъ": "'", "э": "e", "ю": "yu", "я": "ya",
    # Russian letters that appear in loanwords
    "ц": "ts", "щ": "shch", "ы": "y", "ь": "",
}

_ASCII_FOLD = {"ī": "i", "ū": "u", "Ī": "I", "Ū": "U"}

# Longest sequences first so "shch" wins over "sh" and "kh" over "k".
_LAT_TO_CYR = [
    ("shch", "щ"), ("kh", "х"), ("gh", "ғ"), ("zh", "ж"), ("ch", "ч"),
    ("sh", "ш"), ("ts", "ц"), ("yo", "ё"), ("yu", "ю"), ("ya", "я"),
    ("a", "а"), ("b", "б"), ("v", "в"), ("g", "г"), ("d", "д"),
    ("e", "е"), ("z", "з"), ("i", "и"), ("ī", "ӣ"), ("y", "й"),
    ("k", "к"), ("q", "қ"), ("l", "л"), ("m", "м"), ("n", "н"),
    ("o", "о"), ("p", "п"), ("r", "р"), ("s", "с"), ("t", "т"),
    ("u", "у"), ("ū", "ӯ"), ("f", "ф"), ("h", "ҳ"), ("j", "ҷ"),
    ("'", "ъ"),
]


def to_latin(text: str, ascii_only: bool = False) -> str:
    """Transliterate Tajik Cyrillic text to Latin script.

    >>> to_latin("Тоҷикистон")
    'Tojikiston'
    """
    out = []
    for i, char in enumerate(text):
        lower = char.lower()
        if lower in _CYR_TO_LAT:
            next_char = text[i + 1] if i + 1 < len(text) else ""
            out.append(match_case(char, _CYR_TO_LAT[lower], next_char))
        else:
            out.append(char)
    result = "".join(out)
    if ascii_only:
        result = "".join(_ASCII_FOLD.get(c, c) for c in result)
    return result


def to_cyrillic(text: str) -> str:
    """Transliterate Latin-script Tajik back to Cyrillic.

    The conversion is greedy, so it is lossy for rare letter clusters
    (for example "к" followed by "ҳ" comes back as "х").

    >>> to_cyrillic("Dushanbe")
    'Душанбе'
    """
    out = []
    i = 0
    while i < len(text):
        for latin, cyrillic in _LAT_TO_CYR:
            chunk = text[i:i + len(latin)]
            if chunk.lower() == latin:
                out.append(cyrillic.upper() if chunk[0].isupper() else cyrillic)
                i += len(latin)
                break
        else:
            out.append(text[i])
            i += 1
    return "".join(out)
