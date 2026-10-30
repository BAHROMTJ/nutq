// Convert integers to Tajik words (cardinal and ordinal).

import { checkInt, thousands } from "../../core/integer.js";

export const ONES = ["", "як", "ду", "се", "чор", "панҷ", "шаш", "ҳафт", "ҳашт", "нӯҳ"];
export const TEENS = [
  "даҳ", "ёздаҳ", "дувоздаҳ", "сенздаҳ", "чордаҳ",
  "понздаҳ", "шонздаҳ", "ҳабдаҳ", "ҳаждаҳ", "нуздаҳ",
];
export const TENS = ["", "", "бист", "сӣ", "чил", "панҷоҳ", "шаст", "ҳафтод", "ҳаштод", "навад"];
export const HUNDREDS = [
  "", "сад", "дусад", "сесад", "чорсад",
  "панҷсад", "шашсад", "ҳафтсад", "ҳаштсад", "нӯҳсад",
];
export const SCALES = ["", "ҳазор", "миллион", "миллиард", "триллион", "квадриллион"];

export const VOWELS = new Set("аеёиӣоуӯэюя");

function lastChar(word) {
  const chars = Array.from(word);
  return chars.length ? chars[chars.length - 1] : "";
}

/**
 * Attach the linking conjunction "у" (and) to the end of a word.
 * бист -> бисту, сӣ -> сиву, ду -> дую
 */
export function withConjunction(word) {
  if (word.endsWith("ӣ")) return word.slice(0, -1) + "иву";
  if (VOWELS.has(lastChar(word))) return word + "ю";
  return word + "у";
}

function join(parts) {
  let result = parts[0];
  for (const part of parts.slice(1)) result = withConjunction(result) + " " + part;
  return result;
}

function underThousand(n) {
  const parts = [];
  const hundreds = Math.floor(n / 100);
  const rest = n % 100;
  if (hundreds) parts.push(HUNDREDS[hundreds]);
  if (rest >= 10 && rest < 20) {
    parts.push(TEENS[rest - 10]);
  } else {
    const tens = Math.floor(rest / 10);
    const ones = rest % 10;
    if (tens) parts.push(TENS[tens]);
    if (ones) parts.push(ONES[ones]);
  }
  return parts;
}

/**
 * Return the Tajik cardinal number for `n`.
 *     toWords(2026)  // "ду ҳазору бисту шаш"
 */
export function toWords(n) {
  checkInt(n, "toWords");
  if (n == 0) return "сифр"; // eslint-disable-line eqeqeq
  if (n < 0) return "минус " + toWords(-n);
  const groups = [];
  thousands(n).forEach((group, scale) => {
    if (!group) return;
    if (scale >= SCALES.length) throw new RangeError("number is too large");
    let text = join(underThousand(group));
    if (SCALES[scale]) text += " " + SCALES[scale];
    groups.push(text);
  });
  return join(groups.reverse());
}

/**
 * Return the Tajik ordinal number for `n` (1 -> якум, 2 -> дуюм).
 *     toOrdinal(3)  // "сеюм"
 */
export function toOrdinal(n) {
  checkInt(n, "toOrdinal");
  if (n < 1) throw new RangeError("ordinals are defined for positive numbers");
  const words = toWords(n);
  if (words.endsWith("ӣ")) return words.slice(0, -1) + "июм";
  if (VOWELS.has(lastChar(words))) return words + "юм";
  return words + "ум";
}
