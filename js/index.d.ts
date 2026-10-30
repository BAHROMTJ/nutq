// Type definitions for nutq 0.1.0

/** ISO 15924 script code. Script options also accept names such as "latin". */
export type Script = "Cyrl" | "Latn" | "Arab";

/** A script code or name: "Cyrl", "Latn", "Arab", "cyrillic", "latin", "arabic", "perso-arabic", ... */
export type ScriptName = Script | (string & {});

/** Converter key: "Source->Target", for example "Cyrl->Latn". */
export type ConverterKey = `${string}->${string}`;

export type Integer = number | bigint;

/** Fields accepted by `register()` and the `Language` constructor. */
export interface LanguageSpec {
  code: string;
  name: string;
  nativeName: string;
  defaultScript: string;
  scripts: readonly string[];
  /** Cardinal number words in `defaultScript`. */
  cardinal: (n: Integer) => string;
  /** Ordinal number words in `defaultScript`. */
  ordinal: (n: Integer) => string;
  /** Written text -> speakable words. */
  normalize: (text: string) => string;
  /** Fix characters only. */
  clean: (text: string) => string;
  converters?: Readonly<Record<ConverterKey, (text: string) => string>>;
  aliases?: readonly string[];
  /** Defaults to "beta". */
  status?: string;
  experimental?: ReadonlyArray<readonly [string, string]>;
}

/** Everything nutq knows about one language (immutable). */
export class Language {
  constructor(spec: LanguageSpec);
  readonly code: string;
  readonly name: string;
  readonly nativeName: string;
  readonly defaultScript: string;
  readonly scripts: readonly string[];
  readonly cardinal: (n: Integer) => string;
  readonly ordinal: (n: Integer) => string;
  readonly normalize: (text: string) => string;
  readonly clean: (text: string) => string;
  readonly converters: Readonly<Record<string, (text: string) => string>>;
  readonly aliases: readonly string[];
  readonly status: string;
  readonly experimental: ReadonlyArray<readonly [string, string]>;
  /** Converter from `source` to `target`, directly or through a third script. */
  converter(source: string, target: string): (text: string) => string;
}

/** Thrown when a language, script or conversion is not available. */
export class UnsupportedError extends RangeError {
  constructor(message?: string);
}

export interface ConvertOptions {
  /** Target script (required). */
  to: ScriptName;
  /** Source script; detected from the text when omitted. */
  source?: ScriptName | null;
}

export interface NumberOptions {
  /** Ordinal (1st, 2nd, ...) instead of cardinal. */
  ordinal?: boolean;
  /** Output script; defaults to the language's default script. */
  script?: ScriptName | null;
}

/** Convert `text` in language `lang` to another script. */
export function convert(text: string, lang: string, options: ConvertOptions): string;

/** Rewrite numbers, dates, times, money and abbreviations as words (also cleans). */
export function normalize(text: string, lang: string): string;

/** Fix characters only: look-alike letters, apostrophes, digit forms. */
export function clean(text: string, lang: string): string;

/**
 * Spell out an integer. Throws TypeError for non-integers (and booleans),
 * RangeError for |n| >= 10**18 and for ordinals of n < 1.
 */
export function numberToWords(n: Integer, lang: string, options?: NumberOptions): string;

/** All registered languages, sorted by code. */
export function languages(): Language[];

/** Look up a language by code or alias (case-insensitive, "_" = "-"). */
export function getLanguage(code: string): Language;

/** Add or replace a language. */
export function register(language: Language | LanguageSpec): Language;

/** The script most letters in `text` are written in, or null. */
export function detectScript(text: string, candidates?: Iterable<string> | null): Script | null;

/** ISO 15924 code for a script name; throws RangeError for unknown names. */
export function canonicalScript(name: string): Script;

export const version: string;
