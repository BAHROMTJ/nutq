# nutq (JavaScript)

Script conversion and speech-oriented text normalization for **Tajik**
(Cyrillic, Latin, Perso-Arabic), **Persian**, **Dari** and **Uzbek** (Latin,
Cyrillic).

This is the JavaScript port of the Python package
[`nutq`](https://pypi.org/project/nutq/). The Python package is the reference
implementation: both run the same test vectors and give byte-for-byte
identical output.

- Zero dependencies, ESM only, TypeScript types included
- Node.js 18+ and modern browsers (no `fs` or other Node APIs at runtime)

## Install

```sh
npm install @bahrom99/nutq
```

## Usage

```js
import { convert, normalize, clean, numberToWords } from "@bahrom99/nutq";
```

### Tajik (`tg`)

```js
convert("Тоҷикистон", "tg", { to: "Latn" });        // "Tojikiston"
convert("Забони тоҷикӣ", "tg", { to: "Arab" });     // "زبان تاجیکی"
convert("کتاب‌ها", "tg", { to: "Cyrl" });           // "китобҳо" (Arabic -> Cyrillic is experimental)

normalize("Вохӯрӣ 01.09.2026 соати 08:00 аст.", "tg");
// "Вохӯрӣ якуми сентябри соли ду ҳазору бисту шаш соати ҳашт аст."
normalize("Нарх: 3,75 смн", "tg");                  // "Нарх: се сомониву ҳафтоду панҷ дирам"
clean("Тoҷик", "tg");                               // "Тоҷик" (Latin "o" replaced)

numberToWords(2026, "tg");                          // "ду ҳазору бисту шаш"
numberToWords(3, "tg", { ordinal: true });          // "сеюм"
numberToWords(2026, "tg", { script: "Latn" });      // "du hazoru bistu shash"
```

### Persian (`fa`) and Dari (`fa-AF`, alias `prs`)

```js
normalize("در سال ۱۳۹۹ حدود ۸۵٬۰۰۰٬۰۰۰ نفر", "fa");
// "در سال هزار و سیصد و نود و نه حدود هشتاد و پنج میلیون نفر"
normalize("۱۵٪", "fa");                             // "پانزده درصد"
normalize("۱۵٪", "fa-AF");                          // "پانزده فیصد"
normalize("کابل ۱۴۰۳/۰۵/۲۸", "prs");                // "کابل بیست و هشتم اسد هزار و چهارصد و سه"
clean("كتابي", "fa");                               // "کتابی" (Arabic ي/ك -> Persian ی/ک)
numberToWords(23, "fa", { ordinal: true });         // "بیست و سوم"
```

### Uzbek (`uz`)

```js
convert("Ўзбекистон", "uz", { to: "Latn" });        // "Oʻzbekiston"
convert("Oʻzbekiston", "uz", { to: "cyrillic" });   // "Ўзбекистон"
clean("o'zbek", "uz");                              // "oʻzbek" (U+02BB okina)

normalize("Narxi 1 250 000 so'm, 3-sentabr, soat 18:00 da", "uz");
// "Narxi bir million ikki yuz ellik ming soʻm, uchinchi sentabr, soat oʻn sakkiz da"
normalize("15%", "uz");                             // "oʻn besh foiz"
numberToWords(2026, "uz", { script: "Cyrl" });      // "икки минг йигирма олти"
```

## API

| Function | Description |
| --- | --- |
| `convert(text, lang, { to, source? })` | Convert between scripts. `source` is detected when omitted. Scripts are ISO 15924 codes (`Cyrl`, `Latn`, `Arab`) or names (`latin`, `cyrillic`, `arabic`). |
| `normalize(text, lang)` | Numbers, dates, times, money, percentages, units and abbreviations to words (for TTS and language models). Also applies `clean`. |
| `clean(text, lang)` | Fix characters only: look-alike letters, apostrophes, digit forms, ZWNJ. |
| `numberToWords(n, lang, { ordinal?, script? })` | Spell out an integer (a Number or a BigInt, below 10**18). |
| `languages()` | All registered languages, sorted by code. |
| `getLanguage(code)` | Look up a language by code or alias (`prs` -> `fa-AF`, `tgk` -> `tg`; case-insensitive, `_` = `-`). |
| `register(language)` | Add or replace a language (a plain object with the same fields as `Language`). |
| `detectScript(text, candidates?)` | The script most letters are written in, or `null`. |

Errors:

- `UnsupportedError` (extends `RangeError`): unknown language, a script the
  language is not written in, or a conversion that is not available.
- `TypeError`: `numberToWords` with a non-integer (or a boolean).
- `RangeError`: an ordinal of a number below 1, a number of 10**18 or more,
  an unknown script name.

### Custom languages

```js
import { register, normalize } from "@bahrom99/nutq";

register({
  code: "x-demo",
  name: "Demo",
  nativeName: "demo",
  defaultScript: "Latn",
  scripts: ["Latn"],
  cardinal: String,
  ordinal: (n) => `${n}th`,
  normalize: (text) => text.toUpperCase(),
  clean: (text) => text.trim(),
  converters: {},          // { "Cyrl->Latn": fn, ... }
});
normalize("abc", "x-demo"); // "ABC"
```

## Command line

```sh
npx @bahrom99/nutq convert --lang tg --to Latn "Душанбе"     # Dushanbe
echo "Душанбе" | npx @bahrom99/nutq convert -l tg -t Arab    # دوشنبه
npx @bahrom99/nutq normalize -l fa "۱۵٪"                     # پانزده درصد
npx @bahrom99/nutq clean -l tg "Тoҷик"                       # Тоҷик
npx @bahrom99/nutq number -l uz --ordinal 2                  # ikkinchi
npx @bahrom99/nutq number -l tg --script Arab 21             # بیست و یک
npx @bahrom99/nutq languages
```

Text is read from standard input when no text arguments are given.

## More

Linguistic notes, the status of each conversion, the roadmap and how to
contribute (especially as a native speaker) are in the
[main README](https://github.com/BAHROMTJ/nutq#readme).

The Tajik Perso-Arabic word list lives in the Python package
(`src/nutq/lang/tg/data/arabic_words.tsv`); `npm run build:data` regenerates
`src/lang/tg/arabic-words.js` from it. `npm test` runs the shared test vectors
(`test/vectors.json`, exported by `scripts/export_vectors.py`).

## License

MIT © Bahrom Sharifzoda
