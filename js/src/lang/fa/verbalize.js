// Persian (Iran) and Dari (Afghanistan) text normalization for speech.
//
// The two standards share number words but differ in month names, some
// currency words and the words for "percent" and the decimal point. Forms
// marked "verify" need confirmation from a native editor.

import { makeVerbalizer } from "../../core/verbalize.js";
import { D, S, W, toInt } from "../../core/text.js";
import { toOrdinal, toWords } from "./numbers.js";

export const GREGORIAN_MONTHS = {
  fa: ["", "ژانویه", "فوریه", "مارس", "آوریل", "مه", "ژوئن",
    "ژوئیه", "اوت", "سپتامبر", "اکتبر", "نوامبر", "دسامبر"],
  // verify: Afghan media spelling of Gregorian months
  "fa-AF": ["", "جنوری", "فبروری", "مارچ", "اپریل", "می", "جون",
    "جولای", "آگست", "سپتمبر", "اکتوبر", "نومبر", "دسمبر"],
};

export const SOLAR_HIJRI_MONTHS = {
  fa: ["", "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"],
  "fa-AF": ["", "حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
    "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"],
};

// ISO code -> [unit, subunit or null]
export const CURRENCIES = {
  IRR: ["ریال", null],
  AFN: ["افغانی", "پول"],
  TJS: ["سامانی", "دیرم"],
  USD: ["دلار", "سنت"],
  EUR: ["یورو", "سنت"],
  GBP: ["پوند", "پنی"],
  RUB: ["روبل", "کوپک"],
};

export const CURRENCY_SYMBOLS = { "$": "USD", "€": "EUR", "£": "GBP", "₽": "RUB", "؋": "AFN", "﷼": "IRR" };

export const ABBREVIATIONS = {
  "ه.ش.": "هجری شمسی",
  "ه.ق.": "هجری قمری",
  "ق.م.": "قبل از میلاد",
  "ج.ا.ا.": "جمهوری اسلامی ایران",
};

const WORDS = {
  // [decimal point, percent] -- verify the Dari forms
  fa: ["ممیز", "درصد"],
  "fa-AF": ["اعشاریه", "فیصد"],
};

function decimalReader(point) {
  return (integer, fraction) => {
    // 2.05 -> "دو ممیز صفر پنج": leading zeros are read one by one
    const rest = fraction.replace(/^0+/, "");
    const zeros = fraction.length - rest.length;
    const parts = [toWords(integer), point, ...Array(zeros).fill("صفر")];
    if (rest) parts.push(toWords(toInt(rest)));
    return parts.join(" ");
  };
}

function money(amount, cents, code) {
  const [unit, subunit] = CURRENCIES[code];
  let words = `${toWords(amount)} ${unit}`;
  if (cents && subunit) words += ` و ${toWords(cents)} ${subunit}`;
  return words;
}

function time(hours, minutes) {
  if (!minutes) return `ساعت ${toWords(hours)}`;
  return `ساعت ${toWords(hours)} و ${toWords(minutes)} دقیقه`;
}

export function makePersianVerbalizer(variant) {
  const gregorian = GREGORIAN_MONTHS[variant];
  const solar = SOLAR_HIJRI_MONTHS[variant];
  const [point, percent] = WORDS[variant];

  function date(day, month, year) {
    // Years before 1500 are Solar Hijri (1405/01/12), others Gregorian.
    const months = year < 1500 ? solar : gregorian;
    return `${toOrdinal(day)} ${months[month]} ${toWords(year)}`;
  }

  function solarDate(m) {
    // Iranian and Afghan dates are written year first: 1405/01/12
    const year = toInt(m[1]);
    const month = toInt(m[2]);
    const day = toInt(m[3]);
    if (!(month >= 1 && month <= 12 && day >= 1 && day <= 31)) return m[0];
    return date(day, month, year);
  }

  const monthNames = [...gregorian.slice(1), ...solar.slice(1)].join("|");
  return makeVerbalizer({
    cardinal: toWords,
    ordinal: toOrdinal,
    decimal: decimalReader(point),
    percent: (words) => `${words} ${percent}`,
    money,
    date,
    time,
    minus: "منفی",
    dot: "نقطه",
    comma: "،",
    currencySymbols: CURRENCY_SYMBOLS,
    units: { "°C": "درجه", "°": "درجه" },
    abbreviations: ABBREVIATIONS,
    rules: [
      [new RegExp(`(?<!${W})(${D}{4})/(${D}{1,2})/(${D}{1,2})(?!${W})`, "gu"), solarDate],
      // a day before a month name is an ordinal: ۲۲ بهمن -> بیست و دوم بهمن
      [new RegExp(`(?<!${W})(${D}{1,2})(?=${S}+(?:${monthNames})(?!${W}))`, "gu"),
        (m) => toOrdinal(toInt(m[1]))],
      // ۵ام, ۲۱م -> ordinal
      [new RegExp(`(?<!${W})(${D}+)\\u200c?(?:ام|م)(?!${W})`, "gu"), (m) => toOrdinal(toInt(m[1]))],
    ],
  });
}
