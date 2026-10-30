// Integer checks shared by the number-to-words modules.

/**
 * Throw TypeError unless `n` is an integer (a whole Number or a BigInt).
 * Booleans are rejected, as in Python.
 */
export function checkInt(n, name) {
  if (typeof n === "bigint") return;
  if (typeof n !== "number" || !Number.isInteger(n)) {
    throw new TypeError(`${name}() expects an integer`);
  }
}

/**
 * Split a positive integer into groups of three digits, lowest first:
 * 1234567 -> [567, 234, 1]. Uses BigInt so that every integer value below
 * 10**18 is exact.
 */
export function thousands(n) {
  const groups = [];
  let rest = BigInt(n);
  while (rest) {
    groups.push(Number(rest % 1000n));
    rest /= 1000n;
  }
  return groups;
}
