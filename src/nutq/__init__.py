"""nutq: script conversion and text normalization for underserved languages.

>>> import nutq
>>> nutq.convert("Тоҷикистон", "tg", to="Arab")
'تاجیکستان'
>>> nutq.normalize("15%", "uz")
'oʻn besh foiz'
"""

from .api import clean, convert, normalize, number_to_words
from .registry import Language, UnsupportedError, get_language, languages, register
from .scripts import detect_script

__all__ = [
    "Language", "UnsupportedError", "clean", "convert", "detect_script",
    "get_language", "languages", "normalize", "number_to_words", "register",
]
__version__ = "0.1.0"
