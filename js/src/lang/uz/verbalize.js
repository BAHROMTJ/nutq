// Uzbek text normalization for speech, in Latin or Cyrillic script.
//
// Words are generated in Latin and converted to Cyrillic when the input text
// is Cyrillic. All forms here still need review by a native Uzbek speaker.

import { makeVerbalizer } from "../../core/verbalize.js";
import { D, LETTER, S, W, length, toInt } from "../../core/text.js";
import { toOrdinal, toWords } from "./numbers.js";
import { toCyrillic } from "./translit.js";

export const MONTHS = [
  "", "yanvar", "fevral", "mart", "aprel", "may", "iyun",
  "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr",
];

export const CURRENCIES = {
  UZS: ["soʻm", "tiyin"],
  USD: ["dollar", "sent"],
  EUR: ["yevro", "sent"],
  RUB: ["rubl", "kopek"],
  GBP: ["funt", "pens"],
};

export const CURRENCY_SYMBOLS = { "$": "USD", "€": "EUR", "₽": "RUB", "£": "GBP" };

export const ABBREVIATIONS = {
  "OʻzR": "Oʻzbekiston Respublikasi",
  "BMT": "Birlashgan Millatlar Tashkiloti",
  "AQSH": "Amerika Qoʻshma Shtatlari",
  "va h.k.": "va hokazo",
  "mln": "million",
  "mlrd": "milliard",
  "km": "kilometr",
  "kg": "kilogramm",
  "sm": "santimetr",
  "mm": "millimetr",
};

const DENOMINATORS = { 1: "oʻndan", 2: "yuzdan", 3: "mingdan" };

function decimal(integer, fraction) {
  // 2,5 -> "ikki butun oʻndan besh"
  const denominator = DENOMINATORS[length(fraction)];
  if (denominator === undefined) {
    const digits = Array.from(fraction, (d) => toWords(toInt(d))).join(" ");
    return `${toWords(integer)} butun ${digits}`;
  }
  return `${toWords(integer)} butun ${denominator} ${toWords(toInt(fraction))}`;
}

function money(amount, cents, code) {
  const [unit, subunit] = CURRENCIES[code];
  let words = `${toWords(amount)} ${unit}`;
  if (cents) words += ` ${toWords(cents)} ${subunit}`;
  return words;
}

function date(day, month, year) {
  // 12.03.2026 is said like "2026-yil 12-mart" (verify)
  return `${toOrdinal(year)} yil ${toOrdinal(day)} ${MONTHS[month]}`;
}

function time(hours, minutes) {
  if (!minutes) return `soat ${toWords(hours)}`;
  return `soat ${toWords(hours)} ${toWords(minutes)} daqiqa`; // verify
}

const ordinalOf = (m) => toOrdinal(toInt(m[1]));

/** A number before "yil" or a month name is an ordinal even without a hyphen. */
function beforeDateWord(words) {
  return [new RegExp(`(?<!${W})(${D}+)(?=${S}+(?:${words.join("|")}))`, "giu"), ordinalOf];
}

const DATE_WORDS = ["yil", ...MONTHS.slice(1)];

const LATIN_RULES = [
  // 5-inchi, 3-chi -> ordinal
  [new RegExp(`(?<!${W})(${D}+)-(?:inchi|nchi|chi)(?!${W})`, "gu"), ordinalOf],
  // 12-mart, 2026-yil, 5-sinf: a hyphen before a word marks an ordinal
  [new RegExp(`(?<!${W})(${D}+)-(?=${LETTER})`, "gu"), ordinalOf],
  beforeDateWord(DATE_WORDS),
];
const CYRILLIC_RULES = [
  [new RegExp(`(?<!${W})(${D}+)-(?:инчи|нчи|чи)(?!${W})`, "gu"), ordinalOf],
  [new RegExp(`(?<!${W})(${D}+)-(?=${LETTER})`, "gu"), ordinalOf],
  beforeDateWord(DATE_WORDS.map(toCyrillic)),
];

function make(script) {
  const cyrillic = script === "Cyrl";
  const symbols = { ...CURRENCY_SYMBOLS, [cyrillic ? "сўм" : "soʻm"]: "UZS" };
  const abbreviations = cyrillic
    ? Object.fromEntries(Object.entries(ABBREVIATIONS).map(([k, v]) => [toCyrillic(k), v]))
    : ABBREVIATIONS;
  return makeVerbalizer({
    cardinal: toWords,
    ordinal: toOrdinal,
    decimal,
    percent: (words) => `${words} foiz`,
    money,
    date,
    time,
    minus: "minus",
    dot: "nuqta",
    currencySymbols: symbols,
    units: { "°C": "daraja", "°": "daraja" },
    abbreviations,
    rules: cyrillic ? CYRILLIC_RULES : LATIN_RULES,
    render: cyrillic ? toCyrillic : (words) => words,
  });
}

export const latin = make("Latn");
export const cyrillic = make("Cyrl");
