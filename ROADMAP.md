# Roadmap

The goal: become the standard open tool for script conversion and speech-ready text in the languages of Central Asia, Iran, Afghanistan and the Balkans — languages that have several scripts but few open NLP tools.

## 0.1 — first release (this repository)

- [x] Tajik: Cyrillic ↔ Latin, Cyrillic → Perso-Arabic, Perso-Arabic → Cyrillic (experimental)
- [x] Persian and Dari: numbers, normalization (incl. Solar Hijri dates), character cleanup
- [x] Uzbek: Cyrillic ↔ Latin (1995 standard), numbers, normalization in both scripts
- [x] Plugin registry with entry points; CLI; 73 tests; Python 3.9+
- [x] Tajik dates and times confirmed by a native speaker
- [ ] Native-speaker review of the remaining forms marked `verify` (Tajik/Persian: Bahrom; Uzbek: needs a reviewer)
- [ ] Publish to GitHub and PyPI (needs the maintainer's OK)
- [ ] `tojiki` 0.2 becomes a thin wrapper over `nutq` so its existing users get the new features

## 0.2 — quality

- [ ] Grow the Tajik → Perso-Arabic word list to the ~2,000 most frequent words (from a frequency list; reviewed)
- [ ] Measure accuracy on a parallel Tajik/Persian test set and publish the number
- [ ] Number words → digits (the reverse of `number_to_words`) for ASR output
- [ ] Fractions (½, 3/4), more units (км/соат, м²), local phone numbers without "+"
- [ ] Restore Tajik letters typed on a Russian keyboard (х → ҳ, к → қ) using the word list

## 0.3 — more languages (each needs a native-speaker co-maintainer)

- [ ] Kazakh: Cyrillic ↔ Latin (2021 alphabet), numbers
- [ ] Turkmen and Azerbaijani: Cyrillic ↔ Latin, numbers
- [ ] Serbian: Cyrillic ↔ Latin (simple and well defined; a good first plugin)
- [ ] Kurdish: Sorani (Arabic script) ↔ Kurmanji (Latin) letters
- [ ] Uzbek: the 2023 Latin alphabet update, once it is final

## Beyond Python

- [ ] **JavaScript / npm port** (`nutq` is free on npm): same API and the same TSV data files. Generate shared test cases from the Python suite as JSON so both implementations pass the same tests. It enables browser keyboards, websites and Node bots.
- [ ] **Hugging Face Space**: a Gradio demo with text in, script and language picker, converted and normalized text out, plus an "is this wrong? suggest a fix" button that collects corrections from native speakers.
- [ ] **MCP server** (`nutq-mcp`): exposes `convert`, `normalize` and `number_to_words` as tools so AI assistants can work correctly with these scripts.
- [ ] Integrations: a text-normalization front end for open TTS models (Piper, Coqui, MMS) for Tajik and Uzbek; a spaCy / Hugging Face `tokenizers` pre-normalizer.

## Growing the community

- Label `good first issue` for word-list additions and new test cases.
- Announce through the Tajik AI course, plus Persian and Uzbek developer communities, Masakhane-style low-resource NLP groups and Hugging Face.
- Credit every native-speaker reviewer in the README.
