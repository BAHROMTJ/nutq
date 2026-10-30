"""Tajik (тоҷикӣ): Cyrillic, Latin and Perso-Arabic scripts."""

from ...registry import Language, register
from . import arabic, translit
from .clean import clean
from .numbers import to_ordinal, to_words
from .verbalize import verbalize

LANGUAGE = register(Language(
    code="tg",
    name="Tajik",
    native_name="тоҷикӣ",
    default_script="Cyrl",
    scripts=("Cyrl", "Latn", "Arab"),
    cardinal=to_words,
    ordinal=to_ordinal,
    normalize=lambda text: verbalize(clean(text)),
    clean=clean,
    converters={
        ("Cyrl", "Latn"): translit.to_latin,
        ("Latn", "Cyrl"): translit.to_cyrillic,
        ("Cyrl", "Arab"): arabic.to_arabic,
        ("Arab", "Cyrl"): arabic.to_cyrillic,
    },
    aliases=("tgk", "tg-Cyrl", "tg-TJ"),
    status="beta",
    experimental=(("Arab", "Cyrl"), ("Arab", "Latn")),
))
