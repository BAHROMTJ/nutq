// Script codes (ISO 15924) and script detection.

import { isAlpha, pyStrip } from "./core/text.js";

const NAMES = {
  cyrl: "Cyrl", cyrillic: "Cyrl", "кириллӣ": "Cyrl",
  latn: "Latn", latin: "Latn", "лотинӣ": "Latn",
  arab: "Arab", arabic: "Arab", "perso-arabic": "Arab", persian: "Arab",
};

/**
 * Return the ISO 15924 code for a script name (`latin` -> `Latn`).
 * Throws RangeError (Python: ValueError) for unknown names.
 */
export function canonicalScript(name) {
  const key = pyStrip(String(name)).toLowerCase();
  if (Object.prototype.hasOwnProperty.call(NAMES, key)) return NAMES[key];
  throw new RangeError(`unknown script '${name}'; use Cyrl, Latn or Arab`);
}

/** Return the script of a single letter, or null for non-letters. */
export function scriptOf(char) {
  if (!isAlpha(char) && char !== "ʻ" && char !== "ʼ") return null;
  const code = char.codePointAt(0);
  if (code >= 0x0400 && code <= 0x052f) return "Cyrl";
  if (
    (code >= 0x0600 && code <= 0x06ff) || (code >= 0x0750 && code <= 0x077f) ||
    (code >= 0xfb50 && code <= 0xfdff) || (code >= 0xfe70 && code <= 0xfeff)
  ) {
    return "Arab";
  }
  if (code < 0x0250 || char === "ʻ" || char === "ʼ" || (code >= 0x1e00 && code <= 0x1eff)) {
    return "Latn";
  }
  return null;
}

/**
 * Return the script most letters in `text` are written in, or null.
 * `candidates` limits the scripts that are counted.
 *
 *     detectScript("Салом, dunyo!")  // "Cyrl"
 */
export function detectScript(text, candidates) {
  const allowed = candidates == null ? null : new Set(candidates);
  const counts = new Map();
  for (const char of text) {
    const script = scriptOf(char);
    if (script && (allowed === null || allowed.has(script))) {
      counts.set(script, (counts.get(script) || 0) + 1);
    }
  }
  let best = null;
  let bestCount = 0;
  for (const [script, count] of counts) {
    if (count > bestCount) {
      best = script;
      bestCount = count;
    }
  }
  return best;
}
