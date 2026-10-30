"""Tajik text normalization for speech: numbers, dates, money as words.

Forms marked "verify" below were chosen by the authors and still need
confirmation from a Tajik editor or linguist.
"""

import re

from ...core.verbalize import Verbalizer
from .numbers import to_ordinal, to_words, with_conjunction

MONTHS = [
    "", "январ", "феврал", "март", "апрел", "май", "июн",
    "июл", "август", "сентябр", "октябр", "ноябр", "декабр",
]

# ISO code -> (unit, subunit)
CURRENCIES = {
    "TJS": ("сомонӣ", "дирам"),
    "USD": ("доллар", "сент"),
    "EUR": ("евро", "сент"),
    "RUB": ("рубл", "копейка"),
    "GBP": ("фунт", "пенс"),
}

CURRENCY_SYMBOLS = {"$": "USD", "€": "EUR", "₽": "RUB", "£": "GBP", "смн": "TJS"}

ABBREVIATIONS = {
    "ҶТ": "Ҷумҳурии Тоҷикистон",
    "ИДМ": "Иттиҳоди Давлатҳои Мустақил",
    "СММ": "Созмони Милали Муттаҳид",
    "ва ғ.": "ва ғайра",
    "ва ҳ.к.": "ва ҳоказо",
    "млн": "миллион",
    "млрд": "миллиард",
    "км": "километр",
    "кг": "килограмм",
    "см": "сантиметр",
    "мм": "миллиметр",
}

# Decimal fractions: 2,5 -> "ду бутуну панҷ даҳум" (verify).
_DENOMINATORS = {1: "даҳум", 2: "садум", 3: "ҳазорум"}


def _decimal(integer: int, fraction: str) -> str:
    denominator = _DENOMINATORS.get(len(fraction))
    if denominator is None:
        digits = " ".join(to_words(int(d)) for d in fraction)
        return f"{to_words(integer)} бутуну {digits}"
    return f"{to_words(integer)} бутуну {to_words(int(fraction))} {denominator}"


def _money(amount: int, cents, code: str) -> str:
    unit, subunit = CURRENCIES[code]
    words = f"{to_words(amount)} {unit}"
    if cents:
        words = f"{with_conjunction(words)} {to_words(cents)} {subunit}"
    return words


def _date(day: int, month: int, year: int) -> str:
    # 12.03.2026 -> "дувоздаҳуми марти соли ду ҳазору бисту шаш"
    return f"{to_ordinal(day)}и {MONTHS[month]}и соли {to_words(year)}"


def _time(hours: int, minutes: int) -> str:
    # 14:30 -> "соати чордаҳу сӣ"
    if not minutes:
        return f"соати {to_words(hours)}"
    return f"соати {with_conjunction(to_words(hours))} {to_words(minutes)}"


# 5-ум, 2-юм, 21-уми -> ordinal (with the izafat "и" kept)
_ORDINAL = re.compile(r"(?<!\w)(\d+)-?(?:ум|юм)(и?)(?!\w)")

verbalize = Verbalizer(
    cardinal=to_words,
    ordinal=to_ordinal,
    decimal=_decimal,
    percent=lambda words: f"{words} фоиз",
    money=_money,
    date=_date,
    time=_time,
    minus="минус",
    dot="нуқта",
    currency_symbols=CURRENCY_SYMBOLS,
    units={"°C": "дараҷа", "°": "дараҷа"},
    abbreviations=ABBREVIATIONS,
    rules=[(_ORDINAL, lambda m: to_ordinal(int(m.group(1))) + m.group(2))],
)
