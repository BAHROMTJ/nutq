"""Hugging Face Space: try nutq in the browser.

Run locally:  pip install -r requirements.txt && python app.py
"""

import gradio as gr
import nutq

ISSUES = "https://github.com/BAHROMTJ/nutq/issues/new"

LANGUAGES = {
    "Тоҷикӣ · Tajik (tg)": "tg",
    "فارسی · Persian (fa)": "fa",
    "دری · Dari (fa-AF)": "fa-AF",
    "Oʻzbekcha · Uzbek (uz)": "uz",
}
CONVERT_LANGUAGES = {k: v for k, v in LANGUAGES.items() if v in ("tg", "uz")}
SCRIPTS = {
    "Cyrillic · Кириллӣ": "Cyrl",
    "Latin · Лотинӣ": "Latn",
    "Perso-Arabic · خط فارسی": "Arab",
}


def _run(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except (ValueError, TypeError) as exc:
        raise gr.Error(str(exc))


def _shown(text):
    """Show Perso-Arabic results right-to-left."""
    return gr.update(value=text, rtl=nutq.detect_script(text) == "Arab")


def convert(text, language, script):
    return _shown(_run(nutq.convert, text, CONVERT_LANGUAGES[language], to=SCRIPTS[script]))


def normalize(text, language):
    return _shown(_run(nutq.normalize, text, LANGUAGES[language]))


def number(value, language, ordinal, script):
    if value is None:
        return ""
    lang = LANGUAGES[language]
    target = SCRIPTS[script] if script else None
    if target and target not in nutq.get_language(lang).scripts:
        target = None  # e.g. Persian is written only in Arabic script
    return _run(nutq.number_to_words, int(value), lang, ordinal=ordinal, script=target)


with gr.Blocks(title="nutq — Tajik, Persian, Dari, Uzbek") as demo:
    gr.Markdown(
        "# nutq · нутқ · نطق\n"
        "Script conversion and speech-ready text for **Tajik, Persian, Dari and Uzbek**. "
        "Open source: [GitHub](https://github.com/BAHROMTJ/nutq) · `pip install nutq`\n\n"
        "Табдили хат ва тайёр кардани матн барои нутқ (TTS) ва зеҳни сунъӣ."
    )

    with gr.Tab("Convert script · Табдили хат"):
        with gr.Row():
            conv_lang = gr.Dropdown(list(CONVERT_LANGUAGES), value="Тоҷикӣ · Tajik (tg)", label="Language")
            conv_script = gr.Dropdown(list(SCRIPTS), value="Perso-Arabic · خط فارسی", label="Convert to")
        conv_in = gr.Textbox(label="Text", lines=4, value="Забони тоҷикӣ ширинтар аз шакар.")
        conv_out = gr.Textbox(label="Result", lines=4, buttons=["copy"])
        gr.Button("Convert", variant="primary").click(convert, [conv_in, conv_lang, conv_script], conv_out)
        gr.Examples(
            [
                ["Тоҷикистон дар Осиёи Марказӣ ҷойгир аст.", "Тоҷикӣ · Tajik (tg)", "Perso-Arabic · خط فارسی"],
                ["Абӯабдуллоҳи Рӯдакӣ", "Тоҷикӣ · Tajik (tg)", "Latin · Лотинӣ"],
                ["O'zbekiston, yo'l, ma'no", "Oʻzbekcha · Uzbek (uz)", "Cyrillic · Кириллӣ"],
                ["Ўзбекистон Республикаси", "Oʻzbekcha · Uzbek (uz)", "Latin · Лотинӣ"],
            ],
            [conv_in, conv_lang, conv_script],
        )
        gr.Markdown(
            "Perso-Arabic → Tajik Cyrillic is experimental: Persian does not write short vowels."
        )

    with gr.Tab("Normalize for speech · Барои нутқ"):
        norm_lang = gr.Dropdown(list(LANGUAGES), value="Тоҷикӣ · Tajik (tg)", label="Language")
        norm_in = gr.Textbox(label="Text", lines=4, value="Нархи 25 $ аст, 12.03.2026, соати 14:30, 15% тахфиф.")
        norm_out = gr.Textbox(label="Result", lines=4, buttons=["copy"])
        gr.Button("Normalize", variant="primary").click(normalize, [norm_in, norm_lang], norm_out)
        gr.Examples(
            [
                ["Телефон: +992 93 123 45 67, ҳарорат -5°C", "Тоҷикӣ · Tajik (tg)"],
                ["۱۴۰۵/۰۱/۱۲، قیمت ۲۵ دلار، ۱۵٪ تخفیف", "فارسی · Persian (fa)"],
                ["۱۴۰۳/۰۵/۲۸، ۱۰۰۰ ؋، ۲٫۵٪", "دری · Dari (fa-AF)"],
                ["2026-yil 12-mart, narxi 12 500 so'm", "Oʻzbekcha · Uzbek (uz)"],
                ["1991 йил 31 августда", "Oʻzbekcha · Uzbek (uz)"],
            ],
            [norm_in, norm_lang],
        )

    with gr.Tab("Numbers · Рақамҳо"):
        with gr.Row():
            num_in = gr.Number(label="Number", value=2026, precision=0)
            num_lang = gr.Dropdown(list(LANGUAGES), value="Тоҷикӣ · Tajik (tg)", label="Language")
            num_script = gr.Dropdown([""] + list(SCRIPTS), value="", label="Script (optional)")
            num_ord = gr.Checkbox(label="Ordinal (1st, 2nd…)")
        num_out = gr.Textbox(label="In words", buttons=["copy"])
        gr.Button("Spell out", variant="primary").click(number, [num_in, num_lang, num_ord, num_script], num_out)

    gr.Markdown(
        f"Found a wrong word or form? Please [open an issue]({ISSUES}) with the correct version — "
        "native speakers' corrections make this better for everyone. "
        "Хато ёфтед? Шакли дурустро дар GitHub нависед."
    )

if __name__ == "__main__":
    demo.launch()
