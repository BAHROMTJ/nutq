// JavaScript-specific tests: errors, registry, script detection, CLI.

import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync, spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import * as nutq from "../src/index.js";

const CLI = fileURLToPath(new URL("../bin/nutq.js", import.meta.url));

function cli(args, input) {
  return execFileSync(process.execPath, [CLI, ...args], { input, encoding: "utf8" }).trim();
}

test("error types", () => {
  assert.throws(() => nutq.numberToWords(1.5, "tg"), TypeError);
  assert.throws(() => nutq.numberToWords(true, "tg"), TypeError);
  assert.throws(() => nutq.numberToWords("12", "tg"), TypeError);
  assert.throws(() => nutq.numberToWords(NaN, "tg"), TypeError);
  assert.throws(() => nutq.numberToWords(0, "tg", { ordinal: true }), RangeError);
  assert.throws(() => nutq.numberToWords(10 ** 18, "fa"), /too large/);
  assert.throws(() => nutq.numberToWords(-(10n ** 18n), "uz"), RangeError);
  assert.throws(() => nutq.getLanguage("xx"), nutq.UnsupportedError);
  assert.throws(() => nutq.convert("салом", "uz", { to: "Arab" }), nutq.UnsupportedError);
  assert.throws(() => nutq.convert("салом", "tg", { to: "klingon" }), RangeError);
  assert.throws(() => nutq.convert("салом", "tg"), TypeError);
  assert.throws(() => nutq.normalize(42, "tg"), TypeError);
  const error = (() => {
    try {
      nutq.getLanguage("xx");
    } catch (e) {
      return e;
    }
  })();
  assert.ok(error instanceof RangeError, "UnsupportedError extends RangeError (Python: ValueError)");
  assert.equal(error.name, "UnsupportedError");
  assert.match(error.message, /unknown language 'xx'; available: fa, fa-AF, tg, uz/);
});

test("integers beyond Number.MAX_SAFE_INTEGER are exact", () => {
  assert.equal(nutq.numberToWords(2n ** 53n + 1n, "uz"),
    // Python: nutq.number_to_words(2**53 + 1, "uz")
    "toʻqqiz kvadrillion yetti trillion yuz toʻqson toʻqqiz milliard ikki yuz ellik" +
    " toʻrt million yetti yuz qirq ming toʻqqiz yuz toʻqson uch");
  assert.equal(nutq.normalize("9007199254740993", "uz"), nutq.numberToWords(9007199254740993n, "uz"));
});

test("aliases", () => {
  assert.equal(nutq.getLanguage("prs").code, "fa-AF");
  assert.equal(nutq.getLanguage("FA_af").code, "fa-AF");
  assert.equal(nutq.getLanguage("tgk").code, "tg");
  assert.equal(nutq.getLanguage("uz-Cyrl").code, "uz");
  assert.deepEqual(nutq.languages().map((l) => l.code).filter((c) => !c.startsWith("x-")),
    ["fa", "fa-AF", "tg", "uz"]);
});

test("languages are immutable", () => {
  const tg = nutq.getLanguage("tg");
  assert.ok(Object.isFrozen(tg));
  assert.deepEqual([...tg.scripts], ["Cyrl", "Latn", "Arab"]);
  assert.equal(tg.nativeName, "тоҷикӣ");
});

test("register a custom language", () => {
  const lang = nutq.register({
    code: "x-test",
    name: "Test",
    nativeName: "test",
    defaultScript: "Latn",
    scripts: ["Latn", "Cyrl"],
    cardinal: String,
    ordinal: (n) => `${n}th`,
    normalize: (text) => text.toUpperCase(),
    clean: (text) => text.trim(),
    converters: { "Latn->Cyrl": (text) => text.replaceAll("a", "а") },
    aliases: ["x-tst"],
  });
  assert.ok(lang instanceof nutq.Language);
  assert.equal(nutq.normalize("abc", "x-test"), "ABC");
  assert.equal(nutq.clean("  abc ", "X_TST"), "abc");
  assert.equal(nutq.numberToWords(4, "x-test", { ordinal: true }), "4th");
  assert.equal(nutq.numberToWords(4, "x-test", { script: "Cyrl" }), "4");
  assert.equal(nutq.convert("aba", "x-test", { to: "cyrillic" }), "аbа");
  assert.throws(() => nutq.convert("аба", "x-test", { to: "Latn" }), nutq.UnsupportedError);
  assert.throws(() => nutq.register({ code: "x-bad" }), TypeError);
});

test("two-step conversion through a third script", () => {
  assert.equal(nutq.convert("Tojikiston", "tg", { to: "Arab" }), "تاجیکستان");
});

test("detectScript", () => {
  assert.equal(nutq.detectScript("Салом, dunyo!"), "Cyrl");
  assert.equal(nutq.detectScript("سلام dunyo"), "Latn");
  assert.equal(nutq.detectScript("سلام دنیا"), "Arab");
  assert.equal(nutq.detectScript("Oʻzbek"), "Latn");
  assert.equal(nutq.detectScript("123 !"), null);
  assert.equal(nutq.detectScript("Салом dunyo", ["Latn"]), "Latn");
  assert.equal(nutq.canonicalScript(" ARAB "), "Arab");
});

test("CLI commands", () => {
  assert.equal(cli(["convert", "-l", "tg", "--to", "Latn", "Душанбе"]), "Dushanbe");
  assert.equal(cli(["convert", "-l", "uz", "-t", "cyrillic", "Toshkent"]), "Тошкент");
  assert.equal(cli(["convert", "--lang=tg", "--to=Arab", "--from", "Cyrl", "Салом"]), "سلام");
  assert.equal(cli(["number", "-l", "tg", "2026"]), "ду ҳазору бисту шаш");
  assert.equal(cli(["number", "-l", "uz", "--ordinal", "2"]), "ikkinchi");
  assert.equal(cli(["number", "-l", "tg", "-5"]), "минус панҷ");
  assert.equal(cli(["normalize", "-l", "fa", "۱۵٪"]), "پانزده درصد");
  assert.equal(cli(["clean", "-l", "tg", "Тoҷик"]), "Тоҷик");
  assert.equal(cli(["normalize", "-l", "tg"], "15%\n"), "понздаҳ фоиз");
  assert.match(cli(["languages"]), /^tg {5}Tajik {4}тоҷикӣ {5}Cyrl, Latn, Arab beta$/m);
  assert.equal(cli(["--version"]), "0.1.0");
});

test("CLI errors", () => {
  const usage = spawnSync(process.execPath, [CLI, "convert", "-l", "tg", "x"], { encoding: "utf8" });
  assert.equal(usage.status, 2);
  assert.match(usage.stderr, /required: --to/);
  const failure = spawnSync(process.execPath, [CLI, "convert", "-l", "uz", "-t", "Arab", "x"], { encoding: "utf8" });
  assert.equal(failure.status, 1);
  assert.match(failure.stderr, /uz is not written in 'Arab'/);
});
