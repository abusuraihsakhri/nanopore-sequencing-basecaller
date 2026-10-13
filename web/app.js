"use strict";
(function () {
  const $ = id => document.getElementById(id);
  let lastFasta = null;
  function message(id, text, isError) {
    const el = $(id);
    el.textContent = text;
    el.className = isError ? "error" : "success";
  }
  $("decode").addEventListener("click", function () {
    lastFasta = null;
    $("download").disabled = true;
    try {
      const parsed = CTCDecoder.parseMatrix($("matrix").value);
      const result = CTCDecoder.decodeCTC(parsed);
      lastFasta = CTCDecoder.formatFasta(result.sequence, $("read-id").value);
      const confidence = result.meanEmittedArgmaxProbability === null
        ? "n/a" : result.meanEmittedArgmaxProbability.toFixed(4);
      $("decoded-result").textContent = lastFasta + "\nTimesteps: " + result.timesteps +
        "\nEmitted bases: " + result.bases +
        "\nMean emitted argmax probability (uncalibrated): " + confidence;
      $("download").disabled = false;
      message("decode-status", "Decoded locally. No sequencing quality score is inferred.", false);
    } catch (error) {
      $("decoded-result").textContent = "";
      message("decode-status", error.message, true);
    }
  });
  $("download").addEventListener("click", function () {
    if (lastFasta === null) return;
    const url = URL.createObjectURL(new Blob([lastFasta], { type: "text/plain;charset=utf-8" }));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "ctc_demo.fasta";
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
  });
  $("matrix-file").addEventListener("change", async function () {
    const file = this.files[0];
    if (!file) return;
    if (file.size > 1000000) { message("decode-status", "File exceeds 1 MB.", true); return; }
    try {
      $("matrix").value = await file.text();
      message("decode-status", "File loaded locally. Press Decode CTC to validate.", false);
    } catch (_) {
      message("decode-status", "Cannot read the selected file.", true);
    }
  });
  $("evaluate").addEventListener("click", function () {
    const primary = Number($("primary").value);
    const secondary = Number($("secondary").value);
    if (!$("primary").value.trim() || !$("secondary").value.trim() ||
        !Number.isFinite(primary) || !Number.isFinite(secondary)) {
      message("audit-status", "Enter finite numeric values for both metrics.", true);
      $("audit-result").textContent = "";
      return;
    }
    const alerts = [];
    if (primary > 25) alerts.push("ELEVATED: Primary metric exceeds 25.");
    if ($("critical").checked) alerts.push("CRITICAL: Explicit critical flag is set.");
    else if (secondary > 12) alerts.push("ELEVATED: Secondary metric exceeds 12.");
    const status = $("descriptor").value.toUpperCase();
    if (["DISCORDANT", "ANOMALY", "MUTANT", "VIOLATION", "FAIL", "REJECT"].some(x => status.includes(x))) {
      alerts.push("ELEVATED: Status descriptor matches an anomaly keyword.");
    }
    $("audit-result").textContent = (alerts.some(x => x.startsWith("CRITICAL")) ? "CRITICAL_STAT_PANIC" :
      alerts.length ? "ELEVATED_RISK" : "ROUTINE") + "\n" +
      (alerts.length ? alerts.join("\n") : "No rule-based alerts.");
    message("audit-status", "Local demonstration only; no clinical or instrument validation.", false);
  });
})();
