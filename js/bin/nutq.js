#!/usr/bin/env node
// Command-line interface: nutq <command> --lang <code> [text]

import { clean, convert, languages, normalize, numberToWords, version } from "../src/index.js";

const USAGE = `usage: nutq [-h] [--version] {convert,normalize,clean,number,languages} ...

Script conversion and text normalization for Tajik, Persian, Dari and Uzbek.

commands:
  convert    convert between scripts
             nutq convert --lang tg --to Latn [--from Cyrl] [text ...]
  normalize  numbers, dates and money to words
             nutq normalize --lang tg [text ...]
  clean      fix look-alike characters
             nutq clean --lang tg [text ...]
  number     number to words
             nutq number --lang tg [--ordinal] [--script Latn] <value>
  languages  list supported languages

Text is read from standard input when no text arguments are given.
Options: --lang/-l, --to/-t, --from, --ordinal, --script, --help/-h, --version`;

class UsageError extends Error {}

// Options taking a value, per command, with their aliases.
const OPTIONS = {
  convert: { "--lang": "lang", "-l": "lang", "--to": "to", "-t": "to", "--from": "source" },
  normalize: { "--lang": "lang", "-l": "lang" },
  clean: { "--lang": "lang", "-l": "lang" },
  number: { "--lang": "lang", "-l": "lang", "--script": "script" },
  languages: {},
};
const FLAGS = { number: { "--ordinal": "ordinal" } };
const REQUIRED = { convert: ["lang", "to"], normalize: ["lang"], clean: ["lang"], number: ["lang"] };

function parse(argv) {
  if (argv.includes("-h") || argv.includes("--help") || argv.length === 0) {
    return { help: true, missing: argv.length === 0 };
  }
  if (argv[0] === "--version") return { version: true };
  const [command, ...rest] = argv;
  if (!(command in OPTIONS)) throw new UsageError(`invalid choice: '${command}'`);
  const options = OPTIONS[command];
  const flags = FLAGS[command] || {};
  const args = { command, positional: [] };
  let onlyPositional = false;
  for (let i = 0; i < rest.length; i++) {
    const arg = rest[i];
    if (onlyPositional || !arg.startsWith("-") || arg === "-" || /^-\d/.test(arg)) {
      args.positional.push(arg);
    } else if (arg === "--") {
      onlyPositional = true;
    } else if (arg in flags) {
      args[flags[arg]] = true;
    } else {
      const eq = arg.indexOf("=");
      const name = eq === -1 ? arg : arg.slice(0, eq);
      if (!(name in options)) throw new UsageError(`unrecognized arguments: ${arg}`);
      let value;
      if (eq !== -1) value = arg.slice(eq + 1);
      else if (i + 1 < rest.length) value = rest[++i];
      else throw new UsageError(`argument ${name}: expected one argument`);
      args[options[name]] = value;
    }
  }
  for (const key of REQUIRED[command] || []) {
    if (args[key] === undefined) {
      const names = Object.keys(options).filter((o) => options[o] === key).join("/");
      throw new UsageError(`the following arguments are required: ${names}`);
    }
  }
  if (command === "languages" && args.positional.length) {
    throw new UsageError(`unrecognized arguments: ${args.positional.join(" ")}`);
  }
  if (command === "number") {
    if (args.positional.length !== 1) {
      throw new UsageError(args.positional.length ? `unrecognized arguments: ${args.positional.slice(1).join(" ")}`
        : "the following arguments are required: value");
    }
    const text = args.positional[0].trim();
    if (!/^[+-]?\d+(?:_\d+)*$/.test(text)) {
      throw new UsageError(`argument value: invalid int value: '${args.positional[0]}'`);
    }
    const big = BigInt(text.replaceAll("_", ""));
    args.value = big >= BigInt(Number.MIN_SAFE_INTEGER) && big <= BigInt(Number.MAX_SAFE_INTEGER)
      ? Number(big) : big;
  }
  return args;
}

async function readText(args) {
  if (args.positional.length) return args.positional.join(" ");
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  // Like Python's text-mode stdin: universal newlines, trailing newlines removed.
  return Buffer.concat(chunks).toString("utf8").replace(/\r\n?/g, "\n").replace(/\n+$/, "");
}

function pad(text, width) {
  const size = Array.from(text).length;
  return size >= width ? text : text + " ".repeat(width - size);
}

async function main(argv) {
  let args;
  try {
    args = parse(argv);
  } catch (error) {
    if (!(error instanceof UsageError)) throw error;
    process.stderr.write(`usage: nutq [-h] [--version] {convert,normalize,clean,number,languages} ...\nnutq: error: ${error.message}\n`);
    return 2;
  }
  if (args.help) {
    (args.missing ? process.stderr : process.stdout).write(USAGE + "\n");
    return args.missing ? 2 : 0;
  }
  if (args.version) {
    process.stdout.write(version + "\n");
    return 0;
  }
  let output;
  switch (args.command) {
    case "convert":
      output = convert(await readText(args), args.lang, { to: args.to, source: args.source });
      break;
    case "normalize":
      output = normalize(await readText(args), args.lang);
      break;
    case "clean":
      output = clean(await readText(args), args.lang);
      break;
    case "number":
      output = numberToWords(args.value, args.lang, { ordinal: Boolean(args.ordinal), script: args.script });
      break;
    case "languages":
      output = languages()
        .map((l) => `${pad(l.code, 6)} ${pad(l.name, 8)} ${pad(l.nativeName, 10)} ${pad(l.scripts.join(", "), 16)} ${l.status}`)
        .join("\n");
      break;
  }
  process.stdout.write(output + "\n");
  return 0;
}

main(process.argv.slice(2)).then(
  (code) => {
    process.exitCode = code;
  },
  (error) => {
    process.stderr.write(`nutq: error: ${error.message}\n`);
    process.exitCode = 1;
  },
);
