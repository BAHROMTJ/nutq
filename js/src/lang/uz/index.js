// Uzbek (oʻzbekcha / ўзбекча): Latin and Cyrillic scripts.

import { fixLatinInCyrillic } from "../../core/lookalikes.js";
import { detectScript } from "../../scripts.js";
import * as translit from "./translit.js";
import * as verbalize from "./verbalize.js";
import { toOrdinal, toWords } from "./numbers.js";

/** Unify apostrophes (o'zbek -> oʻzbek) and fix Latin letters in Cyrillic words. */
export function clean(text) {
  return fixLatinInCyrillic(translit.fixApostrophes(text.normalize("NFC")));
}

export function normalize(text) {
  text = clean(text);
  if (detectScript(text, ["Latn", "Cyrl"]) === "Cyrl") return verbalize.cyrillic(text);
  return verbalize.latin(text);
}

export const LANGUAGE = {
  code: "uz",
  name: "Uzbek",
  nativeName: "oʻzbekcha",
  defaultScript: "Latn",
  scripts: ["Latn", "Cyrl"],
  cardinal: toWords,
  ordinal: toOrdinal,
  normalize,
  clean,
  converters: {
    "Cyrl->Latn": translit.toLatin,
    "Latn->Cyrl": translit.toCyrillic,
  },
  aliases: ["uzb", "uz-Latn", "uz-Cyrl", "uz-UZ"],
  status: "beta",
};
