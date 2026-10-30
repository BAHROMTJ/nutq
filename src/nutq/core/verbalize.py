"""Language-independent pipeline that turns written text into speakable words.

A language describes *how* to say things (number words, dates, money) in a
:class:`Verbalizer`; this module finds *where* those things are in the text.
Text-to-speech and language models need this because "12.03.2026" or "25 $"
have no pronunciation of their own.

The steps run in a fixed order, and each one replaces digits with words, so
later steps never see text an earlier step already handled:

1. language-specific rules (ordinal suffixes like "5-ум", "12-mart")
2. dates (DD.MM.YYYY, DD/MM/YYYY, YYYY-MM-DD)
3. times (14:30)
4. money ($25, 25 €, 100 смн)
5. percentages (15%)
6. negative numbers, decimals and integers (with space-separated thousands)
7. abbreviations
"""

import re
from dataclasses import dataclass, field
from typing import Callable, Dict, Match, Optional, Pattern, Sequence, Tuple

# Persian (U+06F0) and Arabic-Indic (U+0660) digits, and the Arabic decimal
# and thousands separators.
_DIGITS = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩٫٪",
    "01234567890123456789.%",
)
_THOUSANDS_SIGN = re.compile(r"(?<=\d)٬(?=\d{3})")

_INT = r"(?:\d{1,3}(?:[   ]\d{3})+(?!\d)|\d+)"
_NUM = _INT + r"(?:[.,]\d+)?"

_DATE_DMY = re.compile(r"(?<!\w)(\d{1,2})([./])(\d{1,2})\2(\d{4})(?!\w)")
_DATE_ISO = re.compile(r"(?<!\w)(\d{4})-(\d{2})-(\d{2})(?!\w)")
_TIME = re.compile(r"(?<![\w:])([01]?\d|2[0-3]):([0-5]\d)(?![\w:])")
_PERCENT = re.compile(r"(?<!\w)(" + _NUM + r")\s?%")
_NUMBER = re.compile(r"(?:(?<!\w)([-−])(?=\d))?(?<!\w)(" + _INT + r")(?:([.,])(\d+))?(?!\d)")
_SPACES = re.compile(r"[ \t]{2,}")
_LAST_WORD = re.compile(r"(\w+)\s*$")

Rule = Tuple[Pattern, Callable[[Match], str]]


def _int(text: str) -> int:
    return int(re.sub(r"\D", "", text))


def _split_number(text: str) -> Tuple[int, Optional[str]]:
    """Split "1 250,75" into (1250, "75")."""
    match = re.fullmatch(r"(" + _INT + r")(?:[.,](\d+))?", text)
    return _int(match.group(1)), match.group(2)


def _is_date(day: int, month: int) -> bool:
    return 1 <= day <= 31 and 1 <= month <= 12


@dataclass
class Verbalizer:
    """How one language says numbers, dates, times and money.

    Every callable returns words in the language's default script; ``render``
    can convert them afterwards (Uzbek uses it to answer Cyrillic text in
    Cyrillic).
    """

    cardinal: Callable[[int], str]
    ordinal: Callable[[int], str]
    decimal: Callable[[int, str], str]          # (integer part, fraction digits)
    percent: Callable[[str], str]               # number words -> "... percent"
    money: Callable[[int, Optional[int], str], str]  # (amount, cents, ISO code)
    date: Callable[[int, int, int], str]        # (day, month, year)
    time: Callable[[int, int], str]             # (hours, minutes)
    minus: str
    currency_symbols: Dict[str, str] = field(default_factory=dict)
    abbreviations: Dict[str, str] = field(default_factory=dict)
    rules: Sequence[Rule] = ()
    render: Callable[[str], str] = lambda words: words

    def __post_init__(self):
        symbols = sorted(self.currency_symbols, key=len, reverse=True)
        if symbols:
            sym = "|".join(re.escape(s) for s in symbols)
            self._money = re.compile(
                r"(?:(?<!\w)(?P<s1>" + sym + r")\s?(?P<n1>" + _NUM + r")"
                r"|(?<!\w)(?P<n2>" + _NUM + r")\s?(?P<s2>" + sym + r"))(?!\w)"
            )
        else:
            self._money = None
        abbrs = sorted(self.abbreviations, key=len, reverse=True)
        self._abbr = re.compile(
            r"(?<!\w)(" + "|".join(re.escape(a) for a in abbrs) + r")(?!\w)"
        ) if abbrs else None

    # -- helpers -------------------------------------------------------------

    def _out(self, words: str, match: Match) -> str:
        """Render ``words`` and keep them apart from a letter glued to the match."""
        words = self.render(words)
        text, end = match.string, match.end()
        if end < len(text) and text[end].isalpha():
            words += " "
        return words

    def number(self, text: str) -> str:
        integer, fraction = _split_number(text)
        if fraction is None:
            return self.cardinal(integer)
        return self.decimal(integer, fraction)

    # -- steps ---------------------------------------------------------------

    def _date_dmy(self, m: Match) -> str:
        day, month, year = int(m.group(1)), int(m.group(3)), int(m.group(4))
        if not _is_date(day, month):
            return m.group(0)
        return self._out(self.date(day, month, year), m)

    def _date_iso(self, m: Match) -> str:
        year, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if not _is_date(day, month):
            return m.group(0)
        return self._out(self.date(day, month, year), m)

    def _time(self, m: Match) -> str:
        words = self.time(int(m.group(1)), int(m.group(2)))
        # Don't repeat the word "hour" when the text already has it
        # ("соати 14:30" -> "соати чордаҳу сӣ").
        before = _LAST_WORD.search(m.string[:m.start()])
        first, _, rest = words.partition(" ")
        if before and rest:
            previous = before.group(1).lower()
            if first.lower().startswith(previous) or previous.startswith(first.lower()):
                words = rest
        return self._out(words, m)

    def _money_sub(self, m: Match) -> str:
        symbol = m.group("s1") or m.group("s2")
        amount, fraction = _split_number(m.group("n1") or m.group("n2"))
        cents = None
        if fraction is not None:
            cents = int(fraction.ljust(2, "0")[:2])
        return self._out(self.money(amount, cents or None, self.currency_symbols[symbol]), m)

    def _percent(self, m: Match) -> str:
        return self._out(self.percent(self.number(m.group(1))), m)

    def _number(self, m: Match) -> str:
        sign, integer, sep, fraction = m.groups()
        value = _int(integer)
        words = self.cardinal(value) if fraction is None else self.decimal(value, fraction)
        if sign:
            words = self.minus + " " + words
        return self._out(words, m)

    def _abbreviation(self, m: Match) -> str:
        return self.render(self.abbreviations[m.group(1)])

    def __call__(self, text: str) -> str:
        text = _THOUSANDS_SIGN.sub("", text).translate(_DIGITS)
        for pattern, handler in self.rules:
            text = pattern.sub(lambda m, h=handler: self._out(h(m), m), text)
        text = _DATE_DMY.sub(self._date_dmy, text)
        text = _DATE_ISO.sub(self._date_iso, text)
        text = _TIME.sub(self._time, text)
        if self._money is not None:
            text = self._money.sub(self._money_sub, text)
        text = _PERCENT.sub(self._percent, text)
        text = _NUMBER.sub(self._number, text)
        if self._abbr is not None:
            text = self._abbr.sub(self._abbreviation, text)
        return _SPACES.sub(" ", text)
