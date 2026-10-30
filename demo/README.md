---
title: nutq — Tajik, Persian, Dari, Uzbek
emoji: 🗣️
colorFrom: green
colorTo: red
sdk: gradio
sdk_version: 6.31.0
app_file: app.py
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

# nutq demo

Try [nutq](https://github.com/BAHROMTJ/nutq) in the browser:

- **Convert script**: Tajik Cyrillic ↔ Latin ↔ Perso-Arabic, Uzbek Latin ↔ Cyrillic
- **Normalize for speech**: numbers, dates (including Solar Hijri), times, money, percentages, phone numbers and abbreviations as words, in Tajik, Persian, Dari and Uzbek
- **Numbers**: cardinal and ordinal number words in any supported script

```bash
pip install nutq
```

## Deploying this Space

This folder is the whole Space: `app.py`, `requirements.txt` and this README (its front matter configures the Space). To publish it, create a Gradio Space on Hugging Face and push these three files to it. When a new `nutq` version is released, bump the version in `requirements.txt`.
