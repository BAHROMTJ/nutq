# nutq

[![PyPI](https://img.shields.io/pypi/v/nutq)](https://pypi.org/project/nutq/) [![CI](https://github.com/BAHROMTJ/nutq/actions/workflows/ci.yml/badge.svg)](https://github.com/BAHROMTJ/nutq/actions/workflows/ci.yml)

**Script conversion and text normalization for Tajik, Persian, Dari and Uzbek** — in pure Python, with no dependencies.

*nutq* (нутқ · نطق · nutq) means "speech" in all three languages.

More than 150 million people speak these languages, and many of them write them in more than one script. Text-to-speech systems, chat bots, search engines and language models need the same text in a consistent form and the numbers spelled out, and there is little open tooling for that. `nutq` gives you one small, tested API for both jobs, and other languages can be added as plugins.

| | Tajik `tg` | Persian `fa` | Dari `fa-AF` | Uzbek `uz` |
|---|---|---|---|---|
| Scripts | Cyrillic · Latin · Perso-Arabic | Perso-Arabic | Perso-Arabic | Latin · Cyrillic |
| Script conversion | Cyrl ↔ Latn, Cyrl → Arab, Arab → Cyrl *(experimental)* | via `tg` | via `tg` | Cyrl ↔ Latn |
| Numbers → words | cardinal, ordinal | cardinal, ordinal | cardinal, ordinal | cardinal, ordinal |
| Normalization for speech | numbers, decimals, %, money, dates, times, phone and version numbers, °C, abbreviations | + Solar Hijri dates | + Afghan month names | Latin and Cyrillic |
| Character cleanup | look-alike letters | ي/ك → ی/ک, digits, ZWNJ | same as `fa` | apostrophes oʻ gʻ ʼ |

Status: **beta**. Each rule is tested, but native speakers still need to review many of them. See [Linguistic review](#linguistic-review).

## Install

```bash
pip install nutq
```

## Usage

```python
import nutq

# Script conversion
nutq.convert("Забони тоҷикӣ", "tg", to="Arab")      # 'زبان تاجیکی'
nutq.convert("Тоҷикистон", "tg", to="Latn")          # 'Tojikiston'
nutq.convert("Ўзбекистон", "uz", to="Latn")          # 'Oʻzbekiston'
nutq.convert("O'zbekiston", "uz", to="Cyrl")         # 'Ўзбекистон'

# Numbers to words
nutq.number_to_words(2026, "tg")                     # 'ду ҳазору бисту шаш'
nutq.number_to_words(2026, "fa")                     # 'دو هزار و بیست و شش'
nutq.number_to_words(3, "uz", ordinal=True)          # 'uchinchi'
nutq.number_to_words(4, "uz", script="Cyrl", ordinal=True)  # 'тўртинчи'

# Normalization for TTS and language models
nutq.normalize("Нархи 25 $ аст, 12.03.2026", "tg")
# 'Нархи бисту панҷ доллар аст, дувоздаҳуми марти соли ду ҳазору бисту шаш'
nutq.normalize("۱۴۰۵/۰۱/۱۲، ۱۵٪", "fa")
# 'دوازدهم فروردین هزار و چهارصد و پنج، پانزده درصد'
nutq.normalize("2026-yil 12-mart, 2,5 kg", "uz")
# 'ikki ming yigirma oltinchi yil oʻn ikkinchi mart, ikki butun oʻndan besh kilogramm'

# Character cleanup only
nutq.clean("Тoҷик", "tg")      # 'Тоҷик'  (the "o" was Latin)
nutq.clean("كتابي", "fa")       # 'کتابی'
```

Language codes follow BCP-47 / ISO 639 (`tg`, `fa`, `fa-AF`, `prs`, `uz`, ...). Scripts are ISO 15924 codes (`Cyrl`, `Latn`, `Arab`) or names (`"latin"`). If you don't pass `source=`, `convert` detects the source script.

### Command line

```bash
nutq convert --lang tg --to Arab "Забони тоҷикӣ"
nutq normalize --lang uz "Narxi 25 $, 15% chegirma"
nutq number --lang fa --ordinal 23
echo "O'zbekiston" | nutq convert -l uz -t Cyrl
nutq languages
```

## How Tajik → Perso-Arabic works

Tajik Cyrillic writes every vowel. Persian script leaves out short vowels and has several letters for one sound (с = س ص ث). A rule-only converter therefore cannot be exact. `nutq` works in three steps:

1. **Word list** — [`lang/tg/data/arabic_words.tsv`](src/nutq/lang/tg/data/arabic_words.tsv) holds the spellings rules can't guess (китоб → کتاب, илм → علم).
2. **Suffixes and stems** — plural -ҳо/-ён, object -ро → را, izafat -и, comparative -тар/-тарин, the linking -у → و, verb prefixes ме-/наме- → می‌/نمی‌, and stems like хонд → خواند, кун → کن.
3. **Letter rules** for everything else. They are correct for many common words (нон → نان, Самарқанд → سمرقند).

Arabic → Cyrillic is **experimental**. Without a dictionary, an unvowelled word can only be read approximately.

## Adding a language

Each language is one folder under `src/nutq/lang/`. It registers a `Language` object, and third-party packages can add languages through an entry point without changing `nutq`. See [CONTRIBUTING.md](CONTRIBUTING.md). Kazakh, Turkmen, Azerbaijani, Serbian and Kurdish are next on the [roadmap](ROADMAP.md), and we are looking for native speakers to help.

## Linguistic review

Some forms are our best guess and still need a native editor to confirm them. Each one is marked `verify` in the source:

- **Tajik:** decimals (`ду бутуну панҷ даҳум`) and the Perso-Arabic word list. Dates and times were confirmed by a native speaker.
- **Persian / Dari:** `ممیز` vs `اعشاریه`, `درصد` vs `فیصد`, Afghan spellings of Gregorian months, `یکم` vs `اول`.
- **Uzbek:** all forms. Open questions: `yuz` vs `bir yuz`, `ming` vs `bir ming`, time and date reading, and `ts` → `ц` in Latin → Cyrillic.

If you find a mistake, please [open an issue](https://github.com/BAHROMTJ/nutq/issues) with the correct form. Issues may be written in English, Tajik, Persian, Uzbek or Russian.

## Development

```bash
pip install -e .
python -m unittest discover -s tests
```

Python 3.9+ and no dependencies.

---

## Бо забони тоҷикӣ

**nutq** (нутқ) — китобхонаи кушода (open source) барои забонҳои тоҷикӣ, форсӣ, дарӣ ва ӯзбекӣ. Он ду кор мекунад:

1. **Табдили хат:** тоҷикии кириллӣ ↔ лотинӣ ↔ хати форсӣ (Perso-Arabic), ӯзбекии кириллӣ ↔ лотинӣ.
2. **Тайёр кардани матн барои нутқ (TTS) ва зеҳни сунъӣ:** рақамҳо, санаҳо, вақт, пул, фоиз ва ихтисораҳо бо калима навишта мешаванд. Масалан, «25 $» → «бисту панҷ доллар».

```python
import nutq
nutq.convert("Забони тоҷикӣ", "tg", to="Arab")   # 'زبان تاجیکی'
nutq.normalize("Соати 14:30, 15% тахфиф", "tg")
# 'Соати чордаҳу сӣ, понздаҳ фоиз тахфиф'
```

Ҳар кас метавонад онро бепул истифода барад ва дар рушди он саҳм гузорад. Агар хатое ёбед, масалан калимае, ки бо хати форсӣ нодуруст навишта шудааст, лутфан дар GitHub issue кушоед ё калимаро ба файли `arabic_words.tsv` илова кунед. Ба забондонҳои ӯзбек, қазоқ, туркман, озарӣ, серб ва курд барои илова кардани забонҳои нав ниёз дорем.

## License

MIT
