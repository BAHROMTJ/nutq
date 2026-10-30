// Language-independent pipeline that turns written text into speakable words.
//
// A language describes *how* to say things (number words, dates, money) in a
// Verbalizer; this module finds *where* those things are in the text.
//
// The steps run in a fixed order, and each one replaces digits with words, so
// later steps never see text an earlier step already handled:
//
// 1. language-specific rules (ordinal suffixes like "5-ум", "12-mart")
// 2. phone numbers (+992 93 123 45 67), read group by group
// 3. dates (DD.MM.YYYY, DD/MM/YYYY, YYYY-MM-DD)
// 4. version numbers (2.0.1)
// 5. times (14:30)
// 6. money ($25, 25 €, 100 смн)
// 7. percentages (15%) and units after a number (-5°C)
// 8. negative numbers, decimals and integers (with space-separated thousands)
// 9. abbreviations

import {
  D, W, W_BODY, S, charAt, digitsToInt, escapeRegExp, isAlpha, length,
  makeCharTranslator, sub, toInt,
} from "./text.js";

// Persian (U+06F0) and Arabic-Indic (U+0660) digits, and the Arabic decimal
// and percent signs.
const DIGITS = makeCharTranslator(
  "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩٫٪",
  "01234567890123456789.%",
);
const THOUSANDS_SIGN = new RegExp(`(?<=${D})\u066c(?=${D}{3})`, "gu");

export const INT = `(?:${D}{1,3}(?:[ \\xa0\\u202f]${D}{3})+(?!${D})|${D}+)`;
export const NUM = `${INT}(?:[.,]${D}+)?`;

const NB = `(?<!${W})`; // Python (?<!\w)
const NA = `(?!${W})`; // Python (?!\w)

const DATE_DMY = new RegExp(`${NB}(${D}{1,2})([./])(${D}{1,2})\\2(${D}{4})${NA}`, "gu");
const DATE_ISO = new RegExp(`${NB}(${D}{4})-(${D}{2})-(${D}{2})${NA}`, "gu");
const PHONE = new RegExp(`(?<![${W_BODY}+])\\+(${D}{1,3}(?:[ \\-]${D}{2,4}){2,})(?!${D})`, "gu");
const VERSION = new RegExp(`(?<![${W_BODY}.])${D}+(?:\\.${D}+){2,}(?![${W_BODY}.])`, "gu");
const TIME = new RegExp(`(?<![${W_BODY}:])([01]?${D}|2[0-3]):([0-5]${D})(?![${W_BODY}:])`, "gu");
const PERCENT = new RegExp(`${NB}(${NUM})${S}?%`, "gu");
const NUMBER = new RegExp(`(?:${NB}([-−])(?=${D}))?${NB}(${INT})(?:([.,])(${D}+))?(?!${D})`, "gu");
const SPACES = /[ \t]{2,}/g;
const LAST_WORD = new RegExp(`(${W}+)${S}*$`, "u");
const SPLIT_NUMBER = new RegExp(`^(${INT})(?:[.,](${D}+))?$`, "u");

/** Split "1 250,75" into [1250, "75"] (fraction undefined when absent). */
function splitNumber(text) {
  const match = SPLIT_NUMBER.exec(text);
  return [digitsToInt(match[1]), match[2]];
}

function isDate(day, month) {
  return day >= 1 && day <= 31 && month >= 1 && month <= 12;
}

function byLengthDesc(keys) {
  return [...keys].sort((a, b) => length(b) - length(a));
}

/**
 * How one language says numbers, dates, times and money.
 *
 * Every callable returns words in the language's default script; `render`
 * can convert them afterwards (Uzbek uses it to answer Cyrillic text in
 * Cyrillic). The returned object is callable: `verbalizer(text)`.
 *
 * Options: cardinal(n), ordinal(n), decimal(integer, fractionDigits),
 * percent(words), money(amount, cents|null, isoCode), date(d, m, y),
 * time(h, m), minus, dot ("."), comma (","), currencySymbols, units,
 * abbreviations, rules ([[RegExp, (match) => words], ...]), render.
 */
