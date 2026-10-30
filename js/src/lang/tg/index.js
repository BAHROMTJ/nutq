// Tajik (тоҷикӣ): Cyrillic, Latin and Perso-Arabic scripts.

import * as arabic from "./arabic.js";
import * as translit from "./translit.js";
import { clean } from "./clean.js";
import { toOrdinal, toWords } from "./numbers.js";
import { verbalize } from "./verbalize.js";

export const LANGUAGE = {
  code: "tg",
  name: "Tajik",
  nativeName: "тоҷикӣ",
  defaultScript: "Cyrl",
  scripts: ["Cyrl", "Latn", "Arab"],
  cardinal: toWords,
  ordinal: toOrdinal,
  normalize: (text) => verbalize(clean(text)),
  clean,
  converters: {
    "Cyrl->Latn": (text) => translit.toLatin(text),
    "Latn->Cyrl": translit.toCyrillic,
    "Cyrl->Arab": arabic.toArabic,
    "Arab->Cyrl": arabic.toCyrillic,
  },
  aliases: ["tgk", "tg-Cyrl", "tg-TJ"],
  status: "beta",
  experimental: [["Arab", "Cyrl"], ["Arab", "Latn"]],
};
