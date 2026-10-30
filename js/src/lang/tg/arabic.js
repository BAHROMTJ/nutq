// Conversion between Tajik Cyrillic and the Perso-Arabic script.
//
// Cyrillic -> Arabic works in three steps for each word:
//
// 1. look the word up in the word list (spellings rules can't guess)
// 2. strip a known suffix (-ҳо, -ро, izafat -и, ...) and look the stem up
// 3. fall back to letter rules
//
// The rules cannot be exact. Persian does not write short vowels, and several
// Arabic letters share one Tajik letter (с = س ص ث, з = ز ذ ض ظ, т = ت ط,
// ҳ = ه ح). The word list (generated from
// src/nutq/lang/tg/data/arabic_words.tsv by scripts/build-data.mjs) fixes the
// common words where the rules are wrong.
//
// Arabic -> Cyrillic is experimental: without short vowels a word can only be
// read reliably with a dictionary, so unknown words come out approximate.

import { D, W, length, makeCharTranslator, makeTranslator, sub } from "../../core/text.js";
import { TO_ARABIC, TO_CYRILLIC } from "./arabic-words.js";
import { HUNDREDS, ONES, SCALES, TEENS, TENS } from "./numbers.js";

export const ZWNJ = "\u200c";

const VOWELS = new Set("аеёиӣоуӯэюя");

const CONSONANTS = new Map(Object.entries({
  "б": "ب", "в": "و", "г": "گ", "ғ": "غ", "д": "د", "ж": "ژ", "з": "ز",
  "й": "ی", "к": "ک", "қ": "ق", "л": "ل", "м": "م", "н": "ن", "п": "پ",
  "р": "ر", "с": "س", "т": "ت", "ф": "ف", "х": "خ", "ҳ": "ه", "ч": "چ",
  "ҷ": "ج", "ш": "ش", "ъ": "ع", "ц": "تس", "щ": "شچ", "ь": "",
}));

// [initial, medial, final] spelling of each vowel.
const VOWEL_FORMS = new Map(Object.entries({
  "а": ["ا", "", "ه"],
  "о": ["آ", "ا", "ا"],
  "и": ["ای", "ی", "ی"],
  "ӣ": ["ای", "ی", "ی"],
  "у": ["او", "و", "و"],
  "ӯ": ["او", "و", "و"],
  "е": ["ای", "ی", "ی"],
  "э": ["ا", "", "ه"],
  "ё": ["یا", "یا", "یا"],
  "ю": ["یو", "یو", "یو"],
  "я": ["ی", "ی", "یه"],
  "ы": ["ی", "ی", "ی"],
}));

// Suffix, Arabic form, shortest stem it can follow.
const SUFFIXES = [
  ["ҳоро", ZWNJ + "ها را", 2],
  ["ҳои", ZWNJ + "های", 2],
  ["ҳо", ZWNJ + "ها", 2],
  ["ро", " را", 3],
  ["тарин", ZWNJ + "ترین", 3], // comparative: калонтарин -> کلان‌ترین
  ["тар", ZWNJ + "تر", 3], // ширинтар -> شیرین‌تر (дафтар is in the word list)
  ["ён", "یان", 3], // plural after a vowel: донишҷӯён -> دانشجویان
  ["и", "", 3], // izafat; not written after a consonant
];

// Verb and word stems whose spelling the letter rules can't guess; matched
// at the start of a word, also after the negative "на-" (нахонд -> نخواند).
const STEMS = [
  ["хонд", "خواند"], ["хоҳ", "خواه"], ["хост", "خواست"], ["хоб", "خواب"],
  ["кун", "کن"], ["шуд", "شد"], ["гуфт", "گفت"],
];

// Present-tense verbs: ме-/наме- + stem + personal ending (мешавад -> می‌شود).
const VERB = new RegExp(`^(?:(на)?ме(?![ҳъ])(${W}+(?:ам|ӣ|ад|ем|ед|анд|ям|яд|янд)))$`, "u");

const PUNCT = makeTranslator({ ",": "،", "?": "؟", ";": "؛", "%": "٪" });
const PUNCT_BACK = makeTranslator({ "،": ",", "؟": "?", "؛": ";", "٪": "%", [ZWNJ]: "" });
const TO_PERSIAN_DIGITS = makeCharTranslator("0123456789", "۰۱۲۳۴۵۶۷۸۹");
const TO_LATIN_DIGITS = makeCharTranslator("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789");

const CYR_WORD = /[\u0400-\u052f]+/gu;
const ARAB_WORD = /[\u0621-\u063a\u0641-\u0652\u0671-\u06d3\u200c]+/gu;
const DIGIT_ORDINAL = new RegExp(`(${D})-?(?:ум|юм)и?(?![\\u0400-\\u052F])`, "gu"); // 21-ум -> ۲۱م
const DECIMAL = new RegExp(`(?<=${D})[.,](?=${D})`, "gu");

