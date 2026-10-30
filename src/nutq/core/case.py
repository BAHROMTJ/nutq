"""Letter case helpers for transliteration."""


def match_case(source: str, target: str, next_char: str) -> str:
    """Apply the case of ``source`` to ``target``.

    A single uppercase letter that maps to several letters is fully
    uppercased inside an all-caps word (ШАҲР -> SHAHR) and only capitalised
    otherwise (Шаҳр -> Shahr).
    """
    if not source[0].isupper():
        return target
    if len(source) > 1 or len(target) <= 1:
        return target.upper()
    if next_char.isupper():
        return target.upper()
    return target[0].upper() + target[1:]
