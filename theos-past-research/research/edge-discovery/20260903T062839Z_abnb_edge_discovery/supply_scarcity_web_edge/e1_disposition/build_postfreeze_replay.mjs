import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadArtifactTool } from "../../../../../scripts/artifact_tool_runtime.mjs";

const { SpreadsheetFile, Workbook } = await loadArtifactTool();

const outputDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(outputDir, "../../../../..");
const readinessDir = path.join(
  repoRoot,
  "research/readiness/20260903T053309Z_abnb_readiness",
);
const completedAt = "2026-09-03T16:02:58Z";
const frozenAt = "2026-09-03T15:56:21Z";

async function rowsFromCsv(filePath, sheetName) {
  const csvText = await fs.readFile(filePath, "utf8");
  const workbook = await Workbook.fromCSV(csvText, { sheetName });
  const sheet = workbook.worksheets.getItem(sheetName);
  const values = sheet.getUsedRange().values;
  const headers = values[0].map((value) => String(value));
  return values.slice(1).map((row) =>
    Object.fromEntries(headers.map((header, index) => [header, row[index] ?? ""])),
  );
}

function csvCell(value) {
  if (value === null || value === undefined) return "";
  const text = String(value);
  return /[",\n\r]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

function toCsv(headers, rows) {
  return [
    headers.map(csvCell).join(","),
    ...rows.map((row) => headers.map((header) => csvCell(row[header])).join(",")),
  ].join("\n") + "\n";
}

function numberOrNull(value) {
  if (value === "" || value === null || value === undefined) return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function boolValue(value) {
  return String(value).toLowerCase() === "true";
}

function isoTimestamp(value) {
  if (value instanceof Date) return value.toISOString().replace(".000Z", "Z");
  return String(value);
}

function direction(delta) {
  if (delta === null) return "";
  if (delta > 0) return "up";
  if (delta < 0) return "down";
  return "neutral";
}

function previousYearGuidedPeriod(period) {
  const match = /^(\d{4})Q([1-4])$/.exec(period);
  if (!match) return "";
  return `${Number(match[1]) - 1}Q${match[2]}`;
}

function makeBaseline(target, baselineTarget, unavailableReason) {
  const targetValue = numberOrNull(target.target_midpoint);
  const baselineValue = baselineTarget
    ? numberOrNull(baselineTarget.target_midpoint)
    : null;
  if (targetValue === null) {
    return {
      predictionId: "",
      value: "",
      status: "target_non_numeric",
      delta: "",
      targetDirection: "",
    };
  }
  if (!baselineTarget || baselineValue === null) {
    return {
      predictionId: baselineTarget?.prediction_id ?? "",
      value: "",
      status: unavailableReason,
      delta: "",
      targetDirection: "",
    };
  }
  const delta = targetValue - baselineValue;
  return {
    predictionId: baselineTarget.prediction_id,
    value: baselineValue,
    status: "available",
    delta,
    targetDirection: direction(delta),
  };
}

const targets = await rowsFromCsv(
  path.join(readinessDir, "target_panel.csv"),
  "Targets",
);
const earlyReplay = await rowsFromCsv(
  path.join(readinessDir, "cohort_2020q4_2023q2_replay.csv"),
  "EarlyReplay",
);
const lateReplay = await rowsFromCsv(
  path.join(readinessDir, "cohort_2023q3_2026q2_replay.csv"),
  "LateReplay",
);

if (targets.length !== 23) {
  throw new Error(`Expected 23 target rows, found ${targets.length}`);
}

const targetByGuidedPeriod = new Map(
  targets.map((target) => [String(target.guided_fiscal_period), target]),
);
const h001ByPrediction = new Map();
for (const row of [...earlyReplay, ...lateReplay]) {
  if (String(row.signal_id) !== "H-001") continue;
  h001ByPrediction.set(String(row.prediction_id), {
    eligible: boolValue(row.eligible),
    implication: String(row.signal_implication ?? ""),
    classification: String(row.replay_classification || row.classification || ""),
  });
}
if (h001ByPrediction.size !== 23) {
  throw new Error(`Expected 23 H-001 replay rows, found ${h001ByPrediction.size}`);
}

const hypotheses = [
  {
    hypothesisId: "H-005",
    sourceId: "ORANGE_FL_TDT_RELEASES",
    sourceExactUrl: "https://www.occompt.com/quicklinks.aspx?CID=39",
    expectedDirection: "positive",
    primaryFormula:
      "year-over-year percentage change in the trailing three-month sum of Orange County TDT collections using only monthly PDFs with initial publication timestamps strictly before cutoff",
    sensitivityFormula:
      "latest single released collection month's year-over-year percentage change; no seasonal adjustment, threshold, or post-hoc month selection",
    featureUnit: "percent",
    missingness:
      "source_observation; collection_reference_month; initial_publication_timestamp; released_amount; stable_tax_definition; trailing_3m_yoy_comparator",
    baseExclusion:
      "permission gate denied; no lawful source request or source observation; initial publication timing and tax-definition stability cannot be verified",
    preRegime: false,
  },
  {
    hypothesisId: "H-006",
    sourceId: "NYC_OSE_STR_SNAPSHOTS",
    sourceExactUrl:
      "https://www.nyc.gov/site/specialenforcement/registration-law/registration-and-listing-data.page",
    expectedDirection: "positive",
    primaryFormula:
      "percentage change in unique active registration numbers between consecutive dated OSE snapshots proven published strictly before cutoff, aggregated citywide with no addresses or listing identifiers",
    sensitivityFormula:
      "grant-to-application ratio from the latest dated annual registration report strictly before cutoff; no borough selection, threshold, or address-level retention",
    featureUnit: "percent",
    missingness:
      "source_observation; dated_snapshot_transition; initial_publication_timestamp; released_vintage; active_registration_definition",
    baseExclusion:
      "permission gate denied; no lawful source request or source observation; historical snapshots and exact initial publication timing cannot be verified",
    preRegime: true,
  },
];

const replayHeaders = [
  "replay_id",
  "hypothesis_id",
  "hypothesis_version",
  "hypothesis_frozen_at_utc",
  "source_id",
  "source_exact_url",
  "prediction_id",
  "cohort",
  "issuing_fiscal_period",
  "guided_fiscal_period",
  "cutoff_utc",
  "target_source_id",
  "target_citation",
  "target_type",
  "target_low",
  "target_high",
  "target_midpoint",
  "target_unit",
  "currency",
  "constant_currency_basis",
  "frozen_expected_direction",
  "frozen_primary_formula",
  "frozen_sensitivity_formula",
  "source_permission_status",
  "source_request_count",
  "source_observation_date",
  "source_reference_period",
  "source_initial_publication_utc",
  "source_revision_or_vintage",
  "source_feature_value",
  "source_feature_unit",
  "primary_signal_implication",
  "event_status",
  "eligible",
  "exclusion_reason",
  "missingness",
  "seasonal_baseline_name",
  "seasonal_baseline_prediction_id",
  "seasonal_baseline_value",
  "seasonal_baseline_status",
  "target_change_vs_seasonal",
  "target_direction_vs_seasonal",
  "seasonal_replay_classification",
  "prior_quarter_baseline_name",
  "prior_quarter_baseline_prediction_id",
  "prior_quarter_baseline_value",
  "prior_quarter_baseline_status",
  "target_change_vs_prior_quarter",
  "target_direction_vs_prior_quarter",
  "prior_quarter_replay_classification",
  "h001_comparator_status",
  "h001_signal_implication",
  "h001_replay_classification",
  "h001_source_replay_path",
  "discrepancies",
  "leakage_warnings",
  "completed_at_utc",
];

const replayRows = [];
for (const hypothesis of hypotheses) {
  for (let index = 0; index < targets.length; index += 1) {
    const target = targets[index];
    const seasonalTarget = targetByGuidedPeriod.get(
      previousYearGuidedPeriod(String(target.guided_fiscal_period)),
    );
    const previousTarget = index > 0 ? targets[index - 1] : null;
    const seasonal = makeBaseline(
      target,
      seasonalTarget,
      "same_guided_quarter_prior_year_midpoint_unavailable",
    );
    const prior = makeBaseline(
      target,
      previousTarget,
      "prior_quarter_guidance_midpoint_unavailable",
    );
    const h001 = h001ByPrediction.get(String(target.prediction_id));
    const h001Comparable =
      numberOrNull(target.target_midpoint) !== null &&
      h001?.eligible === true &&
      ["hit", "miss", "neutral"].includes(h001.classification);
    const cutoffUtc = isoTimestamp(target.guidance_available_at_utc);
    const preRegime =
      hypothesis.preRegime &&
      cutoffUtc < "2023-09-01T00:00:00Z";
    const eventStatus = preRegime ? "excluded" : "not_testable";
    const exclusionReason = preRegime
      ? "pre-regime structural exclusion: cutoff precedes the September 2023 NYC registration regime; permission gate is also denied and no source observation was collected"
      : hypothesis.baseExclusion;

    replayRows.push({
      replay_id: `${hypothesis.hypothesisId}-${target.prediction_id}`,
      hypothesis_id: hypothesis.hypothesisId,
      hypothesis_version: 1,
      hypothesis_frozen_at_utc: frozenAt,
      source_id: hypothesis.sourceId,
      source_exact_url: hypothesis.sourceExactUrl,
      prediction_id: target.prediction_id,
      cohort: target.cohort,
      issuing_fiscal_period: target.issuing_fiscal_period,
      guided_fiscal_period: target.guided_fiscal_period,
      cutoff_utc: cutoffUtc,
      target_source_id: target.target_source_id,
      target_citation: target.target_citation,
      target_type: target.target_type,
      target_low: target.target_low,
      target_high: target.target_high,
      target_midpoint: target.target_midpoint,
      target_unit: target.target_unit,
      currency: target.currency,
      constant_currency_basis: target.constant_currency_basis,
      frozen_expected_direction: hypothesis.expectedDirection,
      frozen_primary_formula: hypothesis.primaryFormula,
      frozen_sensitivity_formula: hypothesis.sensitivityFormula,
      source_permission_status: "denied",
      source_request_count: 0,
      source_observation_date: "",
      source_reference_period: "",
      source_initial_publication_utc: "",
      source_revision_or_vintage: "",
      source_feature_value: "",
      source_feature_unit: hypothesis.featureUnit,
      primary_signal_implication: "",
      event_status: eventStatus,
      eligible: false,
      exclusion_reason: exclusionReason,
      missingness: hypothesis.missingness,
      seasonal_baseline_name: "seasonal_naive_same_guided_quarter_prior_year_midpoint",
      seasonal_baseline_prediction_id: seasonal.predictionId,
      seasonal_baseline_value: seasonal.value,
      seasonal_baseline_status: seasonal.status,
      target_change_vs_seasonal: seasonal.delta,
      target_direction_vs_seasonal: seasonal.targetDirection,
      seasonal_replay_classification: "not_testable",
      prior_quarter_baseline_name: "prior_quarter_guidance_midpoint",
      prior_quarter_baseline_prediction_id: prior.predictionId,
      prior_quarter_baseline_value: prior.value,
      prior_quarter_baseline_status: prior.status,
      target_change_vs_prior_quarter: prior.delta,
      target_direction_vs_prior_quarter: prior.targetDirection,
      prior_quarter_replay_classification: "not_testable",
      h001_comparator_status: h001Comparable
        ? "comparable"
        : "not_comparable_target_or_baseline",
      h001_signal_implication: h001Comparable ? h001.implication : "",
      h001_replay_classification: h001Comparable ? h001.classification : "",
      h001_source_replay_path: h001Comparable
        ? `research/readiness/20260903T053309Z_abnb_readiness/${
            String(target.cohort) === "2020q4_2023q2"
              ? "cohort_2020q4_2023q2_replay.csv"
              : "cohort_2023q3_2026q2_replay.csv"
          }`
        : "",
      discrepancies:
        "No supply-source result exists; baseline calculations describe targets only and must not be interpreted as evidence for the frozen signal.",
      leakage_warnings:
        "No current archive index, later replacement file, present-day snapshot, guidance text, transcript content, or post-cutoff information was used as a signal feature.",
      completed_at_utc: completedAt,
    });
  }
}

if (replayRows.length !== 46) {
  throw new Error(`Expected 46 replay rows, found ${replayRows.length}`);
}

const summaryHeaders = [
  "hypothesis_id",
  "source_id",
  "governance_disposition",
  "total_events",
  "excluded_pre_regime_events",
  "not_testable_events",
  "eligible_events",
  "source_requests",
  "seasonal_baseline_available_events",
  "prior_quarter_baseline_available_events",
  "h001_comparable_events",
  "minimum_evidence_status",
  "replay_conclusion",
];

const summaryRows = hypotheses.map((hypothesis) => {
  const rows = replayRows.filter((row) => row.hypothesis_id === hypothesis.hypothesisId);
  const eligible = rows.filter((row) => row.eligible === true).length;
  return {
    hypothesis_id: hypothesis.hypothesisId,
    source_id: hypothesis.sourceId,
    governance_disposition: "INCONCLUSIVE",
    total_events: rows.length,
    excluded_pre_regime_events: rows.filter((row) => row.event_status === "excluded").length,
    not_testable_events: rows.filter((row) => row.event_status === "not_testable").length,
    eligible_events: eligible,
    source_requests: rows.reduce((sum, row) => sum + Number(row.source_request_count), 0),
    seasonal_baseline_available_events: rows.filter(
      (row) => row.seasonal_baseline_status === "available",
    ).length,
    prior_quarter_baseline_available_events: rows.filter(
      (row) => row.prior_quarter_baseline_status === "available",
    ).length,
    h001_comparable_events: rows.filter(
      (row) => row.h001_comparator_status === "comparable",
    ).length,
    minimum_evidence_status:
      hypothesis.hypothesisId === "H-005"
        ? "failed_not_testable: 0 eligible vs minimum 12"
        : "failed_not_testable: 0 eligible post-regime events vs minimum 8 and 0 consecutive snapshot transitions vs minimum 4",
    replay_conclusion:
      "NOT_TESTABLE: permission gate denied and no lawful source observations exist; no hit/miss or predictive inference is permitted.",
  };
});

const replayCsv = toCsv(replayHeaders, replayRows);
const summaryCsv = toCsv(summaryHeaders, summaryRows);
await fs.writeFile(path.join(outputDir, "postfreeze_event_replay.csv"), replayCsv, "utf8");
await fs.writeFile(path.join(outputDir, "postfreeze_replay_summary.csv"), summaryCsv, "utf8");

const workbook = await Workbook.fromCSV(replayCsv, { sheetName: "Replay" });
await workbook.fromCSV(summaryCsv, { sheetName: "Summary" });

const replaySheet = workbook.worksheets.getItem("Replay");
const summarySheet = workbook.worksheets.getItem("Summary");
for (const sheet of [replaySheet, summarySheet]) {
  sheet.showGridLines = false;
  sheet.freezePanes.freezeRows(1);
  const used = sheet.getUsedRange();
  used.format.font = { name: "Arial", size: 9, color: "#000000" };
  used.format.verticalAlignment = "top";
  used.format.wrapText = true;
  used.format.borders = {
    insideHorizontal: { style: "thin", color: "#D9E2F3" },
    bottom: { style: "thin", color: "#A6A6A6" },
  };
  const header = used.getRow(0);
  header.format.fill = "#17365D";
  header.format.font = { name: "Arial", size: 9, bold: true, color: "#FFFFFF" };
  header.format.rowHeight = 34;
}
replaySheet.freezePanes.freezeColumns(7);
replaySheet.getUsedRange().format.rowHeight = 42;
replaySheet.getRange("A:A").format.columnWidth = 28;
replaySheet.getRange("B:F").format.columnWidth = 20;
replaySheet.getRange("G:M").format.columnWidth = 22;
replaySheet.getRange("D2:D47").setNumberFormat("yyyy-mm-dd hh:mm:ss");
replaySheet.getRange("K2:K47").setNumberFormat("yyyy-mm-dd hh:mm:ss");
replaySheet.getRange("BE2:BE47").setNumberFormat("yyyy-mm-dd hh:mm:ss");
replaySheet.getRange("N:U").format.columnWidth = 16;
replaySheet.getRange("V:W").format.columnWidth = 54;
replaySheet.getRange("X:AF").format.columnWidth = 20;
replaySheet.getRange("AG:AJ").format.columnWidth = 48;
replaySheet.getRange("AK:AX").format.columnWidth = 24;
replaySheet.getRange("AY:BE").format.columnWidth = 28;
summarySheet.getUsedRange().format.rowHeight = 46;
summarySheet.getRange("A:C").format.columnWidth = 28;
summarySheet.getRange("D:K").format.columnWidth = 18;
summarySheet.getRange("L:M").format.columnWidth = 58;

const summaryInspect = await workbook.inspect({
  kind: "table",
  sheetId: "Summary",
  range: "A1:M3",
  include: "values,formulas",
  tableMaxRows: 3,
  tableMaxCols: 13,
  maxChars: 8000,
});
console.log(summaryInspect.ndjson);
const replayInspect = await workbook.inspect({
  kind: "table",
  sheetId: "Replay",
  range: "A1:N8",
  include: "values,formulas",
  tableMaxRows: 8,
  tableMaxCols: 14,
  maxChars: 8000,
});
console.log(replayInspect.ndjson);
const formulaErrors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
});
console.log(formulaErrors.ndjson);

const summaryPreview = await workbook.render({
  sheetName: "Summary",
  range: "A1:M3",
  scale: 1,
  format: "png",
});
await fs.mkdir(path.join(outputDir, ".artifact_tool"), { recursive: true });
await fs.writeFile(
  path.join(outputDir, ".artifact_tool/summary_preview.png"),
  new Uint8Array(await summaryPreview.arrayBuffer()),
);
const replayPreview = await workbook.render({
  sheetName: "Replay",
  range: "A1:N8",
  scale: 1,
  format: "png",
});
await fs.writeFile(
  path.join(outputDir, ".artifact_tool/replay_preview.png"),
  new Uint8Array(await replayPreview.arrayBuffer()),
);

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(path.join(outputDir, "postfreeze_event_replay.xlsx"));

console.log(
  JSON.stringify({
    replayRows: replayRows.length,
    summaryRows: summaryRows.length,
    h001Rows: h001ByPrediction.size,
    outputs: [
      "postfreeze_event_replay.csv",
      "postfreeze_replay_summary.csv",
      "postfreeze_event_replay.xlsx",
    ],
  }),
);
