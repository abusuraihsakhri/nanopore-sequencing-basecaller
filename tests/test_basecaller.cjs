const { test } = require("node:test");
const assert = require("node:assert/strict");
const { parseMatrix, decodeCTC, formatFasta } = require("../web/basecaller.js");

test("standard CTC collapses duplicates and strips blank", () => {
  const decoded = decodeCTC([
    [.01,.96,.01,.01,.01], [.01,.96,.01,.01,.01],
    [.96,.01,.01,.01,.01], [.01,.96,.01,.01,.01],
    [.96,.01,.01,.01,.01], [.01,.01,.96,.01,.01]
  ]);
  assert.equal(decoded.sequence, "AAC");
  assert.equal(decoded.bases, 3);
  assert.equal(decoded.timesteps, 6);
});

test("blank-only matrix returns empty sequence", () => {
  const out = decodeCTC([[1,0,0,0,0]]);
  assert.equal(out.sequence, "");
  assert.equal(out.meanEmittedArgmaxProbability, null);
});

test("rejects invalid shape and probabilities", () => {
  assert.throws(() => decodeCTC([]), /between/);
  assert.throws(() => decodeCTC([[1,0,0,0]]), /five/);
  assert.throws(() => decodeCTC([[0.5,0.4,0,0,0]]), /sum/);
  assert.throws(() => decodeCTC([[NaN,0,0,0,1]]), /finite/);
  assert.throws(() => decodeCTC([[0,0,0,0,2]]), /finite/);
});

test("parses CSV header and JSON matrices", () => {
  const expected = [[0.8,0.2,0,0,0]];
  assert.deepEqual(parseMatrix("blank,A,C,G,T\n0.8,0.2,0,0,0"), expected);
  assert.deepEqual(parseMatrix(JSON.stringify(expected)), expected);
  assert.throws(() => decodeCTC(parseMatrix("{bad")), /five|finite/);
});

test("FASTA identifier is sanitized and sequence validated", () => {
  assert.equal(formatFasta("ACGT", "unsafe > id"), ">unsafe___id\nACGT\n");
  assert.throws(() => formatFasta("ACNX", "a"), /Invalid/);
});
