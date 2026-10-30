"""MCP server that gives AI assistants nutq's script conversion and normalization.

Language models often get Tajik Perso-Arabic spelling, Uzbek oʻ/gʻ letters or
number words wrong. These tools let an assistant call a tested
implementation instead of guessing.

Run it over stdio (what Claude Desktop, Claude Code and most clients use):

    nutq-mcp
"""

import functools
from typing import Optional

import nutq
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations

LANGUAGES_HELP = (
    "Language codes: tg (Tajik: Cyrl, Latn, Arab), fa (Persian, Iran: Arab), "
    "fa-AF or prs (Dari, Afghanistan: Arab), uz (Uzbek: Latn, Cyrl)."
)

server = MCPServer(
    name="nutq",
    version=nutq.__version__,
    instructions=(
        "Tools for Tajik, Persian, Dari and Uzbek text. Use convert_script to change "
        "the writing system (e.g. Tajik Cyrillic to Perso-Arabic, Uzbek Latin to "
        "Cyrillic), normalize_text to spell out numbers, dates, times, money and "
        "abbreviations before text-to-speech, and number_to_words for single numbers. "
        + LANGUAGES_HELP
    ),
    website_url="https://github.com/BAHROMTJ/nutq",
)

_PURE = ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False)


def _tool(fn):
    """Register ``fn`` as a tool; report bad input back to the model as a tool error."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except (ValueError, TypeError) as exc:  # unknown language, script, bad number
            raise ToolError(str(exc)) from exc
    return server.tool(annotations=_PURE)(wrapper)


@_tool
def convert_script(text: str, lang: str, to: str, source: Optional[str] = None) -> str:
    """Convert text to another writing system of the same language.

    Args:
        text: The text to convert.
        lang: Language code: tg, uz (fa and fa-AF use one script only; for
            Persian <-> Tajik Cyrillic use lang="tg").
        to: Target script: Cyrl, Latn or Arab (or cyrillic/latin/arabic).
        source: Source script; detected from the text when omitted.

    Tajik Perso-Arabic -> Cyrillic is experimental: Persian does not write
    short vowels, so unknown words come out approximate.
    """
    return nutq.convert(text, lang, to=to, source=source)


@_tool
def normalize_text(text: str, lang: str) -> str:
    """Rewrite numbers, dates, times, money, percentages, phone and version
    numbers, units and abbreviations as words, ready for text-to-speech.

    Example: ("Нархи 25 $ аст", "tg") -> "Нархи бисту панҷ доллар аст".
    Persian dates written year first (1405/01/12) are read as Solar Hijri.
    Uzbek text is answered in the script it is written in.
    """
    return nutq.normalize(text, lang)


@_tool
def number_to_words(number: int, lang: str, ordinal: bool = False, script: Optional[str] = None) -> str:
    """Spell out an integer in words.

    Args:
        number: The integer (negative numbers are allowed for cardinals).
        lang: tg, fa, fa-AF or uz.
        ordinal: True for "first, second, ..." forms.
        script: Output script (e.g. "Cyrl" for Uzbek Cyrillic, "Arab" for Tajik
            in Perso-Arabic); defaults to the language's main script.
    """
    return nutq.number_to_words(number, lang, ordinal=ordinal, script=script)


@_tool
def clean_text(text: str, lang: str) -> str:
    """Fix characters only: Latin letters hidden in Cyrillic words, Arabic ي/ك
    in Persian, Uzbek apostrophes (o'zbek -> oʻzbek), digit forms, ZWNJ.
    Use before searching, comparing or deduplicating text."""
    return nutq.clean(text, lang)


@_tool
def list_languages() -> list[dict]:
    """List supported languages with their scripts and status."""
    return [
        {"code": l.code, "name": l.name, "native_name": l.native_name,
         "scripts": list(l.scripts), "status": l.status}
        for l in nutq.languages()
    ]


def main():
    server.run()


if __name__ == "__main__":
    main()
