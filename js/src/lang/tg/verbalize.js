// Tajik text normalization for speech: numbers, dates, money as words.
//
// Forms marked "verify" below were chosen by the authors and still need
// confirmation from a Tajik editor or linguist.

import { makeVerbalizer } from "../../core/verbalize.js";
import { D, W, length, toInt } from "../../core/text.js";
import { toOrdinal, toWords, withConjunction } from "./numbers.js";

export const MONTHS = [
  "", "январ", "феврал", "март", "апрел", "май", "июн",
  "июл", "август", "сентябр", "октябр", "ноябр", "декабр",
];

// ISO code -> [unit, subunit]
export const CURRENCIES = {
  TJS: ["сомонӣ", "дирам"],
  USD: ["доллар", "сент"],
  EUR: ["евро", "сент"],
  RUB: ["рубл", "копейка"],
  GBP: ["фунт", "пенс"],
};

export const CURRENCY_SYMBOLS = { "$": "USD", "€": "EUR", "₽": "RUB", "£": "GBP", "смн": "TJS" };

export const ABBREVIATIONS = {
  "ҶТ": "Ҷумҳурии Тоҷикистон",
  "ИДМ": "Иттиҳоди Давлатҳои Мустақил",
  "СММ": "Созмони Милали Муттаҳид",
  "ва ғ.": "ва ғайра",
  "ва ҳ.к.": "ва ҳоказо",
  "млн": "миллион",
  "млрд": "миллиард",
  "км": "километр",
  "кг": "килограмм",
  "см": "сантиметр",
  "мм": "миллиметр",
};

// Decimal fractions: 2,5 -> "ду бутуну панҷ даҳум" (verify).
const DENOMINATORS = { 1: "даҳум", 2: "садум", 3: "ҳазорум" };

function decimal(integer, fraction) {
  const denominator = DENOMINATORS[length(fraction)];
  if (denominator === undefined) {
    const digits = Array.from(fraction, (d) => toWords(toInt(d))).join(" ");
    return `${toWords(integer)} бутуну ${digits}`;
  }
  return `${toWords(integer)} бутуну ${toWords(toInt(fraction))} ${denominator}`;
}

function money(amount, cents, code) {
  const [unit, subunit] = CURRENCIES[code];
  let words = `${toWords(amount)} ${unit}`;
  if (cents) words = `${withConjunction(words)} ${toWords(cents)} ${subunit}`;
  return words;
}

function date(day, month, year) {
  // 12.03.2026 -> "дувоздаҳуми марти соли ду ҳазору бисту шаш"
  return `${toOrdinal(day)}и ${MONTHS[month]}и соли ${toWords(year)}`;
}

function time(hours, minutes) {
  // 14:30 -> "соати чордаҳу сӣ"
  if (!minutes) return `соати ${toWords(hours)}`;
  return `соати ${withConjunction(toWords(hours))} ${toWords(minutes)}`;
}

// 5-ум, 2-юм, 21-уми -> ordinal (with the izafat "и" kept)
const ORDINAL = new RegExp(`(?<!${W})(${D}+)-?(?:ум|юм)(и?)(?!${W})`, "gu");

export const verbalize = makeVerbalizer({
  cardinal: toWords,
  ordinal: toOrdinal,
  decimal,
  percent: (words) => `${words} фоиз`,
  money,
  date,
  time,
  minus: "минус",
  dot: "нуқта",
  currencySymbols: CURRENCY_SYMBOLS,
  units: { "°C": "дараҷа", "°": "дараҷа" },
  abbreviations: ABBREVIATIONS,
  rules: [[ORDINAL, (m) => toOrdinal(toInt(m[1])) + m[2]]],
});
