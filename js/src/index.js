// nutq: script conversion and text normalization for Tajik, Persian, Dari
// and Uzbek.
//
//     import { convert, normalize } from "nutq";
//     convert("Тоҷикистон", "tg", { to: "Arab" });  // "تاجیکستان"
//     normalize("15%", "uz");                        // "oʻn besh foiz"

import { getLanguage, resolveScript } from "./registry.js";
import { detectScript } from "./scripts.js";

export { Language, UnsupportedError, getLanguage, languages, register } from "./registry.js";
export { canonicalScript, detectScript } from "./scripts.js";

export const version = "0.1.0";

function checkText(text, name) {
  if (typeof text !== "string") throw new TypeError(`${name}() expects text as a string`);
}

/**
 * Convert `text` in language `lang` to the script `to`.
 *
 * `source` is detected from the text when omitted. Scripts are ISO 15924
 * codes (`Cyrl`, `Latn`, `Arab`) or names (`latin`).
 *
 *     convert("Ўзбекистон", "uz", { to: "Latn" })  // "Oʻzbekiston"
 */
export function convert(text, lang, { to, source } = {}) {
  checkText(text, "convert");
  const language = getLanguage(lang);
  if (to === undefined || to === null) throw new TypeError("convert() requires the `to` option");
  const target = resolveScript(language, to);
  const from = resolveScript(language, source) || detectScript(text, language.scripts);
  if (from === null || from === target) return text;
  return language.converter(from, target)(text);
}

/**
 * Spell out the integer `n` (`ordinal: true` for 1st, 2nd, ...).
 *
 *     numberToWords(2026, "tg")  // "ду ҳазору бисту шаш"
 */
export function numberToWords(n, lang, { ordinal = false, script } = {}) {
  const language = getLanguage(lang);
  let words = ordinal ? language.ordinal(n) : language.cardinal(n);
  const target = resolveScript(language, script);
  if (target && target !== language.defaultScript) {
    words = language.converter(language.defaultScript, target)(words);
  }
  return words;
}

/**
 * Rewrite numbers, dates, times, money and abbreviations as words.
 *
 * Use this before text-to-speech or to give language models a consistent
 * input. It also applies `clean`.
 */
export function normalize(text, lang) {
  checkText(text, "normalize");
  return getLanguage(lang).normalize(text);
}

/** Fix characters only: look-alike letters, apostrophes, digit forms. */
export function clean(text, lang) {
  checkText(text, "clean");
  return getLanguage(lang).clean(text);
}
