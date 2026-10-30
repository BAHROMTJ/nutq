"""Language registry.

Every language is described by a :class:`Language` object. Built-in
languages live in ``nutq.lang`` and register themselves on import. Other
packages can add languages through the ``nutq.languages`` entry point group;
the entry point may point at a ``Language`` object or at a module that calls
:func:`register` when imported.
"""

import warnings
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

from .scripts import canonical_script

Converter = Callable[[str], str]


class UnsupportedError(ValueError):
    """Raised when a language, script or conversion is not available."""


@dataclass(frozen=True)
class Language:
    """Everything nutq knows about one language.

    ``cardinal`` and ``ordinal`` return words in ``default_script``.
    ``normalize`` turns written text into speakable words; ``clean`` only
    fixes characters (look-alike letters, apostrophes, digit forms).
    ``converters`` maps ``(source_script, target_script)`` to a function.
    """

    code: str
    name: str
    native_name: str
    default_script: str
    scripts: Tuple[str, ...]
    cardinal: Callable[[int], str]
    ordinal: Callable[[int], str]
    normalize: Converter
    clean: Converter
    converters: Dict[Tuple[str, str], Converter] = field(default_factory=dict)
    aliases: Tuple[str, ...] = ()
    status: str = "beta"
    experimental: Tuple[Tuple[str, str], ...] = ()

    def converter(self, source: str, target: str) -> Converter:
        """Return a function converting ``source`` script to ``target``.

        If there is no direct converter, a two-step path through a third
        script is used (for example Latin -> Cyrillic -> Arabic).
        """
        if (source, target) in self.converters:
            return self.converters[(source, target)]
        for (src, middle), first in self.converters.items():
            second = self.converters.get((middle, target))
            if src == source and second is not None:
                return lambda text, a=first, b=second: b(a(text))
        raise UnsupportedError(
            f"{self.code}: no conversion from {source} to {target}; "
            f"available: {', '.join(f'{s}->{t}' for s, t in sorted(self.converters))}"
        )


_LANGUAGES: Dict[str, Language] = {}
_ALIASES: Dict[str, str] = {}
_loaded = False


def register(language: Language) -> Language:
    """Add ``language`` to the registry (replacing one with the same code)."""
    _load()  # load the built-ins first, so ``language`` can replace one of them
    key = language.code.lower()
    _LANGUAGES[key] = language
    for alias in (language.code,) + language.aliases:
        _ALIASES[alias.lower()] = key
    return language


def _entry_points():
    from importlib.metadata import entry_points

    eps = entry_points()
    if hasattr(eps, "select"):
        return eps.select(group="nutq.languages")
    return eps.get("nutq.languages", [])


def _load():
    global _loaded
    if _loaded:
        return
    _loaded = True
    from . import lang  # noqa: F401  (registers the built-in languages)

    for ep in _entry_points():
        try:
            obj = ep.load()
        except Exception as exc:  # a broken plugin must not break nutq
            warnings.warn(f"nutq: could not load language plugin {ep.name!r}: {exc}")
            continue
        if isinstance(obj, Language):
            register(obj)


def get_language(code: str) -> Language:
    """Return the language for a BCP-47 or ISO 639 code (``tg``, ``fa-AF``, ``prs``)."""
    _load()
    key = _ALIASES.get(code.lower().replace("_", "-"))
    if key is None:
        raise UnsupportedError(
            f"unknown language {code!r}; available: {', '.join(sorted(l.code for l in _LANGUAGES.values()))}"
        )
    return _LANGUAGES[key]


def languages() -> List[Language]:
    """Return all registered languages, sorted by code."""
    _load()
    return sorted(_LANGUAGES.values(), key=lambda l: l.code)


def resolve_script(language: Language, script: Optional[str]) -> Optional[str]:
    if script is None:
        return None
    code = canonical_script(script)
    if code not in language.scripts:
        raise UnsupportedError(
            f"{language.code} is not written in {script!r}; scripts: {', '.join(language.scripts)}"
        )
    return code
