// Uzbek Cyrillic <-> Latin, following the 1995 official Latin alphabet.
//
// The Latin letters oʻ and gʻ use U+02BB (ʻ) and the tutuq belgisi (ъ) uses
// U+02BC (ʼ), as the official standard says. Text typed with ASCII ' or with
// ‘ ’ ` is accepted on input.

import { matchCase } from "../../core/case.js";
import { W, isAlpha, isUpperChar, length, sub } from "../../core/text.js";

export const OKINA = "ʻ"; // ʻ in oʻ, gʻ
export const TUTUQ = "ʼ"; // ʼ for ъ

const CYR_TO_LAT = new Map(Object.entries({
  "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "ё": "yo",
  "ж": "j", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
  "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
  "ф": "f", "х": "x", "ч": "ch", "ш": "sh", "ъ": TUTUQ, "ь": "",
  "э": "e", "ю": "yu", "я": "ya", "ў": "o" + OKINA, "қ": "q",
  "ғ": "g" + OKINA, "ҳ": "h",
}));
const CYR_VOWELS = new Set("аеёиоуэюяў");

const AFTER_O_G = /([oOgG])['‘’`ʻʼ]/gu;
const OTHER = new RegExp(`(?<=${W})['\\u2018\\u2019\`\\u02bc]`, "gu");

// Longest sequences first.
const LAT_TO_CYR = [
  ["s" + TUTUQ + "h", "сҳ"], // Isʼhoq: the apostrophe separates s and h
  ["o" + OKINA, "ў"], ["g" + OKINA, "ғ"],
  ["sh", "ш"], ["ch", "ч"], ["yo", "ё"], ["yu", "ю"], ["ya", "я"],
  ["ye", "е"], ["ts", "ц"],
  ["a", "а"], ["b", "б"], ["d", "д"], ["e", "е"], ["f", "ф"], ["g", "г"], ["h", "ҳ"],
  ["i", "и"], ["j", "ж"], ["k", "к"], ["l", "л"], ["m", "м"], ["n", "н"],
  ["o", "о"], ["p", "п"], ["q", "қ"], ["r", "р"], ["s", "с"], ["t", "т"],
  ["u", "у"], ["v", "в"], ["x", "х"], ["y", "й"], ["z", "з"],
  [TUTUQ, "ъ"],
].map(([latin, cyrillic]) => [latin, cyrillic, length(latin)]);
const LAT_VOWELS = new Set("aeiou");

/** Use ʻ after o/g and ʼ elsewhere inside words (o'zbek -> oʻzbek). */
export function fixApostrophes(text) {
  text = sub(AFTER_O_G, text, (m) => m[1] + OKINA);
  return text.replace(OTHER, TUTUQ);
}

/**
 * Transliterate Uzbek Cyrillic to Latin.
 *     toLatin("Ўзбекистон")  // "Oʻzbekiston"
 */
export function toLatin(text) {
  const chars = Array.from(text);
  let out = "";
  chars.forEach((char, i) => {
    const lower = char.toLowerCase();
    const prev = i ? chars[i - 1].toLowerCase() : "";
    const nextChar = i + 1 < chars.length ? chars[i + 1] : "";
    let latin;
    if (lower === "е") {
      // ye at the start of a word and after a vowel, ъ or ь
      const starts = !isAlpha(prev) || CYR_VOWELS.has(prev) || "ъь".includes(prev);
      latin = starts ? "ye" : "e";
    } else if (lower === "ц") {
      // ts after a vowel, s elsewhere (цирк -> sirk, милиция -> militsiya)
      latin = CYR_VOWELS.has(prev) ? "ts" : "s";
    } else if (CYR_TO_LAT.has(lower)) {
      latin = CYR_TO_LAT.get(lower);
    } else {
      out += char;
      return;
    }
    out += matchCase(char, latin, nextChar);
  });
  return out;
}

/**
 * Transliterate Uzbek Latin to Cyrillic.
 *
 * "s" + "ts" is ambiguous in Latin; "ts" always becomes ц.
 *     toCyrillic("Oʻzbekiston")  // "Ўзбекистон"
 */
export function toCyrillic(text) {
  const chars = Array.from(fixApostrophes(text));
  let out = "";
  let i = 0;
  while (i < chars.length) {
    const prev = i ? chars[i - 1].toLowerCase() : "";
    let matched = false;
    for (const [latin, cyr, size] of LAT_TO_CYR) {
      const chunk = chars.slice(i, i + size);
      if (chunk.join("").toLowerCase() !== latin) continue;
      if (latin === "yo" && chars[i + 2] === OKINA) continue; // yoʻl is y + oʻ, not yo + ʻ
      let cyrillic = cyr;
      if (latin === "e" && (!isAlpha(prev) || LAT_VOWELS.has(prev))) {
        cyrillic = "э"; // word-initial e (ekran -> экран)
      }
      out += isUpperChar(chunk[0]) ? cyrillic.toUpperCase() : cyrillic;
      i += size;
      matched = true;
      break;
    }
    if (!matched) {
      out += chars[i];
      i += 1;
    }
  }
  return out;
}
