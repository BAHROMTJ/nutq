"""Uzbek (oʻzbekcha / ўзбекча): Latin and Cyrillic scripts."""

import unicodedata

from ...core.lookalikes import fix_latin_in_cyrillic
from ...registry import Language, register
from ...scripts import detect_script
from . import translit, verbalize
from .numbers import to_ordinal, to_words


def clean(text: str) -> str:
    """Unify apostrophes (o'zbek -> oʻzbek) and fix Latin letters in Cyrillic words."""
    text = unicodedata.normalize("NFC", text)
    return fix_latin_in_cyrillic(translit.fix_apostrophes(text))


def normalize(text: str) -> str:
    text = clean(text)
    if detect_script(text, ("Latn", "Cyrl")) == "Cyrl":
        return verbalize.cyrillic(text)
    return verbalize.latin(text)


LANGUAGE = register(Language(
    code="uz",
    name="Uzbek",
    native_name="oʻzbekcha",
    default_script="Latn",
    scripts=("Latn", "Cyrl"),
    cardinal=to_words,
    ordinal=to_ordinal,
    normalize=normalize,
    clean=clean,
    converters={
        ("Cyrl", "Latn"): translit.to_latin,
        ("Latn", "Cyrl"): translit.to_cyrillic,
    },
    aliases=("uzb", "uz-Latn", "uz-Cyrl", "uz-UZ"),
    status="beta",
))
