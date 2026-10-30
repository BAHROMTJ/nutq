"""Persian (فارسی, Iran) and Dari (دری, Afghanistan).

Persian and Dari are written only in the Perso-Arabic script. Conversion
to and from Tajik Cyrillic lives in the Tajik module: use
``nutq.convert(text, "tg", to="Cyrl")``.
"""

from ...registry import Language, register
from .clean import clean
from .numbers import to_ordinal, to_words
from .verbalize import make_verbalizer

_persian = make_verbalizer("fa")
_dari = make_verbalizer("fa-AF")

PERSIAN = register(Language(
    code="fa",
    name="Persian",
    native_name="فارسی",
    default_script="Arab",
    scripts=("Arab",),
    cardinal=to_words,
    ordinal=to_ordinal,
    normalize=lambda text: _persian(clean(text)),
    clean=clean,
    aliases=("fas", "per", "pes", "fa-IR"),
    status="beta",
))

DARI = register(Language(
    code="fa-AF",
    name="Dari",
    native_name="دری",
    default_script="Arab",
    scripts=("Arab",),
    cardinal=to_words,
    ordinal=to_ordinal,
    normalize=lambda text: _dari(clean(text)),
    clean=clean,
    aliases=("prs", "dari"),
    status="beta",
))