const IOTATED = new Map([["я", "а"], ["ё", "о"], ["ю", "у"]]);

function rules(word) {
  const verb = VERB.exec(word);
  if (verb) return (verb[1] ? "نمی" : "می") + ZWNJ + rules(verb[2]);
  for (const [stem, arabic] of STEMS) {
    for (const [lead, leadArabic] of [["", ""], ["на", "ن"]]) {
      if (word.startsWith(lead + stem)) {
        const plain = letters(lead + stem);
        const spelled = letters(word);
        if (spelled.startsWith(plain)) return leadArabic + arabic + spelled.slice(plain.length);
      }
    }
  }
  return letters(word);
}

function letters(word) {
  const chars = Array.from(word);
  const last = chars.length - 1;
  let out = "";
  chars.forEach((char, i) => {
    if (i > 0 && char === chars[i - 1] && !VOWELS.has(char)) return; // миллат -> ملت
    if (VOWEL_FORMS.has(char)) {
      let [initial, medial, final] = VOWEL_FORMS.get(char);
      if (IOTATED.has(char) && i > 0 && "иӣ".includes(chars[i - 1])) {
        // the "й" is already in the и: Русия -> روسیه, адабиёт -> ادبیات
        [initial, medial, final] = VOWEL_FORMS.get(IOTATED.get(char));
      }
      if (i === 0) out += initial;
      else if (i === last) out += final;
      else if (VOWELS.has(chars[i - 1]) && "аэ".includes(char)) out += "ا"; // carrier
      else out += medial;
    } else {
      out += CONSONANTS.has(char) ? CONSONANTS.get(char) : char;
    }
  });
  return out;
}

function attach(stem, suffix, arabicSuffix) {
  if (suffix === "и" && (stem.endsWith("ه") || stem.endsWith("ا") || stem.endsWith("و"))) {
    // izafat after a vowel: خانه‌ی, دریای
    return stem + (stem.endsWith("ه") ? ZWNJ : "") + "ی";
  }
  return stem + arabicSuffix;
}

// Number words, so that the linking "-у" can be written as a separate و
// (бисту панҷ -> بیست و پنج).
const NUMBER_WORDS = new Set([...ONES, ...TEENS, ...TENS, ...HUNDREDS, ...SCALES]);
NUMBER_WORDS.delete("");

function numberWithConjunction(lower) {
  if (lower.endsWith("иву") && NUMBER_WORDS.has(lower.slice(0, -3) + "ӣ")) {
    return lower.slice(0, -3) + "ӣ";
  }
  const last = lower.slice(-1);
  if ((last === "у" || last === "ю") && NUMBER_WORDS.has(lower.slice(0, -1))) {
    return lower.slice(0, -1);
  }
  return null;
}

/**
 * Return the stem of a word ending in the linking "-у"/"-ю" (шаъну -> шаън).
 *
 * "-у" follows a consonant and "-ю" a vowel. Short words (ту, ду, бӯ) and
 * words where the ending is part of the stem (тарозу) are in the word list.
 */
function nounWithConjunction(lower, words) {
  const stem = lower.slice(0, -1);
  const last = lower.slice(-1);
  if (!stem || (last !== "у" && last !== "ю")) return null;
  const afterVowel = VOWELS.has(stem.slice(-1));
  if ((last === "у") === afterVowel) return null;
  if (words.has(stem) || length(stem) >= (afterVowel ? 3 : 4)) return stem;
  return null;
}

/** Return the number word of an ordinal (якум -> як, сиюм -> сӣ). */
function ordinal(lower) {
  if (lower.endsWith("июм") && NUMBER_WORDS.has(lower.slice(0, -3) + "ӣ")) {
    return lower.slice(0, -3) + "ӣ";
  }
  const end = lower.slice(-2);
  if ((end === "ум" || end === "юм") && NUMBER_WORDS.has(lower.slice(0, -2))) {
    return lower.slice(0, -2);
  }
  return null;
}

