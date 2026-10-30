// Letter case helpers for transliteration.

import { charAt, isUpperChar, length } from "./text.js";

/**
 * Apply the case of `source` to `target`.
 *
 * A single uppercase letter that maps to several letters is fully
 * uppercased inside an all-caps word (ШАҲР -> SHAHR) and only capitalised
 * otherwise (Шаҳр -> Shahr).
 */
export function matchCase(source, target, nextChar) {
  if (!isUpperChar(charAt(source, 0))) return target;
  if (length(source) > 1 || length(target) <= 1) return target.toUpperCase();
  if (isUpperChar(nextChar)) return target.toUpperCase();
  const first = charAt(target, 0);
  return first.toUpperCase() + target.slice(first.length);
}
