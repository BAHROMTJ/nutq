// Helpers that reproduce Python's Unicode-aware string and regex behaviour.
//
// Python's `\w`, `\d`, `\s`, `str.isalpha()` and `str.isupper()` all follow
// Unicode; JavaScript's built-in versions mostly don't. The regex fragments
// below are meant for patterns compiled with the `u` flag.

/** Python `\w`: Unicode letters, numbers and underscore (no combining marks). */
export const W = "[\\p{L}\\p{N}_]";
/** Python `\W`. */
export const NW = "[^\\p{L}\\p{N}_]";
/** Body of `\w` for use inside a character class. */
export const W_BODY = "\\p{L}\\p{N}_";
/** Python `\d`: Unicode decimal digits (category Nd). */
export const D = "\\p{Nd}";
/** Python `\s` (characters for which `str.isspace()` is true). */
export const S = "[\\t\\n\\v\\f\\r\\x1c-\\x1f \\x85\\xa0\\u1680\\u2000-\\u200a\\u2028\\u2029\\u202f\\u205f\\u3000]";
/** Python `[^\W\d_]`: letters (and non-decimal numbers), no digits or "_". */
export const LETTER = "[\\p{L}\\p{Nl}\\p{No}]";

const ALPHA = /^\p{L}+$/u;
const UPPER = /^\p{Uppercase}$/u;
const NON_DIGIT = /\P{Nd}/gu;
const DIGIT = /^\p{Nd}$/u;
const PY_SPACE = new RegExp(`^${S}$`, "u");

/** Python `str.isalpha()`. */
export function isAlpha(text) {
  return ALPHA.test(text);
}

/** Python `str.isupper()` for a single character ("" is not upper). */
export function isUpperChar(char) {
  return UPPER.test(char);
}

/** Python `str.isspace()` for a single character. */
export function isSpaceChar(char) {
  return PY_SPACE.test(char);
}

/** The character (code point) at UTF-16 index `index`, or "". */
export function charAt(text, index) {
  if (index >= text.length) return "";
  return String.fromCodePoint(text.codePointAt(index));
}

/** Number of code points (Python `len`). */
export function length(text) {
  let n = 0;
  for (const _ of text) n++; // eslint-disable-line no-unused-vars
  return n;
}

function digitValue(char) {
  let cp = char.codePointAt(0);
  if (cp >= 0x30 && cp <= 0x39) return cp - 0x30;
  // Unicode decimal digits come in contiguous runs of ten, starting at zero.
  let start = cp;
  while (DIGIT.test(String.fromCodePoint(start - 1))) start--;
  return (cp - start) % 10;
}

/**
 * Python `int()` of a string of Unicode decimal digits. Returns a Number,
 * or a BigInt when the value is beyond Number.MAX_SAFE_INTEGER (so that
 * long digit strings stay exact, as Python ints do).
 */
export function toInt(text) {
  let value = 0n;
  for (const char of text) value = value * 10n + BigInt(digitValue(char));
  return value <= BigInt(Number.MAX_SAFE_INTEGER) ? Number(value) : value;
}

/** Python `int(re.sub(r"\D", "", text))`. */
export function digitsToInt(text) {
  return toInt(text.replace(NON_DIGIT, ""));
}

/** Python `str.translate` with a {char: replacement} table. */
export function makeTranslator(table) {
  const map = new Map(Object.entries(table));
  return (text) => {
    let out = "";
    for (const char of text) {
      const mapped = map.get(char);
      out += mapped === undefined ? char : mapped;
    }
    return out;
  };
}

/** Python `str.maketrans(from, to)` as a translator. */
export function makeCharTranslator(from, to) {
  const table = {};
  const a = Array.from(from);
  const b = Array.from(to);
  a.forEach((char, i) => {
    table[char] = b[i];
  });
  return makeTranslator(table);
}

/** Python `re.escape` for use in a `u`-flag pattern. */
export function escapeRegExp(text) {
  return text.replace(/[\\^$.*+?()[\]{}|/]/g, "\\$&");
}

/**
 * Python `pattern.sub(fn, text)`.
 *
 * `fn` receives a match object: `m[0]`, `m[1]` ... are the groups (undefined
 * when a group did not take part, like Python's None), `m.groups` the named
 * groups, `m.index`/`m.end` UTF-16 offsets and `m.input` the full string.
 */
export function sub(regex, text, fn) {
  const re = regex.global ? regex : new RegExp(regex.source, regex.flags + "g");
  re.lastIndex = 0;
  let out = "";
  let last = 0;
  let m;
  while ((m = re.exec(text)) !== null) {
    m.end = m.index + m[0].length;
    out += text.slice(last, m.index) + fn(m);
    last = m.end;
    if (m[0].length === 0) {
      re.lastIndex += text.codePointAt(re.lastIndex) > 0xffff ? 2 : 1;
    }
  }
  return out + text.slice(last);
}

/** Python `str.strip()` (Unicode whitespace as defined by `str.isspace`). */
export function pyStrip(text) {
  const chars = Array.from(text);
  let start = 0;
  let end = chars.length;
  while (start < end && isSpaceChar(chars[start])) start++;
  while (end > start && isSpaceChar(chars[end - 1])) end--;
  return chars.slice(start, end).join("");
}

/** Python `str.splitlines()`. */
export function splitLines(text) {
  const lines = text.split(/\r\n|[\n\r\v\f\x1c\x1d\x1e\x85\u2028\u2029]/);
  if (lines.length && lines[lines.length - 1] === "") lines.pop();
  return lines;
}
