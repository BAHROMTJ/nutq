---
title: nutq — Tajik, Persian, Dari, Uzbek
emoji: 🗣️
colorFrom: green
colorTo: red
sdk: static
pinned: false
license: mit
short_description: Script conversion and TTS text normalization for tg/fa/uz
tags:
  - tajik
  - persian
  - dari
  - uzbek
  - transliteration
  - text-normalization
  - tts
---

# nutq web demo

Try [nutq](https://github.com/BAHROMTJ/nutq) in the browser. The page uses the JavaScript port, so everything runs locally in your browser and nothing is sent to a server.

- **Convert script**: Tajik Cyrillic ↔ Latin ↔ Perso-Arabic, Uzbek Latin ↔ Cyrillic
- **Normalize for speech**: numbers, dates (including Solar Hijri), times, money, percentages, phone numbers and abbreviations as words
- **Numbers**: cardinal and ordinal number words in any supported script

## Building and deploying

This folder is a static Hugging Face Space (the front matter above configures it).

```bash
./build.sh          # copies js/src into web/nutq/
python3 -m http.server -d web 8000   # try it at http://localhost:8000
hf upload <user>/nutq web . --repo-type space
```
