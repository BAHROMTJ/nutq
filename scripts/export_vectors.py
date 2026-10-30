"""Export test vectors: every call the Python test suite makes, with its result.

The Python package is the reference implementation. Other ports (js/) run
the same vectors, so they produce exactly the same output.

    python scripts/export_vectors.py   # writes js/test/vectors.json
"""

import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import nutq  # noqa: E402

# Extra inputs on top of what the tests use.
EXTRA = [
    ("normalize", ("Соли 2026 дар Душанбе 1 200 000 нафар зиндагӣ мекунанд.", "tg"), {}),
    ("normalize", ("Нарх: 3,75 смн; тахфиф 12,5%.", "tg"), {}),
    ("normalize", ("Вохӯрӣ 01.09.2026 соати 08:00 аст.", "tg"), {}),
    ("normalize", ("€15 ва £3.5 ва 100$", "tg"), {}),
    ("normalize", ("در سال ۱۳۹۹ حدود ۸۵٬۰۰۰٬۰۰۰ نفر", "fa"), {}),
    ("normalize", ("کابل ۱۴۰۳/۰۵/۲۸", "fa-AF"), {}),
    ("normalize", ("Narxi 1 250 000 so'm, 3-sentabr, soat 18:00 da", "uz"), {}),
    ("convert", ("Тоҷикистон дар Осиёи Марказӣ ҷойгир аст. Пойтахти он шаҳри Душанбе мебошад.", "tg"), {"to": "Arab"}),
    ("convert", ("Модар ва падари ман дар деҳа зиндагӣ мекунанд.", "tg"), {"to": "Arab"}),
    ("convert", ("همه افراد بشر آزاد به دنیا می‌آیند", "tg"), {"to": "Cyrl"}),
    ("convert", ("Barcha odamlar erkin, qadr-qimmat va huquqlarda teng boʻlib tugʻiladilar.", "uz"), {"to": "Cyrl"}),
    ("convert", ("Шеър, ЎЗБЕКИСТОН, Ёшлик, ЮНЕСКО, Ценз, Қуёш", "uz"), {"to": "Latn"}),
    ("convert", ("ҲАМАИ ОДАМОН ҶАҲОН", "tg"), {"to": "Latn"}),
]


def main():
    vectors = []
    builtin = {id(language) for language in nutq.languages()}

    def is_builtin(lang):
        try:
            return id(nutq.get_language(lang)) in builtin
        except Exception:
            return not str(lang).startswith("x-")  # unknown codes are useful error vectors

    originals = {name: getattr(nutq, name) for name in ("convert", "normalize", "number_to_words", "clean")}

    def recorder(name):
        def call(*args, **kwargs):
            lang = args[1] if len(args) > 1 else kwargs.get("lang")
            try:
                result = originals[name](*args, **kwargs)
            except Exception as exc:
                if is_builtin(lang):
                    vectors.append({"fn": name, "args": list(args), "kwargs": kwargs,
                                    "error": type(exc).__name__})
                raise
            if is_builtin(lang):
                vectors.append({"fn": name, "args": list(args), "kwargs": kwargs, "result": result})
            return result
        return call

    for name in originals:
        setattr(nutq, name, recorder(name))
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT / "tests"))
    outcome = unittest.TextTestRunner(stream=open("/dev/null", "w")).run(suite)
    if not outcome.wasSuccessful():
        sys.exit("tests failed; fix them before exporting vectors")
    for name, args, kwargs in EXTRA:
        getattr(nutq, name)(*args, **kwargs)
    for name, fn in originals.items():
        setattr(nutq, name, fn)

    unique = {json.dumps(v, ensure_ascii=False, sort_keys=True): v for v in vectors}
    out = ROOT / "js" / "test" / "vectors.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(list(unique.values()), ensure_ascii=False, indent=1) + "\n", "utf-8")
    print(f"wrote {len(unique)} vectors to {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
