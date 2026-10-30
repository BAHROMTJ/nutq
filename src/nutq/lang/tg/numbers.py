"""Convert integers to Tajik words (cardinal and ordinal)."""

_ONES = ["", "як", "ду", "се", "чор", "панҷ", "шаш", "ҳафт", "ҳашт", "нӯҳ"]
_TEENS = [
    "даҳ", "ёздаҳ", "дувоздаҳ", "сенздаҳ", "чордаҳ",
    "понздаҳ", "шонздаҳ", "ҳабдаҳ", "ҳаждаҳ", "нуздаҳ",
]
_TENS = ["", "", "бист", "сӣ", "чил", "панҷоҳ", "шаст", "ҳафтод", "ҳаштод", "навад"]
_HUNDREDS = [
    "", "сад", "дусад", "сесад", "чорсад",
    "панҷсад", "шашсад", "ҳафтсад", "ҳаштсад", "нӯҳсад",
]
_SCALES = ["", "ҳазор", "миллион", "миллиард", "триллион", "квадриллион"]

VOWELS = set("аеёиӣоуӯэюя")


def with_conjunction(word: str) -> str:
    """Attach the linking conjunction "у" (and) to the end of a word.

    бист -> бисту, сӣ -> сиву, ду -> дую
    """
    if word.endswith("ӣ"):
        return word[:-1] + "иву"
    if word[-1] in VOWELS:
        return word + "ю"
    return word + "у"


def _join(parts):
    result = parts[0]
    for part in parts[1:]:
        result = with_conjunction(result) + " " + part
    return result


def _under_thousand(n: int):
    parts = []
    hundreds, rest = divmod(n, 100)
    if hundreds:
        parts.append(_HUNDREDS[hundreds])
    if 10 <= rest < 20:
        parts.append(_TEENS[rest - 10])
    else:
        tens, ones = divmod(rest, 10)
        if tens:
            parts.append(_TENS[tens])
        if ones:
            parts.append(_ONES[ones])
    return parts


def to_words(n: int) -> str:
    """Return the Tajik cardinal number for ``n``.

    >>> to_words(2026)
    'ду ҳазору бисту шаш'
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("to_words() expects an int")
    if n == 0:
        return "сифр"
    if n < 0:
        return "минус " + to_words(-n)

    groups = []
    scale = 0
    while n:
        n, group = divmod(n, 1000)
        if group:
            if scale >= len(_SCALES):
                raise ValueError("number is too large")
            text = _join(_under_thousand(group))
            if _SCALES[scale]:
                text += " " + _SCALES[scale]
            groups.append(text)
        scale += 1
    return _join(list(reversed(groups)))


def to_ordinal(n: int) -> str:
    """Return the Tajik ordinal number for ``n`` (1 -> якум, 2 -> дуюм).

    >>> to_ordinal(3)
    'сеюм'
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("to_ordinal() expects an int")
    if n < 1:
        raise ValueError("ordinals are defined for positive numbers")
    words = to_words(n)
    if words.endswith("ӣ"):
        return words[:-1] + "июм"
    if words[-1] in VOWELS:
        return words + "юм"
    return words + "ум"