export function makeVerbalizer(options) {
  const v = {
    dot: ".",
    comma: ",",
    currencySymbols: {},
    units: {},
    abbreviations: {},
    rules: [],
    render: (words) => words,
    ...options,
  };

  const symbols = byLengthDesc(Object.keys(v.currencySymbols));
  let money = null;
  if (symbols.length) {
    const sym = symbols.map(escapeRegExp).join("|");
    money = new RegExp(
      `(?:${NB}(?<s1>${sym})${S}?(?<n1>${NUM})|${NB}(?<n2>${NUM})${S}?(?<s2>${sym}))${NA}`,
      "gu",
    );
  }
  const unitKeys = byLengthDesc(Object.keys(v.units));
  const unit = unitKeys.length
    ? new RegExp(
      `(?:${NB}([-−])(?=${D}))?${NB}(${NUM})${S}?(${unitKeys.map(escapeRegExp).join("|")})${NA}`,
      "gu",
    )
    : null;
  const abbrKeys = byLengthDesc(Object.keys(v.abbreviations));
  const abbr = abbrKeys.length
    ? new RegExp(`${NB}(${abbrKeys.map(escapeRegExp).join("|")})${NA}`, "gu")
    : null;

  /** Render `words` and keep them apart from a letter glued to the match. */
  function out(words, m) {
    words = v.render(words);
    if (m.end < m.input.length && isAlpha(charAt(m.input, m.end))) words += " ";
    return words;
  }

  function number(text) {
    const [integer, fraction] = splitNumber(text);
    if (fraction === undefined) return v.cardinal(integer);
    return v.decimal(integer, fraction);
  }

  function dateDmy(m) {
    const day = toInt(m[1]);
    const month = toInt(m[3]);
    const year = toInt(m[4]);
    if (!isDate(day, month)) return m[0];
    return out(v.date(day, month, year), m);
  }

  function dateIso(m) {
    const year = toInt(m[1]);
    const month = toInt(m[2]);
    const day = toInt(m[3]);
    if (!isDate(day, month)) return m[0];
    return out(v.date(day, month, year), m);
  }

  function phone(m) {
    const groups = m[1].split(/[ -]/);
    return out(groups.map((g) => v.cardinal(toInt(g))).join(`${v.comma} `), m);
  }

  function version(m) {
    const parts = m[0].split(".");
    return out(parts.map((p) => v.cardinal(toInt(p))).join(` ${v.dot} `), m);
  }

  function unitSub(m) {
    let words = number(m[2]);
    if (m[1]) words = v.minus + " " + words;
    return out(words + " " + v.units[m[3]], m);
  }

  function time(m) {
    let words = v.time(toInt(m[1]), toInt(m[2]));
    // Don't repeat the word "hour" when the text already has it
    // ("соати 14:30" -> "соати чордаҳу сӣ").
    const before = LAST_WORD.exec(m.input.slice(0, m.index));
    const space = words.indexOf(" ");
    const first = space === -1 ? words : words.slice(0, space);
    const rest = space === -1 ? "" : words.slice(space + 1);
    if (before && rest) {
      const previous = before[1].toLowerCase();
      if (first.toLowerCase().startsWith(previous) || previous.startsWith(first.toLowerCase())) {
        words = rest;
      }
    }
    return out(words, m);
  }

  function moneySub(m) {
    const symbol = m.groups.s1 || m.groups.s2;
    const [amount, fraction] = splitNumber(m.groups.n1 || m.groups.n2);
    let cents = null;
    if (fraction !== undefined) cents = toInt(fraction.padEnd(2, "0").slice(0, 2));
    return out(v.money(amount, cents || null, v.currencySymbols[symbol]), m);
  }

  function percent(m) {
    return out(v.percent(number(m[1])), m);
  }

  function numberSub(m) {
    const [, sign, integer, , fraction] = m;
    const value = digitsToInt(integer);
    let words = fraction === undefined ? v.cardinal(value) : v.decimal(value, fraction);
    if (sign) words = v.minus + " " + words;
    return out(words, m);
  }

  function abbreviation(m) {
    return v.render(v.abbreviations[m[1]]);
  }

  function verbalize(text) {
    text = DIGITS(text.replace(THOUSANDS_SIGN, ""));
    for (const [pattern, handler] of v.rules) {
      text = sub(pattern, text, (m) => out(handler(m), m));
    }
    text = sub(PHONE, text, phone);
    text = sub(DATE_DMY, text, dateDmy);
    text = sub(DATE_ISO, text, dateIso);
    text = sub(VERSION, text, version);
    text = sub(TIME, text, time);
    if (money !== null) text = sub(money, text, moneySub);
    text = sub(PERCENT, text, percent);
    if (unit !== null) text = sub(unit, text, unitSub);
    text = sub(NUMBER, text, numberSub);
    if (abbr !== null) text = sub(abbr, text, abbreviation);
    return text.replace(SPACES, " ");
  }

  verbalize.number = number;
  return verbalize;
}
