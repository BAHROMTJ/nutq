"""Conversion between Tajik Cyrillic and the Perso-Arabic script.

Cyrillic -> Arabic works in three steps for each word:

1. look the word up in ``data/arabic_words.tsv`` (spellings rules can't guess)
2. strip a known suffix (-ҳо, -ро, izafat -и, ...) and look the stem up
3. fall back to letter rules

The rules cannot be exact. Persian does not write short vowels, and several
Arabic letters share one Tajik letter (с = س ص ث, з = ز ذ ض ظ, т = ت ط,
ҳ = ه ح). Tajik "и" and "у" stand for both short and long vowels, so the rules
always write them as ی and و; the word list fixes the common words where that
is wrong (дил -> دل, гул -> گل). Native speakers: please add words to the list.

Arabic -> Cyrillic is experimental: without short vowels a word can only be
read reliably with a dictionary, so unknown words come out approximate.
"""

import re
from functools import lru_cache
from importlib import resources
from typing import Dict, Tuple

from . import numbers

ZWNJ = "‌"

_VOWELS = set("аеёиӣоуӯэюя")

_CONSONANTS = {
    "б": "ب", "в": "و", "г": "گ", "ғ": "غ", "д": "د", "ж": "ژ", "з": "ز",
    "й": "ی", "к": "ک", "қ": "ق", "л": "ل", "м": "م", "н": "ن", "п": "پ",
    "р": "ر", "с": "س", "т": "ت", "ф": "ف", "х": "خ", "ҳ": "ه", "ч": "چ",
    "ҷ": "ج", "ш": "ش", "ъ": "ع", "ц": "تس", "щ": "شچ", "ь": "",
}

# (initial, medial, final) spelling of each vowel.
_VOWEL_FORMS = {
    "а": ("ا", "", "ه"),
    "о": ("آ", "ا", "ا"),
    "и": ("ای", "ی", "ی"),
    "ӣ": ("ای", "ی", "ی"),
    "у": ("او", "و", "و"),
    "ӯ": ("او", "و", "و"),
    "е": ("ای", "ی", "ی"),
    "э": ("ا", "", "ه"),
    "ё": ("یا", "یا", "یا"),
    "ю": ("یو", "یو", "یو"),
    "я": ("ی", "ی", "یه"),
    "ы": ("ی", "ی", "ی"),
}

# Suffix, Arabic form, shortest stem it can follow.
_SUFFIXES = (
    ("ҳоро", ZWNJ + "ها را", 2),
    ("ҳои", ZWNJ + "های", 2),
    ("ҳо", ZWNJ + "ها", 2),
    ("ро", " را", 3),
    ("тарин", ZWNJ + "ترین", 3),  # comparative: калонтарин -> کلان‌ترین
    ("тар", ZWNJ + "تر", 3),      # ширинтар -> شیرین‌تر (дафтар is in the word list)
    ("ён", "یان", 3),  # plural after a vowel: донишҷӯён -> دانشجویان
    ("и", "", 3),  # izafat; not written after a consonant
)

# Verb and word stems whose spelling the letter rules can't guess; matched
# at the start of a word, also after the negative "на-" (нахонд -> نخواند).
_STEMS = (
    ("хонд", "خواند"), ("хоҳ", "خواه"), ("хост", "خواست"), ("хоб", "خواب"),
    ("кун", "کن"), ("шуд", "شد"), ("гуфт", "گفت"),
)

# Present-tense verbs: ме-/наме- + stem + personal ending (мешавад -> می‌شود).
_VERB = re.compile(r"(на)?ме(?![ҳъ])(\w+(?:ам|ӣ|ад|ем|ед|анд|ям|яд|янд))")

_PUNCT = str.maketrans({",": "،", "?": "؟", ";": "؛", "%": "٪"})
_PUNCT_BACK = str.maketrans({"،": ",", "؟": "?", "؛": ";", "٪": "%", "‌": ""})
_TO_PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
_TO_LATIN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

_CYR_WORD = re.compile(r"[Ѐ-ԯ]+")
_ARAB_WORD = re.compile(r"[ء-غف-ْٱ-ۓ‌]+")
_DIGIT_ORDINAL = re.compile(r"(\d)-?(?:ум|юм)и?(?![Ѐ-ԯ])")  # 21-ум -> ۲۱م
_DECIMAL = re.compile(r"(?<=\d)[.,](?=\d)")