/** Convert one Cyrillic word (any case) to Perso-Arabic script. */
export function wordToArabic(word) {
  const words = TO_ARABIC;
  const lower = word.toLowerCase();
  if (words.has(lower)) return words.get(lower);
  let number = numberWithConjunction(lower) || nounWithConjunction(lower, words);
  if (number) return wordToArabic(number) + " و";
  number = ordinal(lower);
  if (number) {
    if (number === "се") return "سوم";
    const arabic = wordToArabic(number);
    return arabic + (arabic.endsWith("ی") ? ZWNJ + "ام" : "م");
  }
  const size = length(lower);
  for (const [suffix, arabic, minStem] of SUFFIXES) {
    let stem = Array.from(lower).slice(0, Math.max(0, size - length(suffix))).join("");
    if (lower.endsWith(suffix) && length(stem) >= minStem) {
      if (suffix === "и" && stem.endsWith("и")) stem = stem.slice(0, -1) + "ӣ"; // давлатии = давлатӣ + izafat
      return attach(wordToArabic(stem), suffix, arabic);
    }
  }
  return rules(lower);
}

/**
 * Convert Tajik Cyrillic text to Perso-Arabic script.
 *     toArabic("Забони тоҷикӣ")  // "زبان تاجیکی"
 */
export function toArabic(text) {
  text = text.replace(DIGIT_ORDINAL, "$1م");
  text = sub(CYR_WORD, text, (m) => wordToArabic(m[0]));
  text = text.replace(DECIMAL, "٫");
  return TO_PERSIAN_DIGITS(PUNCT(text));
}

// -- Arabic -> Cyrillic (experimental) -----------------------------------------

const HARAKAT = new Map([
  ["\u064e", "а"], ["\u0650", "и"], ["\u064f", "у"], ["\u0652", ""], ["\u064b", "ан"],
]);

const BACK = new Map(Object.entries({
  "ب": "б", "پ": "п", "ت": "т", "ث": "с", "ج": "ҷ", "چ": "ч", "ح": "ҳ",
  "خ": "х", "د": "д", "ذ": "з", "ر": "р", "ز": "з", "ژ": "ж", "س": "с",
  "ش": "ш", "ص": "с", "ض": "з", "ط": "т", "ظ": "з", "ع": "ъ", "غ": "ғ",
  "ف": "ф", "ق": "қ", "ک": "к", "ك": "к", "گ": "г", "ل": "л", "م": "м",
  "ن": "н", "ء": "ъ", "أ": "а", "إ": "и", "ؤ": "ӯ", "ئ": "и", "ة": "а",
}));

const SHADDA = "\u0651";

function rulesBack(word) {
  const chars = Array.from(word);
  const last = chars.length - 1;
  const out = [];
  chars.forEach((char, i) => {
    const prevVowel = i > 0 && "اآویه".includes(chars[i - 1]);
    if (char === "آ") out.push("о");
    else if (char === "ا") out.push(i === 0 ? "а" : "о");
    else if (char === "و") out.push(i === 0 || (prevVowel && i < last) ? "в" : "у");
    else if (char === "ی" || char === "ي") {
      if (i === 0) out.push("й");
      else out.push(i === last ? "ӣ" : "и");
    } else if (char === "ه") out.push(i === last && i > 0 ? "а" : "ҳ");
    else if (char === SHADDA && out.length) out.push(out[out.length - 1]); // shadda doubles
    else if (HARAKAT.has(char)) out.push(HARAKAT.get(char));
    else out.push(BACK.has(char) ? BACK.get(char) : char);
  });
  let result = Array.from(out.join(""));
  if (result[0] === "ъ") result = result.slice(1);
  if (result.length > 2 && !VOWELS.has(result[0]) && !VOWELS.has(result[1])) {
    // Tajik words do not start with two consonants; the missing short
    // vowel is most often "а" (سلام -> салом).
    result = [result[0], "а", ...result.slice(1)];
  }
  return result.join("");
}

export function wordToCyrillic(word) {
  const words = TO_CYRILLIC;
  if (words.has(word)) return words.get(word);
  for (const [prefix, cyrillic] of [["نمی" + ZWNJ, "наме"], ["می" + ZWNJ, "ме"]]) {
    if (word.startsWith(prefix) && length(word) > length(prefix)) {
      return cyrillic + wordToCyrillic(word.slice(prefix.length));
    }
  }
  for (const [arabic, cyrillic] of [[ZWNJ + "ها", "ҳо"], ["ها", "ҳо"], [ZWNJ + "های", "ҳои"]]) {
    if (word.endsWith(arabic) && length(word) > length(arabic)) {
      return wordToCyrillic(word.slice(0, -arabic.length)) + cyrillic;
    }
  }
  // خوا is read "хо" (خواندن -> хондан)
  return rulesBack(word.replaceAll(ZWNJ, "").replaceAll("خوا", "خا"));
}

/** Convert Perso-Arabic text to Tajik Cyrillic (experimental, approximate). */
export function toCyrillic(text) {
  text = sub(ARAB_WORD, text, (m) => wordToCyrillic(m[0]));
  return TO_LATIN_DIGITS(PUNCT_BACK(text.replaceAll("٫", ",")));
}
