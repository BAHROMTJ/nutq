"""Convert integers to Persian words (cardinal and ordinal)."""

_ONES = ["", "یک", "دو", "سه", "چهار", "پنج", "شش", "هفت", "هشت", "نه"]
_TEENS = [
    "ده", "یازده", "دوازده", "سیزده", "چهارده",
    "پانزده", "شانزده", "هفده", "هجده", "نوزده",
]
_TENS = ["", "", "بیست", "سی", "چهل", "پنجاه", "شصت", "هفتاد", "هشتاد", "نود"]
_HUNDREDS = [
    "", "صد", "دویست", "سیصد", "چهارصد",
    "پانصد", "ششصد", "هفتصد", "هشتصد", "نهصد",
]
_SCALES = ["", "هزار", "میلیون", "میلیارد", "تریلیون", "کوادریلیون"]

ZWNJ = "‌"
AND = " و "


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
    """Return the Persian cardinal number for ``n``.

    >>> to_words(2026)
    'دو هزار و بیست و شش'
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("to_words() expects an int")
    if n == 0:
        return "صفر"
    if n < 0:
        return "منفی " + to_words(-n)

    groups = []
    scale = 0
    while n:
        n, group = divmod(n, 1000)
        if group:
            if scale >= len(_SCALES):
                raise ValueError("number is too large")
            if scale == 1 and group == 1:
                text = _SCALES[1]  # "هزار", not "یک هزار"
            else:
                text = AND.join(_under_thousand(group))
                if _SCALES[scale]:
                    text += " " + _SCALES[scale]
            groups.append(text)
        scale += 1
    return AND.join(reversed(groups))


def to_ordinal(n: int) -> str:
    """Return the Persian ordinal number for ``n`` (1 -> یکم, 3 -> سوم).

    >>> to_ordinal(23)
    'بیست و سوم'
    """
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("to_ordinal() expects an int")
    if n < 1:
        raise ValueError("ordinals are defined for positive numbers")
    words = to_words(n)
    if words.endswith("سه"):
        return words[:-2] + "سوم"
    if words.endswith("ی"):
        return words + ZWNJ + "ام"  # سی -> سی‌ام
    return words + "م"
