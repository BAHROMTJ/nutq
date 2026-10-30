// Language registry.
//
// Every language is described by a `Language` object. Built-in languages
// live in `src/lang/` and are registered the first time the registry is used.
// Other code can add languages with `register()`.

import { BUILTIN_LANGUAGES } from "./lang/index.js";
import { canonicalScript } from "./scripts.js";

/**
 * Thrown when a language, script or conversion is not available.
 * Extends RangeError, as the Python version extends ValueError.
 */
export class UnsupportedError extends RangeError {
  constructor(message) {
    super(message);
    this.name = "UnsupportedError";
  }
}

const REQUIRED = [
  "code", "name", "nativeName", "defaultScript", "scripts",
  "cardinal", "ordinal", "normalize", "clean",
];
const FUNCTIONS = ["cardinal", "ordinal", "normalize", "clean"];

function compareTuple(a, b) {
  for (let i = 0; i < a.length; i++) {
    if (a[i] < b[i]) return -1;
    if (a[i] > b[i]) return 1;
  }
  return 0;
}

/**
 * Everything nutq knows about one language.
 *
 * `cardinal` and `ordinal` return words in `defaultScript`. `normalize`
 * turns written text into speakable words; `clean` only fixes characters.
 * `converters` maps "Source->Target" (for example "Cyrl->Latn") to a function.
 */
export class Language {
  constructor(spec) {
    if (spec === null || typeof spec !== "object") {
      throw new TypeError("Language() expects an object");
    }
    for (const key of REQUIRED) {
      if (spec[key] === undefined) throw new TypeError(`Language() missing required field '${key}'`);
    }
    for (const key of FUNCTIONS) {
      if (typeof spec[key] !== "function") throw new TypeError(`Language.${key} must be a function`);
    }
    const converters = {};
    for (const [key, fn] of Object.entries(spec.converters || {})) {
      if (!/^[^>]+->[^>]+$/.test(key) || typeof fn !== "function") {
        throw new TypeError(`Language.converters: expected "Source->Target": function, got '${key}'`);
      }
      converters[key] = fn;
    }
    this.code = String(spec.code);
    this.name = String(spec.name);
    this.nativeName = String(spec.nativeName);
    this.defaultScript = String(spec.defaultScript);
    this.scripts = Object.freeze([...spec.scripts]);
    this.cardinal = spec.cardinal;
    this.ordinal = spec.ordinal;
    this.normalize = spec.normalize;
    this.clean = spec.clean;
    this.converters = Object.freeze(converters);
    this.aliases = Object.freeze([...(spec.aliases || [])]);
    this.status = spec.status === undefined ? "beta" : String(spec.status);
    this.experimental = Object.freeze((spec.experimental || []).map((pair) => Object.freeze([...pair])));
    Object.freeze(this);
  }

  /**
   * Return a function converting `source` script to `target`.
   *
   * If there is no direct converter, a two-step path through a third script
   * is used (for example Latin -> Cyrillic -> Arabic).
   */
  converter(source, target) {
    const direct = this.converters[`${source}->${target}`];
    if (direct) return direct;
    for (const [key, first] of Object.entries(this.converters)) {
      const [src, middle] = key.split("->");
      const second = this.converters[`${middle}->${target}`];
      if (src === source && second !== undefined) return (text) => second(first(text));
    }
    const available = Object.keys(this.converters)
      .map((key) => key.split("->"))
      .sort(compareTuple)
      .map(([s, t]) => `${s}->${t}`)
      .join(", ");
    throw new UnsupportedError(
      `${this.code}: no conversion from ${source} to ${target}; available: ${available}`,
    );
  }
}

const LANGUAGES = new Map();
const ALIASES = new Map();
let loaded = false;

function add(language) {
  const lang = language instanceof Language ? language : new Language(language);
  const key = lang.code.toLowerCase();
  LANGUAGES.set(key, lang);
  for (const alias of [lang.code, ...lang.aliases]) ALIASES.set(alias.toLowerCase(), key);
  return lang;
}

function load() {
  if (loaded) return;
  loaded = true;
  for (const spec of BUILTIN_LANGUAGES) add(spec);
}

/**
 * Add `language` to the registry (replacing one with the same code).
 * Accepts a `Language` or a plain object with the same fields.
 */
export function register(language) {
  load();
  return add(language);
}

/** Return the language for a BCP-47 or ISO 639 code (`tg`, `fa-AF`, `prs`). */
export function getLanguage(code) {
  load();
  if (typeof code !== "string") throw new TypeError("language code must be a string");
  const key = ALIASES.get(code.toLowerCase().replaceAll("_", "-"));
  if (key === undefined) {
    const codes = [...LANGUAGES.values()].map((l) => l.code).sort().join(", ");
    throw new UnsupportedError(`unknown language '${code}'; available: ${codes}`);
  }
  return LANGUAGES.get(key);
}

/** Return all registered languages, sorted by code. */
export function languages() {
  load();
  return [...LANGUAGES.values()].sort((a, b) => (a.code < b.code ? -1 : a.code > b.code ? 1 : 0));
}

export function resolveScript(language, script) {
  if (script === null || script === undefined) return null;
  const code = canonicalScript(script);
  if (!language.scripts.includes(code)) {
    throw new UnsupportedError(
      `${language.code} is not written in '${script}'; scripts: ${language.scripts.join(", ")}`,
    );
  }
  return code;
}
