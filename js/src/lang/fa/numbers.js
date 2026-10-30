// Convert integers to Persian words (cardinal and ordinal).

import { checkInt, thousands } from "../../core/integer.js";

const ONES = ["", "یک", "دو", "سه", "چهار", "پنج", "شش", "هفت", "هشت", "نه"];
const TEENS = [
  "ده", "یازده", "دوازده", "سیزده", "چهارده",
  "پانزده", "شانزده", "هفده", "هجده", "نوزده",
];
const TENS = ["", "", "بیست", "سی", "چهل", "پنجاه", "شصت", "هفتاد", "هشتاد", "نود"];
const HUNDREDS = [
  "", "صد", "دویست", "سیصد", "چهارصد",
  "پانصد", "ششصد", "هفتصد", "هشتصد", "نهصد",
];
const SCALES = ["", "هزار", "میلیون", "میلیارد", "تریلیون", "کوادریلیون"];

const ZWNJ = "‌";
const AND = " و ";

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
 * Return the Persian cardinal number for `n`.
 *     toWords(2026)  // "دو هزار و بیست و شش"
 */
export function toWords(n) {
  checkInt(n, "toWords");
  if (n == 0) return "صفر"; // eslint-disable-line eqeqeq
  if (n < 0) return "منفی " + toWords(-n);
  const groups = [];
  thousands(n).forEach((group, scale) => {
    if (!group) return;
    if (scale >= SCALES.length) throw new RangeError("number is too large");
    let text;
    if (scale === 1 && group === 1) {
      text = SCALES[1]; // "هزار", not "یک هزار"
    } else {
      text = underThousand(group).join(AND);
      if (SCALES[scale]) text += " " + SCALES[scale];
    }
    groups.push(text);
  });
  return groups.reverse().join(AND);
}

/**
 * Return the Persian ordinal number for `n` (1 -> یکم, 3 -> سوم).
 *     toOrdinal(23)  // "بیست و سوم"
 */
export function toOrdinal(n) {
  checkInt(n, "toOrdinal");
  if (n < 1) throw new RangeError("ordinals are defined for positive numbers");
  const words = toWords(n);
  if (words.endsWith("سه")) return words.slice(0, -2) + "سوم";
  if (words.endsWith("ی")) return words + ZWNJ + "ام"; // سی -> سی‌ام
  return words + "م";
}
