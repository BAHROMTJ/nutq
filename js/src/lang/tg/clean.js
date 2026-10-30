// Clean up Tajik text typed with mixed or look-alike characters.
//
// People often type Tajik on Russian or Kazakh keyboards, or paste text where
// Latin letters that look like Cyrillic ones ("a", "o", "x") slipped into a
// word. Such text looks right but breaks search, sorting and spell checking.

import { fixLatinInCyrillic } from "../../core/lookalikes.js";
import { makeTranslator } from "../../core/text.js";

// Characters from other alphabets that are used in place of Tajik letters.
const LOOKALIKES = makeTranslator({
  "һ": "ҳ", "Һ": "Ҳ", // Kazakh/Bashkir shha
  "ӽ": "ҳ", "Ӽ": "Ҳ",
  "ҝ": "қ", "Ҝ": "Қ",
  "ҹ": "ҷ", "Ҹ": "Ҷ", // Azerbaijani/Abkhaz che
  "ҫ": "с", "Ҫ": "С",
});

/**
 * Return `text` with look-alike characters replaced by Tajik letters.
 *
 * - composes letters typed with a combining macron (и + ̄ -> ӣ)
 * - replaces letters borrowed from other Cyrillic alphabets (һ -> ҳ)
 * - replaces Latin letters hidden inside Cyrillic words (Тoҷик -> Тоҷик)
 *
 * Words written fully in Latin script are left untouched.
 */
export function clean(text) {
  return fixLatinInCyrillic(LOOKALIKES(text.normalize("NFC")));
}
