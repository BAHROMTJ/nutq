// Fix Latin letters hidden inside Cyrillic words (Тoҷик -> Тоҷик).

import { makeTranslator, sub, W } from "./text.js";

const LATIN_IN_CYRILLIC = makeTranslator({
  a: "а", c: "с", e: "е", o: "о", p: "р", x: "х", y: "у",
  A: "А", B: "В", C: "С", E: "Е", H: "Н", K: "К", M: "М",
  O: "О", P: "Р", T: "Т", X: "Х", Y: "У",
});

const WORD = new RegExp(`${W}+`, "gu");
const CYRILLIC = /[Ѐ-ԯ]/u;

/**
 * Replace Latin look-alikes inside words that contain Cyrillic letters.
 * Words written fully in Latin script are left untouched.
 */
export function fixLatinInCyrillic(text) {
  return sub(WORD, text, (m) => (CYRILLIC.test(m[0]) ? LATIN_IN_CYRILLIC(m[0]) : m[0]));
}
