// Clean up Persian/Dari text: Arabic letter forms, digits, ZWNJ, tatweel.
//
// Text copied from Arabic keyboards or old websites mixes Arabic letters that
// look the same as Persian ones (ي/ی, ك/ک). Search and models treat them as
// different words, so they are unified here.

import { NW, makeTranslator, sub } from "../../core/text.js";

const ZWNJ = "‌";

const LETTERS = makeTranslator({
  "ي": "ی", "ى": "ی",
  "ك": "ک",
  "ە": "ه",
  "٠": "۰", "١": "۱", "٢": "۲", "٣": "۳", "٤": "۴",
  "٥": "۵", "٦": "۶", "٧": "۷", "٨": "۸", "٩": "۹",
});
const TATWEEL = "ـ";
const PRESENTATION_FORMS = /[ﭐ-﷿ﹰ-﻿]/gu;
const ZWNJ_RUNS = /‌{2,}/gu;
// Python: ‌(?=[\s\W]|$)|(?<=[\s\W])‌|^‌  ([\s\W] is the same as \W)
const ZWNJ_EDGES = new RegExp(`\\u200c(?=${NW}|$)|(?<=${NW})\\u200c|^\\u200c`, "gu");

/**
 * Return `text` with Persian letter forms, digits and ZWNJ unified.
 *     clean("كتابي")  // "کتابی"
 */
export function clean(text) {
  text = sub(PRESENTATION_FORMS, text, (m) => m[0].normalize("NFKC"));
  text = LETTERS(text.normalize("NFC"));
  text = text.replaceAll(TATWEEL, "");
  text = text.replace(ZWNJ_RUNS, ZWNJ);
  return text.replace(ZWNJ_EDGES, "");
}
