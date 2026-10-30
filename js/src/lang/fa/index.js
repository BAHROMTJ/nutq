// Persian (فارسی, Iran) and Dari (دری, Afghanistan).
//
// Persian and Dari are written only in the Perso-Arabic script. Conversion
// to and from Tajik Cyrillic lives in the Tajik module: use
// `convert(text, "tg", { to: "Cyrl" })`.

import { clean } from "./clean.js";
import { toOrdinal, toWords } from "./numbers.js";
import { makePersianVerbalizer } from "./verbalize.js";

const persian = makePersianVerbalizer("fa");
const dari = makePersianVerbalizer("fa-AF");

export const PERSIAN = {
  code: "fa",
  name: "Persian",
  nativeName: "فارسی",
  defaultScript: "Arab",
  scripts: ["Arab"],
  cardinal: toWords,
  ordinal: toOrdinal,
  normalize: (text) => persian(clean(text)),
  clean,
  aliases: ["fas", "per", "pes", "fa-IR"],
  status: "beta",
};

export const DARI = {
  code: "fa-AF",
  name: "Dari",
  nativeName: "دری",
  defaultScript: "Arab",
  scripts: ["Arab"],
  cardinal: toWords,
  ordinal: toOrdinal,
  normalize: (text) => dari(clean(text)),
  clean,
  aliases: ["prs", "dari"],
  status: "beta",
};
