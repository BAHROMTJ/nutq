"""Persian (Iran) and Dari (Afghanistan) text normalization for speech.

The two standards share number words but differ in month names, some
currency words and the words for "percent" and the decimal point. Forms
marked "verify" need confirmation from a native editor.
"""

import re
from typing import Dict, Optional, Tuple

from ...core.verbalize import Verbalizer
from .numbers import to_ordinal, to_words

GREGORIAN_MONTHS = {
    "fa": ["", "ژانویه", "فوریه", "مارس", "آوریل", "مه", "ژوئن",
           "ژوئیه", "اوت", "سپتامبر", "اکتبر", "نوامبر", "دسامبر"],
    # verify: Afghan media spelling of Gregorian months
    "fa-AF": ["", "جنوری", "فبروری", "مارچ", "اپریل", "می", "جون",
              "جولای", "آگست", "سپتمبر", "اکتوبر", "نومبر", "دسمبر"],
}

SOLAR_HIJRI_MONTHS = {
    "fa": ["", "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
           "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"],
    "fa-AF": ["", "حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
              "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"],
}

CURRENCIES: Dict[str, Tuple[str, Optional[str]]] = {
    "IRR": ("ریال", None),
    "AFN": ("افغانی", "پول"),
    "TJS": ("سامانی", "دیرم"),
    "USD": ("دلار", "سنت"),
    "EUR": ("یورو", "سنت"),
    "GBP": ("پوند", "پنی"),
    "RUB": ("روبل", "کوپک"),
}

CURRENCY_SYMBOLS = {"$": "USD", "€": "EUR", "£": "GBP", "₽": "RUB", "؋": "AFN", "﷼": "IRR"}

ABBREVIATIONS = {
    "ه.ش.": "هجری شمسی",
    "ه.ق.": "هجری قمری",
    "ق.م.": "قبل از میلاد",
    "ج.ا.ا.": "جمهوری اسلامی ایران",
}

_WORDS = {
    # (decimal point, percent) -- verify the Dari forms
    "fa": ("ممیز", "درصد"),
    "fa-AF": ("اعشاریه", "فیصد"),
}


def _decimal_reader(point: str):
    def decimal(integer: int, fraction: str) -> str:
        # 2.05 -> "دو ممیز صفر پنج": leading zeros are read one by one
        zeros = len(fraction) - len(fraction.lstrip("0"))
        rest = fraction.lstrip("0")
        parts = [to_words(integer), point] + ["صفر"] * zeros
        if rest:
            parts.append(to_words(int(rest)))
        return " ".join(parts)
    return decimal


def _money(amount: int, cents, code: str) -> str:
    unit, subunit = CURRENCIES[code]
    words = f"{to_words(amount)} {unit}"
    if cents and subunit:
        words += f" و {to_words(cents)} {subunit}"
    return words


def _time(hours: int, minutes: int) -> str:
    if not minutes:
        return f"ساعت {to_words(hours)}"
    return f"ساعت {to_words(hours)} و {to_words(minutes)} دقیقه"


def make_verbalizer(variant: str) -> Verbalizer:
    gregorian = GREGORIAN_MONTHS[variant]
    solar = SOLAR_HIJRI_MONTHS[variant]
    point, percent = _WORDS[variant]

    def date(day: int, month: int, year: int) -> str:
        # Years before 1500 are Solar Hijri (1405/01/12), others Gregorian.
        months = solar if year < 1500 else gregorian
        return f"{to_ordinal(day)} {months[month]} {to_words(year)}"

    def solar_date(m) -> str:
        # Iranian and Afghan dates are written year first: 1405/01/12
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if not (1 <= month <= 12 and 1 <= day <= 31):
            return m.group(0)
        return date(day, month, year)

    return Verbalizer(
        cardinal=to_words,
        ordinal=to_ordinal,
        decimal=_decimal_reader(point),
        percent=lambda words: f"{words} {percent}",
        money=_money,
        date=date,
        time=_time,
        minus="منفی",
        currency_symbols=CURRENCY_SYMBOLS,
        abbreviations=ABBREVIATIONS,
        rules=[
            (re.compile(r"(?<!\w)(\d{4})/(\d{1,2})/(\d{1,2})(?!\w)"), solar_date),
            # ۵ام, ۲۱م -> ordinal
            (re.compile(r"(?<!\w)(\d+)‌?(?:ام|م)(?!\w)"), lambda m: to_ordinal(int(m.group(1)))),
        ],
    )
