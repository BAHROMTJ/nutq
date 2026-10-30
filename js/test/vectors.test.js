// Run every vector exported from the Python test suite (scripts/export_vectors.py)
// through the JavaScript API and require identical output.

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import * as nutq from "../src/index.js";

const vectors = JSON.parse(readFileSync(new URL("./vectors.json", import.meta.url), "utf8"));

const FUNCTIONS = {
  convert: nutq.convert,
  normalize: nutq.normalize,
  clean: nutq.clean,
  number_to_words: nutq.numberToWords,
};

// Python exception name -> JavaScript error class.
const ERRORS = {
  UnsupportedError: nutq.UnsupportedError,
  TypeError,
  ValueError: RangeError,
};

function options(kwargs) {
  const out = {};
  for (const [key, value] of Object.entries(kwargs)) {
    if (value !== null) out[key] = value;
  }
  return out;
}

function call(vector) {
  const fn = FUNCTIONS[vector.fn];
  const args = [...vector.args];
  if (Object.keys(vector.kwargs).length) args.push(options(vector.kwargs));
  return fn(...args);
}

test(`vectors.json has vectors`, () => {
  assert.ok(vectors.length > 0);
});

vectors.forEach((vector, index) => {
  const name = `#${index} ${vector.fn}(${vector.args.map((a) => JSON.stringify(a)).join(", ")}` +
    `${Object.keys(vector.kwargs).length ? ", " + JSON.stringify(vector.kwargs) : ""})`;
  test(name, () => {
    if ("error" in vector) {
      const expected = ERRORS[vector.error];
      assert.ok(expected, `unknown error type ${vector.error}`);
      assert.throws(() => call(vector), expected);
    } else {
      assert.equal(call(vector), vector.result);
    }
  });
});
