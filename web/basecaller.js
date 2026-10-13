/* Dependency-free CTC greedy decoder for already-inferred model probabilities.
 * This is not a raw-current signal model or a calibrated quality estimator.
 */
(function (root) {
  "use strict";
  const ALPHABET = ["blank", "A", "C", "G", "T"];
  const MAX_STEPS = 20000;

  function parseMatrix(input) {
    if (typeof input !== "string" || !input.trim()) {
      throw new Error("Provide a JSON matrix or CSV of timestep probabilities.");
    }
    if (input.length > 1000000) {
      throw new Error("Input exceeds the 1 MB safety limit.");
    }
    const value = input.trim();
    if (value.startsWith("[")) {
      let rows;
      try { rows = JSON.parse(value); }
      catch (_) { throw new Error("Invalid JSON probability matrix."); }
      return rows;
    }
    const lines = value.split(/\r?\n/).map(line => line.trim()).filter(Boolean);
    const first = lines[0].replace(/\s/g, "").toLowerCase();
    if (first === "blank,a,c,g,t" || first === "-,a,c,g,t") lines.shift();
    return lines.map(line => line.split(",").map(cell => Number(cell.trim())));
  }

  function decodeCTC(matrix) {
    if (!Array.isArray(matrix) || matrix.length === 0 || matrix.length > MAX_STEPS) {
      throw new Error("Provide between 1 and 20,000 probability rows.");
    }
    let previous = -1;
    let sequence = "";
    let emittedProbabilitySum = 0;
    let emittedCount = 0;

    for (let t = 0; t < matrix.length; t++) {
      const row = matrix[t];
      if (!Array.isArray(row) || row.length !== ALPHABET.length ||
          !row.every(p => typeof p === "number" && Number.isFinite(p) && p >= 0 && p <= 1)) {
        throw new Error("Row " + (t + 1) + " must contain five finite probabilities in [0, 1].");
      }
      const sum = row.reduce((a, b) => a + b, 0);
      if (Math.abs(sum - 1) > 0.01) {
        throw new Error("Row " + (t + 1) + " probabilities must sum to 1 (±0.01).");
      }
      let winner = 0;
      for (let c = 1; c < row.length; c++) {
        if (row[c] > row[winner]) winner = c;
      }
      // Standard CTC: collapse adjacent duplicates before removing blanks.
      if (winner !== 0 && winner !== previous) {
        sequence += ALPHABET[winner];
        emittedProbabilitySum += row[winner];
        emittedCount++;
      }
      previous = winner;
    }
    return {
      sequence: sequence,
      timesteps: matrix.length,
      bases: sequence.length,
      // Not a Phred score and not an estimated basecalling accuracy.
      meanEmittedArgmaxProbability: emittedCount ? emittedProbabilitySum / emittedCount : null
    };
  }

  function formatFasta(sequence, identifier) {
    const safeId = String(identifier || "example").replace(/[^A-Za-z0-9_.-]/g, "_").slice(0, 80) || "example";
    if (!/^[ACGT]*$/.test(sequence)) throw new Error("Invalid decoded DNA sequence.");
    return ">" + safeId + "\n" + (sequence.match(/.{1,80}/g) || [""]).join("\n") + "\n";
  }

  const api = { ALPHABET, parseMatrix, decodeCTC, formatFasta };
  if (typeof module === "object" && module.exports) module.exports = api;
  root.CTCDecoder = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
