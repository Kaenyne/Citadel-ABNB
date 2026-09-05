import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadArtifactTool } from "../../../../scripts/artifact_tool_runtime.mjs";

const { SpreadsheetFile, Workbook } = await loadArtifactTool();

const runDir = path.dirname(fileURLToPath(import.meta.url));
const repoDir = path.resolve(runDir, "../../../..");
const outputDir = path.join(repoDir, "outputs", "workbooks");
const outputPath = path.join(outputDir, "abnb_us_europe_guidance_comparison.xlsx");
const previewDir = path.join(runDir, "previews");
const inputs = JSON.parse(await fs.readFile(path.join(runDir, "workbook_inputs.json"), "utf8"));

const colors = {
  navy: "#14213D",
  blue: "#1F4E78",
  mediumBlue: "#4472C4",
  lightBlue: "#DCE6F1",
  teal: "#2A9D8F",
  lightTeal: "#D9EAD3",
  orange: "#F4A261",
  paleOrange: "#FCE5CD",
  paleYellow: "#FFF2CC",
  paleRed: "#F4CCCC",
  gray: "#E7E6E6",
  darkGray: "#666666",
  white: "#FFFFFF",
  black: "#000000",
  green: "#008000",
};

function valueOrNull(value) {
  if (value === null || value === undefined || value === "") return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function titleBlock(sheet, title, subtitle, lastColumn) {
  sheet.showGridLines = false;
  sheet.mergeCells(`A1:${lastColumn}2`);
  sheet.getRange("A1").values = [[title]];
  sheet.getRange(`A1:${lastColumn}2`).format = {
    fill: colors.navy,
    font: { bold: true, color: colors.white, size: 18 },
    verticalAlignment: "center",
  };
  sheet.mergeCells(`A3:${lastColumn}3`);
  sheet.getRange("A3").values = [[subtitle]];
  sheet.getRange(`A3:${lastColumn}3`).format = {
    fill: colors.lightBlue,
    font: { color: colors.navy, italic: true, size: 10 },
    wrapText: true,
    verticalAlignment: "center",
  };
  sheet.getRange("1:1").format.rowHeight = 25;
  sheet.getRange("2:2").format.rowHeight = 25;
  sheet.getRange("3:3").format.rowHeight = 32;
}

function tableHeader(range) {
  range.format = {
    fill: colors.blue,
    font: { bold: true, color: colors.white },
    wrapText: true,
    verticalAlignment: "center",
    borders: { preset: "outside", style: "thin", color: colors.navy },
  };
}

function sectionHeader(sheet, address, text) {
  sheet.mergeCells(address);
  sheet.getRange(address.split(":")[0]).values = [[text]];
  sheet.getRange(address).format = {
    fill: colors.blue,
    font: { bold: true, color: colors.white },
    verticalAlignment: "center",
  };
}

const workbook = Workbook.create();
const dashboard = workbook.worksheets.add("Dashboard");
const guidanceSheet = workbook.worksheets.add("Guidance History");
const eventSheet = workbook.worksheets.add("Event Panel");
const comparisonSheet = workbook.worksheets.add("Comparison");
const revenueWeightSheet = workbook.worksheets.add("Revenue Weights");
const usabilitySheet = workbook.worksheets.add("Usability Score");
const observationSheet = workbook.worksheets.add("Observations");
const sourceSheet = workbook.worksheets.add("Source & Permissions");
const methodologySheet = workbook.worksheets.add("Methodology");
const checksSheet = workbook.worksheets.add("Checks");

// Guidance history: formula-driven seasonal comparison.
titleBlock(
  guidanceSheet,
  "Airbnb revenue-guidance history",
  "Twenty-three guidance events. Year-over-year growth is computed against the midpoint for the same guided quarter one year earlier.",
  "Q",
);
const guidanceHeaders = [
  "Event #", "Prediction ID", "Issuing quarter", "Guided quarter", "Available at (UTC)", "Target type",
  "Low ($mm)", "High ($mm)", "Midpoint ($mm)", "Range width ($mm)", "Prior-year guided quarter",
  "Prior-year midpoint ($mm)", "Guidance YoY growth", "Sequential acceleration", "Source ID", "Source URL", "Notes",
];
guidanceSheet.getRange("A6:Q6").values = [guidanceHeaders];
tableHeader(guidanceSheet.getRange("A6:Q6"));
const guidanceStart = 7;
const guidanceEnd = guidanceStart + inputs.guidance.length - 1;
guidanceSheet.getRange(`A${guidanceStart}:Q${guidanceEnd}`).values = inputs.guidance.map((row) => [
  Number(row.event_index), row.prediction_id, row.issuing_fiscal_period, row.guided_fiscal_period,
  new Date(row.guidance_available_at_utc), row.target_type, valueOrNull(row.target_low), valueOrNull(row.target_high),
  valueOrNull(row.target_midpoint), null, null, null, null, null, row.target_source_id, row.target_citation, row.notes,
]);
guidanceSheet.getRange(`J${guidanceStart}:J${guidanceEnd}`).formulas = inputs.guidance.map((_, index) => {
  const row = guidanceStart + index;
  return [`=IF(OR(G${row}="",H${row}=""),"",H${row}-G${row})`];
});
guidanceSheet.getRange(`K${guidanceStart}:K${guidanceEnd}`).formulas = inputs.guidance.map((_, index) => {
  const row = guidanceStart + index;
  return [`=(VALUE(LEFT(D${row},4))-1)&RIGHT(D${row},2)`];
});
guidanceSheet.getRange(`L${guidanceStart}:L${guidanceEnd}`).formulas = inputs.guidance.map((_, index) => {
  const row = guidanceStart + index;
  return [`=IFERROR(INDEX($I$${guidanceStart}:$I$${guidanceEnd},MATCH(K${row},$D$${guidanceStart}:$D$${guidanceEnd},0)),"")`];
});
guidanceSheet.getRange(`M${guidanceStart}:M${guidanceEnd}`).formulas = inputs.guidance.map((_, index) => {
  const row = guidanceStart + index;
  return [`=IF(OR(I${row}="",L${row}=""),"",I${row}/L${row}-1)`];
});
guidanceSheet.getRange(`N${guidanceStart}:N${guidanceEnd}`).formulas = inputs.guidance.map((_, index) => {
  const row = guidanceStart + index;
  if (index === 0) return ["=\"\""];
  return [`=IF(OR(M${row}="",M${row - 1}=""),"",M${row}-M${row - 1})`];
});
guidanceSheet.getRange(`E${guidanceStart}:E${guidanceEnd}`).format.numberFormat = "yyyy-mm-dd hh:mm";
guidanceSheet.getRange(`G${guidanceStart}:L${guidanceEnd}`).format.numberFormat = "$#,##0;[Red]($#,##0);-";
guidanceSheet.getRange(`M${guidanceStart}:N${guidanceEnd}`).format.numberFormat = "0.0%;[Red](0.0%);-";
guidanceSheet.getRange(`O${guidanceStart}:Q${guidanceEnd}`).format.font = { color: colors.darkGray, size: 9 };
guidanceSheet.getRange(`A6:Q${guidanceEnd}`).format.wrapText = true;
guidanceSheet.tables.add(`A6:Q${guidanceEnd}`, true, "GuidanceHistoryTable").style = "TableStyleMedium2";
guidanceSheet.freezePanes.freezeRows(6);
guidanceSheet.freezePanes.freezeColumns(4);
[9, 25, 13, 13, 20, 15, 12, 12, 14, 14, 20, 16, 15, 17, 14, 48, 58].forEach((width, index) => {
  guidanceSheet.getRangeByIndexes(0, index, guidanceEnd, 1).format.columnWidth = width;
});

// Long event-aligned feature panel.
titleBlock(
  eventSheet,
  "Event-aligned U.S. and European signals",
  "The primary composite uses the latest U.S./EMEA revenue mix available before each guidance event. Feature lags remain diagnostic assumptions, not historical publication proof.",
  "Y",
);
const eventHeaders = [
  "Event #", "Prediction ID", "Issuing quarter", "Guided quarter", "Guidance cutoff (UTC)", "Midpoint ($mm)",
  "Guidance YoY", "Guidance acceleration", "Feature ID", "Feature value", "Feature change", "Feature reference period",
  "Assumed diagnostic availability", "Diagnostic value available", "Strict PIT eligible", "Direction match", "Evidence status", "Interpretation",
  "Weight fiscal year", "U.S. revenue ($mm)", "EMEA revenue ($mm)", "U.S. weight", "EMEA weight", "Weight available (UTC)", "Weight source URL",
];
eventSheet.getRange("A6:Y6").values = [eventHeaders];
tableHeader(eventSheet.getRange("A6:Y6"));
const eventStart = 7;
const eventEnd = eventStart + inputs.events.length - 1;
eventSheet.getRange(`A${eventStart}:Y${eventEnd}`).values = inputs.events.map((row) => [
  Number(row.event_index), row.prediction_id, row.issuing_fiscal_period, row.guided_fiscal_period,
  new Date(row.guidance_cutoff_utc), valueOrNull(row.guidance_midpoint_usd_mm), valueOrNull(row.guidance_yoy_growth),
  valueOrNull(row.guidance_acceleration_pp), row.feature_id, valueOrNull(row.feature_value), valueOrNull(row.feature_change_pp),
  row.feature_reference_period, row.assumed_availability_utc_for_diagnostic ? new Date(row.assumed_availability_utc_for_diagnostic) : null,
  row.diagnostic_eligible === "true", row.strict_pit_eligible === "true", row.acceleration_direction_match === "" ? null : row.acceleration_direction_match === "true",
  row.evidence_status, "Current-snapshot diagnostic only; not approved forecast evidence.",
  row.weight_fiscal_year === "" ? null : Number(row.weight_fiscal_year), valueOrNull(row.us_revenue_usd_mm), valueOrNull(row.emea_revenue_usd_mm),
  valueOrNull(row.us_weight), valueOrNull(row.emea_weight), row.weight_available_at_utc ? new Date(row.weight_available_at_utc) : null, row.weight_source_url,
]);
eventSheet.getRange(`E${eventStart}:E${eventEnd}`).format.numberFormat = "yyyy-mm-dd hh:mm";
eventSheet.getRange(`M${eventStart}:M${eventEnd}`).format.numberFormat = "yyyy-mm-dd";
eventSheet.getRange(`F${eventStart}:F${eventEnd}`).format.numberFormat = "$#,##0";
eventSheet.getRange(`G${eventStart}:K${eventEnd}`).format.numberFormat = "0.0%;[Red](0.0%);-";
eventSheet.getRange(`T${eventStart}:U${eventEnd}`).format.numberFormat = "$#,##0";
eventSheet.getRange(`V${eventStart}:W${eventEnd}`).format.numberFormat = "0.0%";
eventSheet.getRange(`X${eventStart}:X${eventEnd}`).format.numberFormat = "yyyy-mm-dd hh:mm";
eventSheet.getRange(`O${eventStart}:O${eventEnd}`).format.fill = colors.paleRed;
eventSheet.getRange(`Q${eventStart}:R${eventEnd}`).format.fill = colors.paleYellow;
eventSheet.getRange(`S${eventStart}:Y${eventEnd}`).format.fill = "#EEF5FB";
eventSheet.getRange(`A6:Y${eventEnd}`).format.wrapText = true;
eventSheet.tables.add(`A6:Y${eventEnd}`, true, "EventPanelTable").style = "TableStyleMedium2";
eventSheet.freezePanes.freezeRows(6);
eventSheet.freezePanes.freezeColumns(4);
[9, 25, 13, 13, 20, 14, 14, 18, 30, 14, 14, 26, 22, 18, 16, 16, 34, 52, 14, 16, 17, 13, 13, 22, 56].forEach((width, index) => {
  eventSheet.getRangeByIndexes(0, index, eventEnd, 1).format.columnWidth = width;
});

// Comparison summary, sorted by descriptive level relationship.
titleBlock(
  comparisonSheet,
  "Descriptive comparison against Airbnb guidance",
  "These correlations use current snapshots retroactively aligned with fixed lags. Ranking is for hypothesis prioritization—not a backtest, alpha claim, or model-selection result.",
  "O",
);
const comparisonHeaders = [
  "Descriptive rank", "Feature ID", "Feature", "Diagnostic events", "Strict PIT events", "Level n", "Level Pearson",
  "Level Spearman", "Acceleration n", "Acceleration Pearson", "Acceleration Spearman", "Direction n",
  "Direction concordance", "What it says", "Next research use",
];
comparisonSheet.getRange("A6:O6").values = [comparisonHeaders];
tableHeader(comparisonSheet.getRange("A6:O6"));
const decisionByFeature = {
  US_SFO_T3M_YOY: [
    "Highest guidance-level relationship in this sample; acceleration relationship is negative and direction agreement is only modest.",
    "Keep as the U.S. activity anchor, then add a second independently governed airport before calling it a U.S. breadth factor.",
  ],
  US_EU_50_50_COMPOSITE: [
    "Equal weighting is retained only as a benchmark; it is not Airbnb's disclosed geographic mix.",
    "Use only as the control against the point-in-time revenue-weighted specification.",
  ],
  US_EMEA_REVENUE_WEIGHTED_COMPOSITE: [
    "Narrowly highest level Pearson, but the gain versus both 50/50 and SFO is immaterial; rank and acceleration tests do not improve.",
    "Use as the economically correct primary specification, then validate prospectively rather than claiming new edge.",
  ],
  EU_PLATFORM_T3M_YOY: [
    "Strongest independent accommodation-native signal; distinct from general tourism nights.",
    "Prioritize prospective archiving because this is closest to Airbnb's platform accommodation mechanism.",
  ],
  EU_TOURISM_T3M_YOY: [
    "Weak guidance-level relationship in a shorter nine-event sample.",
    "Use as a macro tourism control, not the primary predictor.",
  ],
  EU_PLATFORM_MINUS_TOURISM: [
    "Negative relationship in a short sample; may represent platform-share mix rather than revenue growth.",
    "Treat as a regime/mix diagnostic and preregister its expected sign before testing.",
  ],
};
const orderedComparisons = [...inputs.comparisons].sort((a, b) => (valueOrNull(b.guidance_level_pearson) ?? -99) - (valueOrNull(a.guidance_level_pearson) ?? -99));
const comparisonStart = 7;
const comparisonEnd = comparisonStart + orderedComparisons.length - 1;
comparisonSheet.getRange(`A${comparisonStart}:O${comparisonEnd}`).values = orderedComparisons.map((row, index) => [
  index + 1, row.feature_id, row.feature_label, Number(row.diagnostic_event_count), Number(row.strict_pit_event_count),
  Number(row.guidance_level_n), valueOrNull(row.guidance_level_pearson), valueOrNull(row.guidance_level_spearman),
  Number(row.guidance_acceleration_n), valueOrNull(row.guidance_acceleration_pearson), valueOrNull(row.guidance_acceleration_spearman),
  Number(row.direction_test_n), valueOrNull(row.acceleration_direction_concordance), decisionByFeature[row.feature_id][0], decisionByFeature[row.feature_id][1],
]);
comparisonSheet.getRange(`G${comparisonStart}:M${comparisonEnd}`).format.numberFormat = "0.00;[Red](0.00);-";
comparisonSheet.getRange(`M${comparisonStart}:M${comparisonEnd}`).format.numberFormat = "0%";
comparisonSheet.getRange(`E${comparisonStart}:E${comparisonEnd}`).format.fill = colors.paleRed;
comparisonSheet.getRange(`G${comparisonStart}:G${comparisonEnd}`).conditionalFormats.add("colorScale", {
  colors: [colors.paleRed, colors.paleYellow, colors.lightTeal],
});
comparisonSheet.getRange(`A6:O${comparisonEnd}`).format.wrapText = true;
comparisonSheet.getRange(`${comparisonStart}:${comparisonEnd}`).format.rowHeight = 62;
comparisonSheet.tables.add(`A6:O${comparisonEnd}`, true, "ComparisonTable").style = "TableStyleMedium2";
comparisonSheet.freezePanes.freezeRows(6);
[14, 30, 58, 17, 16, 11, 14, 15, 15, 20, 21, 12, 20, 62, 66].forEach((width, index) => {
  comparisonSheet.getRangeByIndexes(0, index, comparisonEnd, 1).format.columnWidth = width;
});

// Official Airbnb revenue weights, kept point-in-time by filing acceptance timestamp.
titleBlock(
  revenueWeightSheet,
  "Point-in-time U.S. / EMEA revenue weights",
  "Airbnb does not disclose Europe-only revenue. EMEA is the closest official proxy; weights are normalized within the two modeled sleeves and never fitted to guidance outcomes.",
  "J",
);
const weightHeaders = [
  "Fiscal year", "10-K accepted (UTC)", "U.S. revenue ($mm)", "EMEA revenue ($mm)", "Total revenue ($mm)",
  "U.S. sleeve weight", "EMEA sleeve weight", "Covered revenue share", "Scope", "Official filing",
];
revenueWeightSheet.getRange("A6:J6").values = [weightHeaders];
tableHeader(revenueWeightSheet.getRange("A6:J6"));
const weightStart = 7;
const weightEnd = weightStart + inputs.revenue_weights.length - 1;
revenueWeightSheet.getRange(`A${weightStart}:J${weightEnd}`).values = inputs.revenue_weights.map((row) => [
  Number(row.fiscal_year), new Date(row.accepted_at_utc), valueOrNull(row.us_revenue_usd_mm), valueOrNull(row.emea_revenue_usd_mm),
  valueOrNull(row.total_revenue_usd_mm), null, null, null, row.weight_scope, row.source_url,
]);
revenueWeightSheet.getRange(`F${weightStart}:F${weightEnd}`).formulas = inputs.revenue_weights.map((_, index) => {
  const row = weightStart + index;
  return [`=C${row}/(C${row}+D${row})`];
});
revenueWeightSheet.getRange(`G${weightStart}:G${weightEnd}`).formulas = inputs.revenue_weights.map((_, index) => {
  const row = weightStart + index;
  return [`=D${row}/(C${row}+D${row})`];
});
revenueWeightSheet.getRange(`H${weightStart}:H${weightEnd}`).formulas = inputs.revenue_weights.map((_, index) => {
  const row = weightStart + index;
  return [`=(C${row}+D${row})/E${row}`];
});
revenueWeightSheet.getRange(`B${weightStart}:B${weightEnd}`).format.numberFormat = "yyyy-mm-dd hh:mm";
revenueWeightSheet.getRange(`C${weightStart}:E${weightEnd}`).format.numberFormat = "$#,##0";
revenueWeightSheet.getRange(`F${weightStart}:H${weightEnd}`).format.numberFormat = "0.0%";
revenueWeightSheet.getRange(`F${weightStart}:H${weightEnd}`).format.fill = colors.lightTeal;
revenueWeightSheet.getRange(`A6:J${weightEnd}`).format.wrapText = true;
revenueWeightSheet.tables.add(`A6:J${weightEnd}`, true, "RevenueWeightTable").style = "TableStyleMedium2";
revenueWeightSheet.freezePanes.freezeRows(6);
[13, 22, 19, 20, 19, 18, 19, 21, 64, 62].forEach((width, index) => {
  revenueWeightSheet.getRangeByIndexes(0, index, weightEnd, 1).format.columnWidth = width;
});

// Auditable usability score: research usefulness, not forecast approval.
titleBlock(
  usabilitySheet,
  "Revenue-weighted composite usability score",
  "A fixed six-part rubric separates economic relevance from evidence quality. Point-in-time integrity carries the largest weight and currently scores zero.",
  "G",
);
sectionHeader(usabilitySheet, "A5:G5", "Weighted scorecard");
usabilitySheet.getRange("A7:E7").values = [["Dimension", "Weight", "Score (0–10)", "Weighted points", "Evidence"]];
tableHeader(usabilitySheet.getRange("A7:E7"));
const usabilityStart = 8;
const usabilityEnd = usabilityStart + inputs.usability.dimensions.length - 1;
usabilitySheet.getRange(`A${usabilityStart}:E${usabilityEnd}`).values = inputs.usability.dimensions.map((row) => [
  row.dimension, valueOrNull(row.weight), valueOrNull(row.score), null, row.evidence,
]);
usabilitySheet.getRange(`D${usabilityStart}:D${usabilityEnd}`).formulas = inputs.usability.dimensions.map((_, index) => {
  const row = usabilityStart + index;
  return [`=B${row}*C${row}`];
});
usabilitySheet.getRange(`B${usabilityStart}:B${usabilityEnd}`).format.numberFormat = "0%";
usabilitySheet.getRange(`C${usabilityStart}:D${usabilityEnd}`).format.numberFormat = "0.0";
usabilitySheet.getRange(`A7:E${usabilityEnd}`).format.wrapText = true;
usabilitySheet.tables.add(`A7:E${usabilityEnd}`, true, "UsabilityScoreTable").style = "TableStyleMedium2";
usabilitySheet.getRange("A15:E17").values = [
  ["Total usability score", null, "/10", null, null],
  ["Rating", inputs.usability.rating, null, null, null],
  ["Forecast deployment gate", inputs.usability.forecast_deployment_gate, null, null, null],
];
usabilitySheet.getRange("B15").formulas = [[`=SUM(D${usabilityStart}:D${usabilityEnd})`]];
usabilitySheet.getRange("B15").format.numberFormat = "0.0";
usabilitySheet.getRange("A15:A17").format = { fill: colors.blue, font: { bold: true, color: colors.white } };
usabilitySheet.getRange("B15:E16").format = { fill: colors.paleYellow, font: { bold: true, color: colors.navy } };
usabilitySheet.getRange("B17:E17").format = { fill: colors.paleRed, font: { bold: true, color: colors.navy } };
sectionHeader(usabilitySheet, "A20:G20", "Observed diagnostic test");
const weightedMetric = inputs.comparisons.find((row) => row.feature_id === "US_EMEA_REVENUE_WEIGHTED_COMPOSITE");
usabilitySheet.getRange("A22:B28").values = [
  ["Metric", "Result"],
  ["Guidance-level Pearson", valueOrNull(weightedMetric.guidance_level_pearson)],
  ["Guidance-level Spearman", valueOrNull(weightedMetric.guidance_level_spearman)],
  ["Pearson delta vs 50/50", valueOrNull(inputs.usability.delta_vs_50_50_pearson)],
  ["Pearson delta vs SFO", valueOrNull(inputs.usability.delta_vs_sfo_pearson)],
  ["Acceleration Pearson", valueOrNull(weightedMetric.guidance_acceleration_pearson)],
  ["Direction concordance", valueOrNull(weightedMetric.acceleration_direction_concordance)],
];
tableHeader(usabilitySheet.getRange("A22:B22"));
usabilitySheet.getRange("B23:B28").format.numberFormat = "0.000;[Red](0.000);-";
usabilitySheet.getRange("B28").format.numberFormat = "0.0%";
usabilitySheet.getRange("A1:G28").format.wrapText = true;
[31, 25, 17, 20, 86, 4, 4].forEach((width, index) => {
  usabilitySheet.getRangeByIndexes(0, index, 28, 1).format.columnWidth = width;
});
usabilitySheet.freezePanes.freezeRows(7);

// Compiled observation dataset.
titleBlock(
  observationSheet,
  "Compiled U.S. and European observations",
  "A normalized 525-row research dataset: SFO airport passengers plus EU27 collaborative-platform and total-tourism nights.",
  "P",
);
const observationHeaders = [
  "Observation ID", "Source ID", "Provider", "Region", "Geography", "Reference period", "Metric", "Segment 1",
  "Segment 2", "Value", "Unit", "Observed first available", "Source loaded at", "Collected at", "Included in feature", "PIT treatment",
];
observationSheet.getRange("A6:P6").values = [observationHeaders];
tableHeader(observationSheet.getRange("A6:P6"));
const observationStart = 7;
const observationEnd = observationStart + inputs.observations.length - 1;
observationSheet.getRange(`A${observationStart}:P${observationEnd}`).values = inputs.observations.map((row) => [
  row.observation_id, row.source_id, row.provider, row.region_family, row.geography, row.reference_period, row.metric,
  row.segment_1, row.segment_2, valueOrNull(row.value), row.unit, row.observed_first_available_at_utc,
  row.source_loaded_at_utc, row.collection_timestamp_utc, row.included_in_feature === "true", row.pit_treatment,
]);
observationSheet.getRange(`J${observationStart}:J${observationEnd}`).format.numberFormat = "#,##0";
observationSheet.getRange(`L${observationStart}:N${observationEnd}`).format.numberFormat = "yyyy-mm-dd hh:mm";
observationSheet.getRange(`P${observationStart}:P${observationEnd}`).format.fill = colors.paleYellow;
observationSheet.getRange(`A6:P${observationEnd}`).format.wrapText = true;
observationSheet.tables.add(`A6:P${observationEnd}`, true, "ObservationTable").style = "TableStyleMedium2";
observationSheet.freezePanes.freezeRows(6);
observationSheet.freezePanes.freezeColumns(2);
[22, 34, 29, 16, 42, 16, 38, 18, 27, 15, 15, 23, 23, 23, 18, 36].forEach((width, index) => {
  observationSheet.getRangeByIndexes(0, index, observationEnd, 1).format.columnWidth = width;
});

// Source permission audit.
titleBlock(
  sourceSheet,
  "Fifteen-source U.S./Europe permission and collection audit",
  "Only approved or previously governed payloads enter the compiled dataset. Blocked and inconclusive sources remain visible with zero rows.",
  "J",
);
const sourceHeaders = [
  "Source ID", "Region", "Provider", "Dataset", "Gate result", "Collection outcome", "Compiled rows", "Strict PIT rows", "Reason", "Source URL",
];
sourceSheet.getRange("A6:J6").values = [sourceHeaders];
tableHeader(sourceSheet.getRange("A6:J6"));
const sourceStart = 7;
const sourceEnd = sourceStart + inputs.sources.length - 1;
sourceSheet.getRange(`A${sourceStart}:J${sourceEnd}`).values = inputs.sources.map((row) => [
  row.source_id, row.region, row.provider, row.dataset, row.gate_result, row.collection_outcome,
  Number(row.compiled_rows), Number(row.strict_pit_rows), row.reason, row.source_url,
]);
sourceSheet.getRange(`G${sourceStart}:H${sourceEnd}`).format.numberFormat = "#,##0";
sourceSheet.getRange(`E${sourceStart}:F${sourceEnd}`).format.fill = colors.paleYellow;
sourceSheet.getRange(`H${sourceStart}:H${sourceEnd}`).format.fill = colors.paleRed;
sourceSheet.getRange(`A6:J${sourceEnd}`).format.wrapText = true;
sourceSheet.tables.add(`A6:J${sourceEnd}`, true, "SourcePermissionTable").style = "TableStyleMedium2";
sourceSheet.freezePanes.freezeRows(6);
sourceSheet.freezePanes.freezeColumns(2);
[34, 16, 36, 54, 24, 32, 14, 14, 72, 58].forEach((width, index) => {
  sourceSheet.getRangeByIndexes(0, index, sourceEnd, 1).format.columnWidth = width;
});

// Methodology and explicit guardrails.
titleBlock(
  methodologySheet,
  "Methodology and evidence controls",
  "The purpose is to prioritize hypotheses for prospective collection while preventing snapshot backfill from being mislabeled as historical forecast evidence.",
  "H",
);
sectionHeader(methodologySheet, "A5:H5", "Predeclared transformations");
methodologySheet.getRange("A7:D12").values = [
  ["Feature", "Transformation", "Diagnostic lag", "Operating bridge"],
  ["U.S. SFO airport activity", "Enplaned + deplaned passengers; trailing 3-month YoY", "60 days", "Realized travel activity → accommodation demand"],
  ["EU27 platform nights", "Collaborative-platform nights; trailing 3-month YoY", "120 days", "Platform accommodation demand → Airbnb nights/revenue"],
  ["EU27 total tourism nights", "All tourist-accommodation nights; trailing 3-month YoY", "60 days", "Macro tourism control"],
  ["Primary U.S.–EMEA composite", "Latest available Airbnb U.S./EMEA revenue weights", "Maximum component lag and filing date", "Official economic mix; normalized within covered sleeves"],
  ["50/50 benchmark", "50% U.S. activity + 50% EU platform nights", "Maximum component lag", "Control only; never weighted by row count"],
];
tableHeader(methodologySheet.getRange("A7:D7"));
sectionHeader(methodologySheet, "A14:H14", "Guidance comparison");
methodologySheet.getRange("A16:B20").values = [
  ["Measure", "Definition"],
  ["Guidance-growth level", "Current guided-quarter midpoint / same guided quarter one year earlier − 1"],
  ["Guidance acceleration", "Current guidance-growth level − prior event guidance-growth level"],
  ["Direction concordance", "Sign of feature change agrees with sign of guidance acceleration"],
  ["Statistics", "Fixed Pearson, Spearman, and direction concordance; no tuning or search"],
];
tableHeader(methodologySheet.getRange("A16:B16"));
sectionHeader(methodologySheet, "A23:H23", "Evidence status");
methodologySheet.getRange("A25:B31").values = [
  ["Control", "Treatment"],
  ["Historical availability", "Observed provider first-availability timestamp must be strictly earlier than the guidance cutoff"],
  ["Current snapshots", "Diagnostic/prospective only; historical reference dates do not create historical vintages"],
  ["Assumed lag", "Used only to prevent reference-period look-ahead in descriptive alignment; it is not publication evidence"],
  ["Strict PIT result", "Zero event-feature rows qualify"],
  ["Model status", "HYPOTHESIS PRIORITIZATION ONLY — NOT APPROVED FOR FORECASTING"],
  ["Next evidence step", "Archive immutable releases prospectively, then run a preregistered walk-forward comparison"],
];
tableHeader(methodologySheet.getRange("A25:B25"));
methodologySheet.getRange("B29:B30").format = { fill: colors.paleRed, font: { bold: true, color: colors.navy } };
methodologySheet.getRange("A7:D31").format.wrapText = true;
methodologySheet.getRange("A:A").format.columnWidth = 31;
methodologySheet.getRange("B:B").format.columnWidth = 78;
methodologySheet.getRange("C:C").format.columnWidth = 22;
methodologySheet.getRange("D:D").format.columnWidth = 58;
methodologySheet.getRange("E:H").format.columnWidth = 4;
methodologySheet.freezePanes.freezeRows(5);

// Visible validation checks.
titleBlock(checksSheet, "Workbook validation checks", "All checks should be OK. The zero strict-PIT count is an expected evidence-control result.", "G");
checksSheet.getRange("A5:G5").values = [["Check", "Actual", "Expected", "Difference", "Tolerance", "Status", "Notes"]];
tableHeader(checksSheet.getRange("A5:G5"));
checksSheet.getRange("A6:G13").values = [
  ["Source candidates", null, 15, null, 0, null, "Fifteen U.S./Europe source candidates are visible"],
  ["Compiled observations", null, 525, null, 0, null, "384 U.S. rows + 141 European rows"],
  ["Guidance events", null, 23, null, 0, null, "Canonical guidance history"],
  ["Event-feature rows", null, 138, null, 0, null, "23 events × six fixed evaluated features"],
  ["Feature specifications", null, 6, null, 0, null, "No in-sample feature search"],
  ["Strict PIT event-feature rows", null, 0, null, 0, null, "Expected zero for current snapshots"],
  ["Numeric guidance events", null, 20, null, 0, null, "Three qualitative events remain blank"],
  ["Revenue-weight vintages", null, 5, null, 0, null, "FY2021–FY2025 official filings"],
];
checksSheet.getRange("B6:B13").formulas = [
  [`=COUNTA('Source & Permissions'!$A$${sourceStart}:$A$${sourceEnd})`],
  [`=COUNTA('Observations'!$A$${observationStart}:$A$${observationEnd})`],
  [`=COUNTA('Guidance History'!$B$${guidanceStart}:$B$${guidanceEnd})`],
  [`=COUNTA('Event Panel'!$A$${eventStart}:$A$${eventEnd})`],
  [`=COUNTA('Comparison'!$B$${comparisonStart}:$B$${comparisonEnd})`],
  [`=COUNTIF('Event Panel'!$O$${eventStart}:$O$${eventEnd},TRUE)`],
  [`=COUNT('Guidance History'!$I$${guidanceStart}:$I$${guidanceEnd})`],
  [`=COUNTA('Revenue Weights'!$A$${weightStart}:$A$${weightEnd})`],
];
checksSheet.getRange("D6:D13").formulas = Array.from({ length: 8 }, (_, index) => [`=B${6 + index}-C${6 + index}`]);
checksSheet.getRange("F6:F13").formulas = Array.from({ length: 8 }, (_, index) => [`=IF(ABS(D${6 + index})<=E${6 + index},"OK","REVIEW")`]);
checksSheet.getRange("A14:E15").values = [["Overall status", null, null, null, null], [null, null, null, null, null]];
checksSheet.mergeCells("A14:E14");
checksSheet.getRange("A14:E14").format = { fill: colors.blue, font: { bold: true, color: colors.white } };
checksSheet.mergeCells("A15:E15");
checksSheet.getRange("A15").formulas = [["=IF(COUNTIF(F6:F13,\"REVIEW\")=0,\"OK — DIAGNOSTIC PANEL VALIDATED / NOT PIT-APPROVED\",\"REVIEW REQUIRED\")"]];
checksSheet.getRange("A15:E15").format = { fill: colors.paleYellow, font: { bold: true, color: colors.navy, size: 12 } };
checksSheet.getRange("B6:B13").format.font = { color: colors.green };
checksSheet.getRange("F6:F13").conditionalFormats.add("containsText", { text: "OK", format: { fill: colors.lightTeal, font: { bold: true, color: colors.navy } } });
checksSheet.getRange("F6:F13").conditionalFormats.add("containsText", { text: "REVIEW", format: { fill: colors.paleRed, font: { bold: true } } });
checksSheet.getRange("A5:G15").format.wrapText = true;
[38, 15, 15, 15, 15, 18, 62].forEach((width, index) => {
  checksSheet.getRangeByIndexes(0, index, 15, 1).format.columnWidth = width;
});

// Dashboard: decision-first presentation.
titleBlock(
  dashboard,
  "ABNB U.S. + Europe alternative-data comparison",
  "Outcome: the point-in-time revenue-weighted U.S./EMEA composite narrowly ranks first, but its gain over 50/50 and SFO is immaterial and does not establish forecasting edge.",
  "Q",
);
const cards = [
  ["A5:C5", "A6:C8", "Sources audited", "='Checks'!B6", colors.lightTeal],
  ["E5:G5", "E6:G8", "Compiled observations", "='Checks'!B7", colors.lightTeal],
  ["I5:K5", "I6:K8", "Usability score / 10", "='Usability Score'!B15", colors.paleYellow],
  ["M5:Q5", "M6:Q8", "Current status", "='Checks'!A15", colors.paleYellow],
];
for (const [labelRange, valueRange, label, formula, fill] of cards) {
  dashboard.mergeCells(labelRange);
  dashboard.getRange(labelRange.split(":")[0]).values = [[label]];
  dashboard.getRange(labelRange).format = { fill: colors.blue, font: { bold: true, color: colors.white } };
  dashboard.mergeCells(valueRange);
  dashboard.getRange(valueRange.split(":")[0]).formulas = [[formula]];
  dashboard.getRange(valueRange).format = {
    fill,
    font: { bold: true, color: colors.green, size: valueRange.startsWith("M") ? 11 : 20 },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
  };
}

sectionHeader(dashboard, "A11:Q11", "Guidance-growth comparison by event");
const eventGroups = new Map();
for (const row of inputs.events) {
  if (row.guidance_yoy_growth === null || row.guidance_yoy_growth === "") continue;
  if (!eventGroups.has(row.prediction_id)) {
    eventGroups.set(row.prediction_id, {
      guided: row.guided_fiscal_period,
      guidance: valueOrNull(row.guidance_yoy_growth),
      features: {},
    });
  }
  eventGroups.get(row.prediction_id).features[row.feature_id] = valueOrNull(row.feature_value);
}
const chartRows = [...eventGroups.values()].map((group) => [
  group.guided,
  group.guidance,
  group.features.US_SFO_T3M_YOY ?? null,
  group.features.EU_PLATFORM_T3M_YOY ?? null,
  group.features.US_EU_50_50_COMPOSITE ?? null,
  group.features.US_EMEA_REVENUE_WEIGHTED_COMPOSITE ?? null,
]);
dashboard.getRange("A13:F13").values = [["Guided quarter", "Guidance YoY", "U.S. SFO YoY", "EU platform YoY", "50/50 benchmark", "Revenue-weighted"]];
tableHeader(dashboard.getRange("A13:F13"));
const chartStart = 14;
const chartEnd = chartStart + chartRows.length - 1;
dashboard.getRange(`A${chartStart}:F${chartEnd}`).values = chartRows;
dashboard.getRange(`B${chartStart}:F${chartEnd}`).format.numberFormat = "0.0%;[Red](0.0%);-";
dashboard.getRange(`A13:F${chartEnd}`).format.wrapText = true;
const trendChart = dashboard.charts.add("line", { chartType: "line", title: "Alt-data growth versus guidance growth", hasLegend: true });
for (const [name, column, color] of [
  ["Guidance YoY", "B", colors.navy],
  ["U.S. SFO YoY", "C", colors.orange],
  ["EU platform YoY", "D", colors.teal],
  ["50/50 benchmark", "E", colors.gray],
  ["Revenue-weighted", "F", colors.mediumBlue],
]) {
  const series = trendChart.series.add(name);
  series.categoryFormula = `'Dashboard'!$A$${chartStart}:$A$${chartEnd}`;
  series.formula = `'Dashboard'!$${column}$${chartStart}:$${column}$${chartEnd}`;
  series.fill = color;
}
trendChart.title = "Alt-data growth versus guidance growth";
trendChart.hasLegend = true;
trendChart.legend = { position: "bottom" };
trendChart.xAxis = { axisType: "textAxis", textStyle: { fontSize: 9 } };
trendChart.yAxis = { numberFormatCode: "0%" };
trendChart.setPosition("G13", "Q31");

sectionHeader(dashboard, "A34:Q34", "What the current sample says");
const best = orderedComparisons[0];
const composite = inputs.comparisons.find((row) => row.feature_id === "US_EMEA_REVENUE_WEIGHTED_COMPOSITE");
const equalComposite = inputs.comparisons.find((row) => row.feature_id === "US_EU_50_50_COMPOSITE");
const platform = inputs.comparisons.find((row) => row.feature_id === "EU_PLATFORM_T3M_YOY");
dashboard.getRange("A36:Q40").values = [
  ["Best level diagnostic", null, `${best.feature_label}: Pearson ${Number(best.guidance_level_pearson).toFixed(2)} across ${best.guidance_level_n} comparable events.`, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
  ["Revenue-weight test", null, `Revenue-weighted Pearson ${Number(composite.guidance_level_pearson).toFixed(3)} versus 50/50 ${Number(equalComposite.guidance_level_pearson).toFixed(3)}; +${Number(inputs.usability.delta_vs_50_50_pearson).toFixed(3)} is immaterial.`, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
  ["Most mechanism-specific", null, `EU platform nights Pearson ${Number(platform.guidance_level_pearson).toFixed(2)}; this is the strongest accommodation-native source family.`, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
  ["Usability verdict", null, `${Number(inputs.usability.total_score).toFixed(1)}/10 — ${inputs.usability.rating}. The zero point-in-time score prevents forecast deployment.`, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
  ["Required next step", null, "Prospectively archive releases, add broader U.S. coverage, and replace EU27 with an EMEA-consistent activity sleeve before judging forecasting power.", null, null, null, null, null, null, null, null, null, null, null, null, null, null],
];
for (let row = 36; row <= 40; row += 1) {
  dashboard.mergeCells(`A${row}:B${row}`);
  dashboard.mergeCells(`C${row}:Q${row}`);
}
dashboard.getRange("A36:B40").format = { fill: colors.paleYellow, font: { bold: true, color: colors.navy } };
dashboard.getRange("C36:Q40").format = { fill: "#FFFDF5", wrapText: true };
dashboard.getRange("A:A").format.columnWidth = 14;
dashboard.getRange("B:F").format.columnWidth = 17;
dashboard.getRange("G:Q").format.columnWidth = 12;
dashboard.getRange("36:40").format.rowHeight = 34;
dashboard.freezePanes.freezeRows(3);

// Compact inspections and formula-error scan before export.
for (const [sheetId, range] of [
  ["Dashboard", "A1:Q40"],
  ["Guidance History", "D6:N18"],
  ["Comparison", `A6:O${comparisonEnd}`],
  ["Revenue Weights", `A6:J${weightEnd}`],
  ["Usability Score", "A7:E28"],
  ["Checks", "A5:G15"],
]) {
  const inspection = await workbook.inspect({
    kind: "table",
    sheetId,
    range,
    include: "values,formulas",
    tableMaxRows: 45,
    tableMaxCols: 18,
    maxChars: 18000,
  });
  console.log(`${sheetId.toUpperCase()}_INSPECT`);
  console.log(inspection.ndjson);
}
const errorInspection = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
console.log("FORMULA_ERROR_SCAN");
console.log(errorInspection.ndjson);

await fs.mkdir(previewDir, { recursive: true });
const previewRanges = {
  Dashboard: "A1:Q40",
  "Guidance History": `A1:Q${guidanceEnd}`,
  "Event Panel": "A1:Y28",
  Comparison: `A1:O${comparisonEnd}`,
  "Revenue Weights": `A1:J${weightEnd}`,
  "Usability Score": "A1:G28",
  Observations: "A1:P26",
  "Source & Permissions": `A1:J${sourceEnd}`,
  Methodology: "A1:H31",
  Checks: "A1:G15",
};
for (const [sheetName, range] of Object.entries(previewRanges)) {
  const preview = await workbook.render({ sheetName, range, scale: 1, format: "png" });
  const safeName = sheetName.toLowerCase().replaceAll(" ", "_").replaceAll("&", "and");
  await fs.writeFile(path.join(previewDir, `${safeName}.png`), new Uint8Array(await preview.arrayBuffer()));
}

await fs.mkdir(outputDir, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(JSON.stringify({ outputPath, sheets: 10, sourceCandidates: inputs.sources.length, observations: inputs.observations.length, events: inputs.guidance.length }));
