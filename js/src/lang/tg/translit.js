// Transliteration between Tajik Cyrillic and Latin script.
//
// The Latin scheme follows the common BGN/PCGN-style romanization of Tajik
// (ҷ -> j, қ -> q, ғ -> gh, х -> kh, ҳ -> h, ӣ -> ī, ӯ -> ū).

import { matchCase } from "../../core/case.js";
import { isUpperChar, length } from "../../core/text.js";

const CYR_TO_LAT = new Map(Object.entries({
  "а": "a", "б": "b", "в": "v", "г": "g", "ғ": "gh", "д": "d",
  "е": "e", "ё": "yo", "ж": "zh", "з": "z", "и": "i", "ӣ": "ī",
  "й": "y", "к": "k", "қ": "q", "л": "l", "м": "m", "н": "n",
  "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
  "ӯ": "ū", "ф": "f", "х": "kh", "ҳ": "h", "ч": "ch", "ҷ": "j",
  "ш": "sh", "ъ": "'", "э": "e", "ю": "yu", "я": "ya",
  // Russian letters that appear in loanwords
  "ц": "ts", "щ": "shch", "ы": "y", "ь": "",
}));

const ASCII_FOLD = new Map(Object.entries({ "ī": "i", "ū": "u", "Ī": "I", "Ū": "U" }));

// Longest sequences first so "shch" wins over "sh" and "kh" over "k".
const LAT_TO_CYR = [
  ["shch", "щ"], ["kh", "х"], ["gh", "ғ"], ["zh", "ж"], ["ch", "ч"],
  ["sh", "ш"], ["ts", "ц"], ["yo", "ё"], ["yu", "ю"], ["ya", "я"],
  ["a", "а"], ["b", "б"], ["v", "в"], ["g", "г"], ["d", "д"],
  ["e", "е"], ["z", "з"], ["i", "и"], ["ī", "ӣ"], ["y", "й"],
  ["k", "к"], ["q", "қ"], ["l", "л"], ["m", "м"], ["n", "н"],
  ["o", "о"], ["p", "п"], ["r", "р"], ["s", "с"], ["t", "т"],
  ["u", "у"], ["ū", "ӯ"], ["f", "ф"], ["h", "ҳ"], ["j", "ҷ"],
  ["'", "ъ"],
].map(([latin, cyrillic]) => [latin, cyrillic, length(latin)]);

/**
 * Transliterate Tajik Cyrillic text to Latin script.
 *     toLatin("Тоҷикистон")  // "Tojikiston"
 */
export function toLatin(text, { asciiOnly = false } = {}) {
  const chars = Array.from(text);
  let result = "";
  chars.forEach((char, i) => {
    const lower = char.toLowerCase();
    if (CYR_TO_LAT.has(lower)) {
      const nextChar = i + 1 < chars.length ? chars[i + 1] : "";
      result += matchCase(char, CYR_TO_LAT.get(lower), nextChar);
    } else {
      result += char;
    }
  });
  if (asciiOnly) {
    result = Array.from(result, (c) => (ASCII_FOLD.has(c) ? ASCII_FOLD.get(c) : c)).join("");
  }
  return result;
}

/**
 * Transliterate Latin-script Tajik back to Cyrillic.
 *
 * The conversion is greedy, so it is lossy for rare letter clusters
 * (for example "к" followed by "ҳ" comes back as "х").
 *     toCyrillic("Dushanbe")  // "Душанбе"
 */
export function toCyrillic(text) {
  const chars = Array.from(text);
  let out = "";
  let i = 0;
  while (i < chars.length) {
    let matched = false;
    for (const [latin, cyrillic, size] of LAT_TO_CYR) {
      const chunk = chars.slice(i, i + size);
      if (chunk.join("").toLowerCase() === latin) {
        out += isUpperChar(chunk[0]) ? cyrillic.toUpperCase() : cyrillic;
        i += size;
        matched = true;
        break;
      }
    }
    if (!matched) {
      out += chars[i];
      i += 1;
    }
  }
  return out;
}
