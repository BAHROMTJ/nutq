// Convert integers to Uzbek words (Latin script).
//
// Spoken forms are used: 100 is "yuz" and 1000 is "ming", not "bir yuz" /
// "bir ming" as in some legal documents (verify with a native editor).

import { checkInt, thousands } from "../../core/integer.js";

const ONES = ["", "bir", "ikki", "uch", "toʻrt", "besh", "olti", "yetti", "sakkiz", "toʻqqiz"];
const TENS = ["", "oʻn", "yigirma", "oʻttiz", "qirq", "ellik", "oltmish", "yetmish", "sakson", "toʻqson"];
const SCALES = ["", "ming", "million", "milliard", "trillion", "kvadrillion"];

const VOWELS = new Set("aeiou");

function underThousand(n) {
  const parts = [];
  const hundreds = Math.floor(n / 100);
  const rest = n % 100;
  if (hundreds) {
    if (hundreds > 1) parts.push(ONES[hundreds]);
    parts.push("yuz");
  }
  const tens = Math.floor(rest / 10);
  const ones = rest % 10;
  if (tens) parts.push(TENS[tens]);
  if (ones) parts.push(ONES[ones]);
  return parts;
}

/**
 * Return the Uzbek cardinal number for `n`.
 *     toWords(2026)  // "ikki ming yigirma olti"
 */
export function toWords(n) {
  checkInt(n, "toWords");
  if (n == 0) return "nol"; // eslint-disable-line eqeqeq
  if (n < 0) return "minus " + toWords(-n);
  const groups = [];
  thousands(n).forEach((group, scale) => {
    if (!group) return;
    if (scale >= SCALES.length) throw new RangeError("number is too large");
    const parts = scale === 1 && group === 1 ? [] : underThousand(group);
    if (SCALES[scale]) parts.push(SCALES[scale]);
    groups.push(parts.join(" "));
  });
  return groups.reverse().join(" ");
}

/**
 * Return the Uzbek ordinal number for `n` (1 -> birinchi).
 *     toOrdinal(2)  // "ikkinchi"
 */
export function toOrdinal(n) {
  checkInt(n, "toOrdinal");
  if (n < 1) throw new RangeError("ordinals are defined for positive numbers");
  const words = toWords(n);
  return words + (VOWELS.has(words.slice(-1)) ? "nchi" : "inchi");
}