@lru_cache(maxsize=None)
def _word_list() -> Tuple[Dict[str, str], Dict[str, str]]:
    """Return (cyrillic -> arabic, arabic -> cyrillic) from the data file."""
    to_arabic, to_cyrillic = {}, {}
    text = resources.files(__package__).joinpath("data/arabic_words.tsv").read_text("utf-8")
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        cyrillic, arabic = (part.strip() for part in line.split("\t") if part.strip())
        to_arabic[cyrillic.lower()] = arabic
        to_cyrillic.setdefault(arabic, cyrillic)
    return to_arabic, to_cyrillic


_IOTATED = {"я": "а", "ё": "о", "ю": "у"}


def _rules(word: str) -> str:
    verb = _VERB.fullmatch(word)
    if verb:
        return ("نمی" if verb.group(1) else "می") + ZWNJ + _rules(verb.group(2))
    for stem, arabic in _STEMS:
        for lead, lead_arabic in (("", ""), ("на", "ن")):
            if word.startswith(lead + stem):
                plain = _letters(lead + stem)
                spelled = _letters(word)
                if spelled.startswith(plain):
                    return lead_arabic + arabic + spelled[len(plain):]
    return _letters(word)


def _letters(word: str) -> str:
    out = []
    last = len(word) - 1
    for i, char in enumerate(word):
        if i > 0 and char == word[i - 1] and char not in _VOWELS:
            continue  # double consonants are written once (миллат -> ملت)
        if char in _VOWEL_FORMS:
            initial, medial, final = _VOWEL_FORMS[char]
            if char in _IOTATED and i > 0 and word[i - 1] in "иӣ":
                # the "й" is already in the и: Русия -> روسیه, адабиёт -> ادبیات
                initial, medial, final = _VOWEL_FORMS[_IOTATED[char]]
            if i == 0:
                out.append(initial)
            elif i == last:
                out.append(final)
            elif word[i - 1] in _VOWELS and char in "аэ":
                out.append("ا")  # a vowel after a vowel needs a carrier
            else:
                out.append(medial)
        else:
            out.append(_CONSONANTS.get(char, char))
    return "".join(out)


def _attach(stem: str, suffix: str, arabic_suffix: str) -> str:
    if suffix == "и" and stem.endswith(("ه", "ا", "و")):
        # izafat after a vowel: خانه‌ی, دریای
        return stem + (ZWNJ if stem.endswith("ه") else "") + "ی"
    return stem + arabic_suffix


# Number words, so that the linking "-у" can be written as a separate و
# (бисту панҷ -> بیست و پنج).
_NUMBER_WORDS = set(
    numbers._ONES + numbers._TEENS + numbers._TENS + numbers._HUNDREDS + numbers._SCALES
) - {""}


def _number_with_conjunction(lower: str):
    if lower.endswith("иву") and lower[:-3] + "ӣ" in _NUMBER_WORDS:
        return lower[:-3] + "ӣ"
    if lower[-1:] in ("у", "ю") and lower[:-1] in _NUMBER_WORDS:
        return lower[:-1]
    return None


def _noun_with_conjunction(lower: str, words: Dict[str, str]):
    """Return the stem of a word ending in the linking "-у"/"-ю" (шаъну -> шаън).

    "-у" follows a consonant and "-ю" a vowel. Short words (ту, ду, бӯ) and
    words where the ending is part of the stem (тарозу) are in the word list.
    """
    stem, last = lower[:-1], lower[-1:]
    if not stem or last not in ("у", "ю"):
        return None
    after_vowel = stem[-1] in _VOWELS
    if (last == "у") == after_vowel:
        return None
    if stem in words or len(stem) >= (3 if after_vowel else 4):
        return stem
    return None


def _ordinal(lower: str):
    """Return the number word of an ordinal (якум -> як, сиюм -> сӣ)."""
    if lower.endswith("июм") and lower[:-3] + "ӣ" in _NUMBER_WORDS:
        return lower[:-3] + "ӣ"
    if lower[-2:] in ("ум", "юм") and lower[:-2] in _NUMBER_WORDS:
        return lower[:-2]
    return None


