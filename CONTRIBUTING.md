# Contributing to nutq

Thank you for helping! **Native speakers are the most valuable contributors here.** Many fixes need language knowledge more than code, so a one-line issue saying "this word is spelled wrong, the correct form is X" is a real contribution.

Issues may be written in English, Tajik, Persian, Uzbek or Russian.

## Ways to help

| You are... | You can... |
|---|---|
| a native speaker | review the forms marked `verify`, report wrong words, add words to `src/nutq/lang/tg/data/arabic_words.tsv` |
| a developer | fix bugs, add tests, port to JavaScript |
| a speaker of a language we don't support yet | add it (see below) or open an issue saying you can review one |

## Development setup

```bash
git clone https://github.com/BAHROMTJ/nutq
cd nutq
pip install -e .
python -m unittest discover -s tests
```

`nutq` has no dependencies and supports Python 3.9+. Every change needs a test.

## Adding a word to the Tajik → Perso-Arabic list

1. Check the current output: `nutq convert -l tg --to Arab "калима"`.
2. Add a word **only if the output is wrong**. Format: Cyrillic, a TAB, then Arabic.
3. Add the word to `test_word_list` in `tests/test_tg.py`, or to a new test.

## Adding a language

A language is one folder under `src/nutq/lang/<code>/`, named with an ISO 639-1 code where one exists. Copy the closest existing language. Uzbek is a good template for Turkic languages with Latin and Cyrillic.

```
src/nutq/lang/kk/
  __init__.py     # builds and registers the Language object
  numbers.py      # to_words(n), to_ordinal(n)
  translit.py     # script converters, if the language has several scripts
  verbalize.py    # a core.verbalize.Verbalizer: dates, money, abbreviations
tests/test_kk.py
```

1. **Numbers** (`numbers.py`): implement `to_words(n: int) -> str` and `to_ordinal(n: int) -> str`. Raise `TypeError` for non-integers and `ValueError` for numbers that are out of range.
2. **Scripts** (`translit.py`): one function per direction, `str -> str`. Document the standard you follow (for example "the 2021 Kazakh Latin alphabet").
3. **Normalization** (`verbalize.py`): create a `Verbalizer` from `nutq.core.verbalize`. You only describe how to *say* things: `cardinal`, `ordinal`, `decimal`, `percent`, `money`, `date`, `time`, the minus word, currency symbols and abbreviations. The core finds them in the text. Put patterns specific to your language (like the Uzbek `12-mart`) in `rules`.
4. **Register** it in `__init__.py`:

   ```python
   from ...registry import Language, register

   LANGUAGE = register(Language(
       code="kk", name="Kazakh", native_name="қазақша",
       default_script="Cyrl", scripts=("Cyrl", "Latn"),
       cardinal=to_words, ordinal=to_ordinal,
       normalize=lambda text: verbalize(clean(text)), clean=clean,
       converters={("Cyrl", "Latn"): to_latin, ("Latn", "Cyrl"): to_cyrillic},
       aliases=("kaz",), status="experimental",
   ))
   ```

5. Import the new module in `src/nutq/lang/__init__.py`.
6. **Tests**: cover numbers, every script direction, round trips and normalization. Mark every form you are not sure of with a `# verify` comment and list it in the PR description.
7. Add the language to the table in `README.md`.

New languages start as `status="experimental"`. A language becomes `beta` after one native speaker has reviewed it, and `stable` after two.

### Languages as separate packages

A language can also live in its own package, for example a dialect or a research model that shouldn't ship with the core. Expose a `Language` object (or a module that calls `register`) under the `nutq.languages` entry point:

```toml
[project.entry-points."nutq.languages"]
kk = "nutq_kazakh:LANGUAGE"
```

## Pull requests

- Keep each PR to one language or one topic.
- Explain linguistic decisions and cite a source where possible (an orthography standard, a dictionary or a style guide).
- Don't change another language's forms without a native speaker's confirmation.
