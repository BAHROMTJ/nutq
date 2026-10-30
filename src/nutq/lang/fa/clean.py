"""Clean up Persian/Dari text: Arabic letter forms, digits, ZWNJ, tatweel.

Text copied from Arabic keyboards or old websites mixes Arabic letters that
look the same as Persian ones (ي/ی, ك/ک). Search and models treat them as
different words, so they are unified here.
"""

import re
import unicodedata

ZWNJ = "‌"

_LETTERS = str.maketrans({
    "ي": "ی", "ى": "ی",
    "ك": "ک",
    "ە": "ه",
    "٠": "۰", "١": "۱", "٢": "۲", "٣": "۳", "٤": "۴",
    "٥": "۵", "٦": "۶", "٧": "۷", "٨": "۸", "٩": "۹",
})
_TATWEEL = "ـ"
_PRESENTATION_FORMS = re.compile(r"[ﭐ-﷿ﹰ-﻿]")
_ZWNJ_RUNS = re.compile("‌{2,}")
_ZWNJ_EDGES = re.compile(r"‌(?=[\s\W]|$)|(?<=[\s\W])‌|^‌")


def clean(text: str) -> str:
    """Return ``text`` with Persian letter forms, digits and ZWNJ unified.

    >>> clean("كتابي")
    'کتابی'
    """
    text = _PRESENTATION_FORMS.sub(lambda m: unicodedata.normalize("NFKC", m.group(0)), text)
    text = unicodedata.normalize("NFC", text)
    text = text.translate(_LETTERS)
    text = text.replace(_TATWEEL, "")
    text = _ZWNJ_RUNS.sub(ZWNJ, text)
    return _ZWNJ_EDGES.sub("", text)
