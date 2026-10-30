"""Convert integers to Uzbek words (Latin script).

Spoken forms are used: 100 is "yuz" and 1000 is "ming", not "bir yuz" /
"bir ming" as in some legal documents (verify with a native editor).
"""

_ONES = ["", "bir", "ikki", "uch", "toʻrt", "besh", "olti", "yetti", "sakkiz", "toʻqqiz"]
_TENS = ["", "oʻn", "yigirma", "oʻttiz", "qirq", "ellik", "oltmish", "yetmish", "sakson", "toʻqson"]
_SCALES = ["", "ming", "million", "milliard", "trillion", "kvadrillion"]

_VOWELS = set("aeiou")


def _under_thousand(n: int):
    parts = []
    hundreds, rest = divmod(n, 100)
    if hundreds:
        if hundreds > 1:
            parts.append(_ONES[hundreds])
        parts.append("yuz")
    tens, ones = divmod(rest, 10)
    if tens:
        parts.append(_TENS[tens])
    if ones:
        parts.append(_ONES[ones])
    return parts


def to_words(n: int) -> str:
    """Return the Uzbek cardinal number for ``n``.

    >>> to_words(2026)
    'ikki ming yigirma olti'
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("to_words() expects an int")
    if n == 0:
        return "nol"
    if n < 0:
        return "minus " + to_words(-n)

    groups = []
    scale = 0
    while n:
        n, group = divmod(n, 1000)
        if group:
            if scale >= len(_SCALES):
                raise ValueError("number is too large")
            if scale == 1 and group == 1:
                parts = []
            else:
                parts = _under_thousand(group)
            if _SCALES[scale]:
                parts.append(_SCALES[scale])
            groups.append(" ".join(parts))
        scale += 1
    return " ".join(reversed(groups))


def to_ordinal(n: int) -> str:
    """Return the Uzbek ordinal number for ``n`` (1 -> birinchi).

    >>> to_ordinal(2)
    'ikkinchi'
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("to_ordinal() expects an int")
    if n < 1:
        raise ValueError("ordinals are defined for positive numbers")
    words = to_words(n)
    return words + ("nchi" if words[-1] in _VOWELS else "inchi")
