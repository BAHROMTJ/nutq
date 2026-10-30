"""Uzbek text normalization for speech, in Latin or Cyrillic script.

Words are generated in Latin and converted to Cyrillic when the input text
is Cyrillic. All forms here still need review by a native Uzbek speaker.
"""

import re

from ...core.verbalize import Verbalizer
from .numbers import to_ordinal, to_words
from .translit import to_cyrillic

MONTHS = [
    "", "yanvar", "fevral", "mart", "aprel", "may", "iyun",
    "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr",
]

CURRENCIES = {
    "UZS": ("soʻm", "tiyin"),
    "USD": ("dollar", "sent"),
    "EUR": ("yevro", "sent"),
    "RUB": ("rubl", "kopek"),
    "GBP": ("funt", "pens"),
}

CURRENCY_SYMBOLS = {"$": "USD", "€": "EUR", "₽": "RUB", "£": "GBP"}

ABBREVIATIONS = {
    "OʻzR": "Oʻzbekiston Respublikasi",
    "BMT": "Birlashgan Millatlar Tashkiloti",
    "AQSH": "Amerika Qoʻshma Shtatlari",
    "va h.k.": "va hokazo",
    "mln": "million",
    "mlrd": "milliard",
    "km": "kilometr",
    "kg": "kilogramm",
    "sm": "santimetr",
    "mm": "millimetr",
}

_DENOMINATORS = {1: "oʻndan", 2: "yuzdan", 3: "mingdan"}


def _decimal(integer: int, fraction: str) -> str:
    # 2,5 -> "ikki butun oʻndan besh"
    denominator = _DENOMINATORS.get(len(fraction))
    if denominator is None:
        digits = " ".join(to_words(int(d)) for d in fraction)
        return f"{to_words(integer)} butun {digits}"
    return f"{to_words(integer)} butun {denominator} {to_words(int(fraction))}"


def _money(amount: int, cents, code: str) -> str:
    unit, subunit = CURRENCIES[code]
    words = f"{to_words(amount)} {unit}"
    if cents:
        words += f" {to_words(cents)} {subunit}"
    return words


def _date(day: int, month: int, year: int) -> str:
    # 12.03.2026 is said like "2026-yil 12-mart" (verify)
    return f"{to_ordinal(year)} yil {to_ordinal(day)} {MONTHS[month]}"


def _time(hours: int, minutes: int) -> str:
    if not minutes:
        return f"soat {to_words(hours)}"
    return f"soat {to_words(hours)} {to_words(minutes)} daqiqa"  # verify


_LATIN_RULES = [
    # 5-inchi, 3-chi -> ordinal
    (re.compile(r"(?<!\w)(\d+)-(?:inchi|nchi|chi)(?!\w)"), lambda m: to_ordinal(int(m.group(1)))),
    # 12-mart, 2026-yil, 5-sinf: a hyphen before a word marks an ordinal
    (re.compile(r"(?<!\w)(\d+)-(?=[^\W\d_])"), lambda m: to_ordinal(int(m.group(1)))),
]
_CYRILLIC_RULES = [
    (re.compile(r"(?<!\w)(\d+)-(?:инчи|нчи|чи)(?!\w)"), lambda m: to_ordinal(int(m.group(1)))),
    (re.compile(r"(?<!\w)(\d+)-(?=[^\W\d_])"), lambda m: to_ordinal(int(m.group(1)))),
]


def _before_date_word(words):
    """A number before "yil" or a month name is an ordinal even without a hyphen."""
    return (
        re.compile(r"(?<!\w)(\d+)(?=\s+(?:" + "|".join(words) + r"))", re.IGNORECASE),
        lambda m: to_ordinal(int(m.group(1))),
    )


_DATE_WORDS = ["yil"] + MONTHS[1:]
_LATIN_RULES.append(_before_date_word(_DATE_WORDS))
_CYRILLIC_RULES.append(_before_date_word([to_cyrillic(w) for w in _DATE_WORDS]))


def _make(script: str) -> Verbalizer:
    cyrillic = script == "Cyrl"
    symbols = dict(CURRENCY_SYMBOLS)
    symbols["soʻm" if not cyrillic else "сўм"] = "UZS"
    abbreviations = (
        {to_cyrillic(k): v for k, v in ABBREVIATIONS.items()} if cyrillic else ABBREVIATIONS
    )
    return Verbalizer(
        cardinal=to_words,
        ordinal=to_ordinal,
        decimal=_decimal,
        percent=lambda words: f"{words} foiz",
        money=_money,
        date=_date,
        time=_time,
        minus="minus",
        dot="nuqta",
        currency_symbols=symbols,
        units={"°C": "daraja", "°": "daraja"},
        abbreviations=abbreviations,
        rules=_CYRILLIC_RULES if cyrillic else _LATIN_RULES,
        render=to_cyrillic if cyrillic else (lambda words: words),
    )


latin = _make("Latn")
cyrillic = _make("Cyrl")