def word_to_arabic(word: str) -> str:
    """Convert one Cyrillic word (any case) to Perso-Arabic script."""
    words, _ = _word_list()
    lower = word.lower()
    if lower in words:
        return words[lower]
    number = _number_with_conjunction(lower) or _noun_with_conjunction(lower, words)
    if number:
        return word_to_arabic(number) + " و"
    number = _ordinal(lower)
    if number:
        if number == "се":
            return "سوم"
        arabic = word_to_arabic(number)
        return arabic + (ZWNJ + "ام" if arabic.endswith("ی") else "م")
    for suffix, arabic, min_stem in _SUFFIXES:
        stem = lower[: -len(suffix)]
        if lower.endswith(suffix) and len(stem) >= min_stem:
            if suffix == "и" and stem.endswith("и"):
                stem = stem[:-1] + "ӣ"  # давлатии = давлатӣ + izafat
            return _attach(word_to_arabic(stem), suffix, arabic)
    return _rules(lower)


def to_arabic(text: str) -> str:
    """Convert Tajik Cyrillic text to Perso-Arabic script.

    >>> to_arabic("Забони тоҷикӣ")
    'زبان تاجیکی'
    """
    text = _DIGIT_ORDINAL.sub(r"\1م", text)
    text = _CYR_WORD.sub(lambda m: word_to_arabic(m.group(0)), text)
    text = _DECIMAL.sub("٫", text)
    return text.translate(_PUNCT).translate(_TO_PERSIAN_DIGITS)


# -- Arabic -> Cyrillic (experimental) -----------------------------------------

_HARAKAT = {"َ": "а", "ِ": "и", "ُ": "у", "ْ": "", "ً": "ан"}

_BACK = {
    "ب": "б", "پ": "п", "ت": "т", "ث": "с", "ج": "ҷ", "چ": "ч", "ح": "ҳ",
    "خ": "х", "د": "д", "ذ": "з", "ر": "р", "ز": "з", "ژ": "ж", "س": "с",
    "ش": "ш", "ص": "с", "ض": "з", "ط": "т", "ظ": "з", "ع": "ъ", "غ": "ғ",
    "ف": "ф", "ق": "қ", "ک": "к", "ك": "к", "گ": "г", "ل": "л", "م": "м",
    "ن": "н", "ء": "ъ", "أ": "а", "إ": "и", "ؤ": "ӯ", "ئ": "и", "ة": "а",
}


def _rules_back(word: str) -> str:
    out = []
    last = len(word) - 1
    for i, char in enumerate(word):
        prev_vowel = i > 0 and word[i - 1] in "اآویه"
        if char == "آ":
            out.append("о")
        elif char == "ا":
            out.append("а" if i == 0 else "о")
        elif char == "و":
            out.append("в" if i == 0 or (prev_vowel and i < last) else "у")
        elif char in "یي":
            if i == 0:
                out.append("й")
            else:
                out.append("ӣ" if i == last else "и")
        elif char == "ه":
            out.append("а" if i == last and i > 0 else "ҳ")
        elif char == "ّ" and out:
            out.append(out[-1])  # shadda doubles the consonant
        elif char in _HARAKAT:
            out.append(_HARAKAT[char])
        else:
            out.append(_BACK.get(char, char))
    result = "".join(out)
    if result.startswith("ъ"):
        result = result[1:]
    if len(result) > 2 and result[0] not in _VOWELS and result[1] not in _VOWELS:
        # Tajik words do not start with two consonants; the missing short
        # vowel is most often "а" (سلام -> салом).
        result = result[0] + "а" + result[1:]
    return result


def word_to_cyrillic(word: str) -> str:
    _, words = _word_list()
    if word in words:
        return words[word]
    for prefix, cyrillic in (("نمی" + ZWNJ, "наме"), ("می" + ZWNJ, "ме")):
        if word.startswith(prefix) and len(word) > len(prefix):
            return cyrillic + word_to_cyrillic(word[len(prefix):])
    for arabic, cyrillic in ((ZWNJ + "ها", "ҳо"), ("ها", "ҳо"), (ZWNJ + "های", "ҳои")):
        if word.endswith(arabic) and len(word) > len(arabic):
            return word_to_cyrillic(word[: -len(arabic)]) + cyrillic
    # خوا is read "хо" (خواندن -> хондан)
    return _rules_back(word.replace(ZWNJ, "").replace("خوا", "خا"))


def to_cyrillic(text: str) -> str:
    """Convert Perso-Arabic text to Tajik Cyrillic (experimental, approximate)."""
    text = _ARAB_WORD.sub(lambda m: word_to_cyrillic(m.group(0)), text)
    return text.replace("٫", ",").translate(_PUNCT_BACK).translate(_TO_LATIN_DIGITS)
