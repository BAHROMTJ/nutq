"""Public functions. Each takes a language code and dispatches to its module."""

from typing import Optional

from .registry import get_language, resolve_script
from .scripts import detect_script


def convert(text: str, lang: str, to: str, source: Optional[str] = None) -> str:
    """Convert ``text`` in language ``lang`` to the script ``to``.

    ``source`` is detected from the text when omitted. Scripts are ISO 15924
    codes (``Cyrl``, ``Latn``, ``Arab``) or names (``latin``).

    >>> convert("Ўзбекистон", "uz", to="Latn")
    'Oʻzbekiston'
    """
    language = get_language(lang)
    target = resolve_script(language, to)
    source = resolve_script(language, source) or detect_script(text, language.scripts)
    if source is None or source == target:
        return text
    return language.converter(source, target)(text)


def number_to_words(n: int, lang: str, ordinal: bool = False, script: Optional[str] = None) -> str:
    """Spell out the integer ``n`` (``ordinal=True`` for 1st, 2nd, ...).

    >>> number_to_words(2026, "tg")
    'ду ҳазору бисту шаш'
    """
    language = get_language(lang)
    words = language.ordinal(n) if ordinal else language.cardinal(n)
    target = resolve_script(language, script)
    if target and target != language.default_script:
        words = language.converter(language.default_script, target)(words)
    return words


def normalize(text: str, lang: str) -> str:
    """Rewrite numbers, dates, times, money and abbreviations as words.

    Use this before text-to-speech or to give language models a consistent
    input. It also applies :func:`clean`.
    """
    return get_language(lang).normalize(text)


def clean(text: str, lang: str) -> str:
    """Fix characters only: look-alike letters, apostrophes, digit forms."""
    return get_language(lang).clean(text)
