"""Clean up Tajik text typed with mixed or look-alike characters.

People often type Tajik on Russian or Kazakh keyboards, or paste text where
Latin letters that look like Cyrillic ones ("a", "o", "x") slipped into a
word. Such text looks right but breaks search, sorting and spell checking.
"""

import unicodedata

from ...core.lookalikes import fix_latin_in_cyrillic

# Characters from other alphabets that are used in place of Tajik letters.
_LOOKALIKES = {
    "һ": "ҳ", "Һ": "Ҳ",  # Kazakh/Bashkir shha
    "ӽ": "ҳ", "Ӽ": "Ҳ",
    "ҝ": "қ", "Ҝ": "Қ",
    "ҹ": "ҷ", "Ҹ": "Ҷ",  # Azerbaijani/Abkhaz che
    "ҫ": "с", "Ҫ": "С",
}


def clean(text: str) -> str:
    """Return ``text`` with look-alike characters replaced by Tajik letters.

    - composes letters typed with a combining macron (и + ̄ -> ӣ)
    - replaces letters borrowed from other Cyrillic alphabets (һ -> ҳ)
    - replaces Latin letters hidden inside Cyrillic words (Тoҷик -> Тоҷик)

    Words written fully in Latin script are left untouched.
    """
    text = unicodedata.normalize("NFC", text)
    text = "".join(_LOOKALIKES.get(c, c) for c in text)
    return fix_latin_in_cyrillic(text)
