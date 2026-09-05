import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadArtifactTool } from "../../../../scripts/artifact_tool_runtime.mjs";

const { SpreadsheetFile, Workbook } = await loadArtifactTool();

const runDir = path.dirname(fileURLToPath(import.meta.url));
const repoDir = path.resolve(runDir, "../../../..");
const outputDir = path.join(repoDir, "outputs", "workbooks");
const outputPath = path.join(outputDir, "abnb_50_source_guidance_comparison.xlsx");
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
  greenLink: "#008000",
};

function numberOrNull(value) {
  if (value === null || value === undefined || value === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
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
    verticalAlignment: "center",
    wrapText: true,
  };
  sheet.getRange("1:1").format.rowHeight = 25;
  sheet.getRange("2:2").format.rowHeight = 25;
  sheet.getRange("3:3").format.rowHeight = 32;
}

function tableHeader(range) {
  range.format = {
    fill: colors.blue,
    font: { bold: true, color: colors.white },
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "outside", style: "thin", color: colors.navy },
  };
}

function sectionHeader(sheet, rangeAddress, text) {
  sheet.mergeCells(rangeAddress);
  const range = sheet.getRange(rangeAddress);
  range.values = [[text]];
  range.format = {
    fill: colors.blue,
    font: { bold: true, color: colors.white },
    verticalAlignment: "center",
  };
}

const workbook = Workbook.create();
const dashboard = workbook.worksheets.add("Dashboard");
const guidanceSheet = workbook.worksheets.add("Guidance History");
const crosswalkSheet = workbook.worksheets.add("Source Crosswalk");
const eligibilitySheet = workbook.worksheets.add("Eligibility Matrix");
const methodologySheet = workbook.worksheets.add("Methodology");
const checksSheet = workbook.worksheets.add("Checks");

// Methodology and visible model assumptions.
titleBlock(
  methodologySheet,
  "ABNB guidance-comparison methodology",
  "The alternative-data feature must forecast the guidance residual—not merely reproduce seasonality in the guidance level.",
  "H",
);
sectionHeader(methodologySheet, "A5:H5", "Scoring weights");
methodologySheet.getRange("A7:C13").values = [
  ["Component", "Weight", "Definition"],
  ["Directness", inputs.weights.directness_score, "Proximity to Airbnb nights, GBV, revenue, or listing supply"],
  ["Timeliness", inputs.weights.timeliness_score, "Release lag relative to an earnings guidance cutoff"],
  ["Frequency", inputs.weights.frequency_score, "Monthly or higher-frequency sources receive more weight"],
  ["Geography", inputs.weights.geography_score, "Breadth and relevance to Airbnb destination markets"],
  ["PIT readiness", inputs.weights.pit_score, "Verified original availability and immutable vintage quality"],
  ["Weight total", null, "Must equal 100%"],
];
methodologySheet.getRange("B13").formulas = [["=SUM(B8:B12)"]];
methodologySheet.getRange("A7:C7").format.fill = colors.blue;
methodologySheet.getRange("A7:C7").format.font = { bold: true, color: colors.white };
methodologySheet.getRange("B8:B13").format.numberFormat = "0%";
methodologySheet.getRange("A13:C13").format.borders = { top: { style: "double", color: colors.navy } };
methodologySheet.getRange("B8:B12").format.font = { color: "#0000FF" };
sectionHeader(methodologySheet, "A15:H15", "Comparison target and bridge");
methodologySheet.getRange("A17:B22").values = [
  ["Stage", "Definition"],
  ["1. Alternative-data feature", "Predeclared, scale-free YoY growth, breadth, mix, or supply measure"],
  ["2. Operating bridge", "Feature → Nights & Experiences Booked / implied ADR → GBV → revenue"],
  ["3. Seasonal baseline", "Revenue-guidance midpoint for the same guided fiscal quarter one year earlier"],
  ["4. Guidance residual", "Current revenue-guidance midpoint less the seasonal baseline midpoint"],
  ["5. Test", "Does the feature improve the signed guidance-residual forecast out of sample?"],
];
tableHeader(methodologySheet.getRange("A17:B17"));
methodologySheet.getRange("A24:H29").values = [
  ["Control", "Required treatment", null, null, null, null, null, null],
  ["Strict cutoff", "first_available_at_utc must be strictly earlier than guidance cutoff", null, null, null, null, null, null],
  ["Manifest approval", "Source must be approved_for_forecasting; discovery status is insufficient", null, null, null, null, null, null],
  ["Historical snapshots", "Current snapshots cannot be presented as original historical vintages", null, null, null, null, null, null],
  ["Feature promotion", "Requires a separate approved walk-forward experiment", null, null, null, null, null, null],
  ["Current state", "FORMAT_READY_NOT_APPROVED_FOR_FORECASTING", null, null, null, null, null, null],
];
methodologySheet.getRange("A24:B24").format = { fill: colors.blue, font: { bold: true, color: colors.white } };
methodologySheet.getRange("B29").format = { fill: colors.paleYellow, font: { bold: true, color: colors.navy } };
methodologySheet.getRange("A:A").format.columnWidth = 25;
methodologySheet.getRange("B:B").format.columnWidth = 75;
methodologySheet.getRange("C:C").format.columnWidth = 72;
methodologySheet.getRange("D:H").format.columnWidth = 3;
methodologySheet.getRange("A7:C29").format.wrapText = true;
methodologySheet.freezePanes.freezeRows(5);

// Canonical guidance history and formula-driven seasonal baseline.
titleBlock(
  guidanceSheet,
  "Airbnb revenue-guidance history",
  "Canonical 23-event target panel. Three early events remain qualitative; no numeric midpoint was invented.",
  "Q",
);
const guidanceHeaders = [
  "Event #", "Prediction ID", "Issuing quarter", "Guided quarter", "Available at (UTC)", "Target type",
  "Low ($mm)", "High ($mm)", "Midpoint ($mm)", "Range width ($mm)", "Prior-year guided quarter",
  "Prior-year midpoint ($mm)", "YoY guidance growth", "Seasonal residual ($mm)", "Source ID", "Source URL", "Notes",
];
guidanceSheet.getRange("A6:Q6").values = [guidanceHeaders];
tableHeader(guidanceSheet.getRange("A6:Q6"));
const guidanceValues = inputs.guidance.map((row) => [
  row.event_index,
  row.prediction_id,
  row.issuing_fiscal_period,
  row.guided_fiscal_period,
  new Date(row.guidance_available_at_utc),
  row.target_type,
  numberOrNull(row.target_low),
  numberOrNull(row.target_high),
  numberOrNull(row.target_midpoint),
  null,
  null,
  null,
  null,
  null,
  row.target_source_id,
  row.target_citation,
  row.notes,
]);
const guidanceStart = 7;
const guidanceEnd = guidanceStart + guidanceValues.length - 1;
guidanceSheet.getRange(`A${guidanceStart}:Q${guidanceEnd}`).values = guidanceValues;
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
  return [`=IF(OR(I${row}="",L${row}=""),"",I${row}-L${row})`];
});
guidanceSheet.getRange(`E${guidanceStart}:E${guidanceEnd}`).format.numberFormat = "yyyy-mm-dd hh:mm";
guidanceSheet.getRange(`G${guidanceStart}:L${guidanceEnd}`).format.numberFormat = "$#,##0;[Red]($#,##0);-";
guidanceSheet.getRange(`M${guidanceStart}:M${guidanceEnd}`).format.numberFormat = "0.0%;[Red](0.0%);-";
guidanceSheet.getRange(`N${guidanceStart}:N${guidanceEnd}`).format.numberFormat = "$#,##0;[Red]($#,##0);-";
guidanceSheet.getRange(`J${guidanceStart}:N${guidanceEnd}`).format.font = { color: colors.black };
guidanceSheet.getRange(`O${guidanceStart}:Q${guidanceEnd}`).format.font = { color: colors.darkGray, size: 9 };
guidanceSheet.getRange(`A6:Q${guidanceEnd}`).format.wrapText = true;
guidanceSheet.tables.add(`A6:Q${guidanceEnd}`, true, "GuidanceHistoryTable").style = "TableStyleMedium2";
guidanceSheet.freezePanes.freezeRows(6);
guidanceSheet.freezePanes.freezeColumns(4);
const guidanceWidths = [9, 25, 13, 13, 20, 15, 12, 12, 14, 14, 20, 16, 15, 18, 14, 48, 55];
guidanceWidths.forEach((width, index) => guidanceSheet.getRangeByIndexes(0, index, guidanceEnd, 1).format.columnWidth = width);

// 50-source crosswalk.
titleBlock(
  crosswalkSheet,
  "50-source guidance crosswalk",
  "Ranked by operating directness, timeliness, frequency, geography, and PIT readiness. Score is a triage score—not measured alpha.",
  "Z",
);
const crosswalkHeaders = [
  "Rank", "Source ID", "Provider", "Dataset", "Family", "Operating bridge", "ABNB KPI", "Guidance target",
  "Proposed transformation", "Expected sign", "Cadence", "Coverage start", "Coverage end", "Valid observations",
  "Directness", "Timeliness", "Frequency", "Geography", "PIT readiness", "Weighted score", "Forecast approval",
  "Historical eligible", "First available (UTC)", "Earliest prospective use", "Caveat", "Source URL",
];
crosswalkSheet.getRange("A6:Z6").values = [crosswalkHeaders];
tableHeader(crosswalkSheet.getRange("A6:Z6"));
const crosswalkStart = 7;
const crosswalkEnd = crosswalkStart + inputs.crosswalk.length - 1;
const crosswalkValues = inputs.crosswalk.map((row) => [
  null,
  row.source_id,
  row.provider,
  row.dataset_name,
  row.family,
  row.operating_bridge,
  row.abnb_kpi,
  row.guidance_target,
  row.proposed_transformation,
  row.expected_sign,
  row.cadence,
  row.coverage_start,
  row.coverage_end,
  row.valid_observations,
  row.directness_score,
  row.timeliness_score,
  row.frequency_score,
  row.geography_score,
  row.pit_score,
  null,
  row.forecast_approval,
  row.historical_eligibility,
  new Date(row.first_available_at_utc),
  row.earliest_prospective_use,
  row.caveat,
  row.source_url,
]);
crosswalkSheet.getRange(`A${crosswalkStart}:Z${crosswalkEnd}`).values = crosswalkValues;
crosswalkSheet.getRange(`A${crosswalkStart}:A${crosswalkEnd}`).formulas = inputs.crosswalk.map((_, index) => {
  const row = crosswalkStart + index;
  return [`=RANK.EQ(T${row},$T$${crosswalkStart}:$T$${crosswalkEnd},0)+COUNTIF($T$${crosswalkStart}:T${row},T${row})-1`];
});
crosswalkSheet.getRange(`T${crosswalkStart}:T${crosswalkEnd}`).formulas = inputs.crosswalk.map((_, index) => {
  const row = crosswalkStart + index;
  return [`=ROUND(O${row}*'Methodology'!$B$8+P${row}*'Methodology'!$B$9+Q${row}*'Methodology'!$B$10+R${row}*'Methodology'!$B$11+S${row}*'Methodology'!$B$12,2)`];
});
crosswalkSheet.getRange(`N${crosswalkStart}:N${crosswalkEnd}`).format.numberFormat = "#,##0";
crosswalkSheet.getRange(`O${crosswalkStart}:S${crosswalkEnd}`).format.numberFormat = "0";
crosswalkSheet.getRange(`T${crosswalkStart}:T${crosswalkEnd}`).format.numberFormat = "0.00";
crosswalkSheet.getRange(`W${crosswalkStart}:W${crosswalkEnd}`).format.numberFormat = "yyyy-mm-dd hh:mm";
crosswalkSheet.getRange(`T${crosswalkStart}:T${crosswalkEnd}`).format.font = { color: colors.greenLink, bold: true };
crosswalkSheet.getRange(`U${crosswalkStart}:U${crosswalkEnd}`).format.fill = colors.paleYellow;
crosswalkSheet.getRange(`V${crosswalkStart}:V${crosswalkEnd}`).format.fill = colors.paleRed;
crosswalkSheet.getRange(`T${crosswalkStart}:T${crosswalkEnd}`).conditionalFormats.add("cellIs", {
  operator: "greaterThanOrEqual",
  formula: 3.5,
  format: { fill: colors.lightTeal, font: { bold: true, color: colors.navy } },
});
crosswalkSheet.getRange(`T${crosswalkStart}:T${crosswalkEnd}`).conditionalFormats.add("cellIs", {
  operator: "lessThan",
  formula: 2.5,
  format: { fill: colors.paleOrange },
});
crosswalkSheet.getRange(`A6:Z${crosswalkEnd}`).format.wrapText = true;
crosswalkSheet.tables.add(`A6:Z${crosswalkEnd}`, true, "SourceCrosswalkTable").style = "TableStyleMedium2";
crosswalkSheet.freezePanes.freezeRows(6);
crosswalkSheet.freezePanes.freezeColumns(2);
const crosswalkWidths = [7, 34, 23, 58, 31, 58, 34, 49, 62, 27, 18, 15, 15, 16, 11, 11, 11, 11, 12, 14, 29, 17, 20, 52, 58, 50];
crosswalkWidths.forEach((width, index) => crosswalkSheet.getRangeByIndexes(0, index, crosswalkEnd, 1).format.columnWidth = width);

// Historical eligibility matrix.
titleBlock(
  eligibilitySheet,
  "Strict point-in-time eligibility matrix",
  "Every source-event pair is retained. False rows are evidence-control results, not missing data to be silently dropped.",
  "P",
);
const eligibilityHeaders = [
  "Prediction ID", "Issuing quarter", "Guided quarter", "Guidance cutoff (UTC)", "Target type", "Midpoint ($mm)",
  "Source rank", "Source ID", "First available (UTC)", "Forecast approval", "Timing pass", "Approval pass",
  "Strictly eligible", "Exclusion reason", "Guidance comparison target", "Expected sign",
];
eligibilitySheet.getRange("A5:P5").values = [eligibilityHeaders];
tableHeader(eligibilitySheet.getRange("A5:P5"));
const eligibilityStart = 6;
const eligibilityEnd = eligibilityStart + inputs.eligibility.length - 1;
const eligibilityValues = inputs.eligibility.map((row) => [
  row.prediction_id,
  row.issuing_fiscal_period,
  row.guided_fiscal_period,
  new Date(row.guidance_cutoff_at_utc),
  row.target_type,
  numberOrNull(row.target_midpoint),
  row.source_rank,
  row.source_id,
  new Date(row.first_available_at_utc),
  row.forecast_approval,
  row.timing_pass,
  row.approval_pass,
  row.strictly_eligible,
  row.exclusion_reason,
  row.guidance_comparison_target,
  row.expected_sign,
]);
eligibilitySheet.getRange(`A${eligibilityStart}:P${eligibilityEnd}`).values = eligibilityValues;
eligibilitySheet.getRange(`D${eligibilityStart}:D${eligibilityEnd}`).format.numberFormat = "yyyy-mm-dd hh:mm";
eligibilitySheet.getRange(`F${eligibilityStart}:F${eligibilityEnd}`).format.numberFormat = "$#,##0;[Red]($#,##0);-";
eligibilitySheet.getRange(`I${eligibilityStart}:I${eligibilityEnd}`).format.numberFormat = "yyyy-mm-dd hh:mm";
eligibilitySheet.getRange(`J${eligibilityStart}:J${eligibilityEnd}`).format.fill = colors.paleYellow;
eligibilitySheet.getRange(`M${eligibilityStart}:M${eligibilityEnd}`).format.fill = colors.paleRed;
eligibilitySheet.getRange(`A5:P${eligibilityEnd}`).format.wrapText = true;
eligibilitySheet.tables.add(`A5:P${eligibilityEnd}`, true, "EligibilityMatrixTable").style = "TableStyleMedium2";
eligibilitySheet.freezePanes.freezeRows(5);
eligibilitySheet.freezePanes.freezeColumns(3);
const eligibilityWidths = [25, 13, 13, 20, 15, 14, 12, 34, 20, 29, 12, 13, 15, 64, 55, 28];
eligibilityWidths.forEach((width, index) => eligibilitySheet.getRangeByIndexes(0, index, eligibilityEnd, 1).format.columnWidth = width);

// Visible checks and model status.
titleBlock(checksSheet, "Workbook checks", "Every check must be OK before the comparison layer is used.", "G");
checksSheet.getRange("A5:G5").values = [["Check", "Actual", "Expected", "Difference", "Tolerance", "Status", "Notes"]];
tableHeader(checksSheet.getRange("A5:G5"));
checksSheet.getRange("A6:G11").values = [
  ["Source count", null, 50, null, 0, null, "Exactly 50 unique source rows"],
  ["Guidance-event count", null, 23, null, 0, null, "Canonical event panel"],
  ["Numeric guidance events", null, 20, null, 0, null, "Three qualitative events remain blank"],
  ["Source-event pairs", null, 1150, null, 0, null, "50 sources × 23 guidance events"],
  ["Strict historical eligible pairs", null, 0, null, 0, null, "Expected zero for current snapshots and discovery-only manifests"],
  ["Scoring-weight total", null, 1, null, 0.000001, null, "Weights must sum to 100%"],
];
checksSheet.getRange("B6:B11").formulas = [
  [`=COUNTA('Source Crosswalk'!$B$${crosswalkStart}:$B$${crosswalkEnd})`],
  [`=COUNTA('Guidance History'!$B$${guidanceStart}:$B$${guidanceEnd})`],
  [`=COUNT('Guidance History'!$I$${guidanceStart}:$I$${guidanceEnd})`],
  [`=COUNTA('Eligibility Matrix'!$A$${eligibilityStart}:$A$${eligibilityEnd})`],
  [`=COUNTIF('Eligibility Matrix'!$M$${eligibilityStart}:$M$${eligibilityEnd},TRUE)`],
  ["='Methodology'!$B$13"],
];
checksSheet.getRange("D6:D11").formulas = [
  ["=B6-C6"], ["=B7-C7"], ["=B8-C8"], ["=B9-C9"], ["=B10-C10"], ["=B11-C11"],
];
checksSheet.getRange("F6:F11").formulas = [
  ["=IF(ABS(D6)<=E6,\"OK\",\"REVIEW\")"],
  ["=IF(ABS(D7)<=E7,\"OK\",\"REVIEW\")"],
  ["=IF(ABS(D8)<=E8,\"OK\",\"REVIEW\")"],
  ["=IF(ABS(D9)<=E9,\"OK\",\"REVIEW\")"],
  ["=IF(ABS(D10)<=E10,\"OK\",\"REVIEW\")"],
  ["=IF(ABS(D11)<=E11,\"OK\",\"REVIEW\")"],
];
checksSheet.getRange("A13:E14").values = [["Overall model status", null, null, null, null], [null, null, null, null, null]];
checksSheet.mergeCells("A13:E13");
checksSheet.getRange("A13:E13").format = { fill: colors.blue, font: { bold: true, color: colors.white } };
checksSheet.mergeCells("A14:E14");
checksSheet.getRange("A14").formulas = [["=IF(COUNTIF(F6:F11,\"REVIEW\")=0,\"OK — FORMAT READY / NOT APPROVED FOR FORECASTING\",\"REVIEW REQUIRED\")"]];
checksSheet.getRange("A14:E14").format = { fill: colors.paleYellow, font: { bold: true, color: colors.navy, size: 12 } };
checksSheet.getRange("B6:B11").format.font = { color: colors.greenLink };
checksSheet.getRange("B11:E11").format.numberFormat = "0.0%";
checksSheet.getRange("F6:F11").conditionalFormats.add("containsText", { text: "OK", format: { fill: colors.lightTeal, font: { bold: true, color: colors.navy } } });
checksSheet.getRange("F6:F11").conditionalFormats.add("containsText", { text: "REVIEW", format: { fill: colors.paleRed, font: { bold: true } } });
checksSheet.getRange("A5:G14").format.wrapText = true;
const checkWidths = [35, 15, 15, 15, 15, 18, 62];
checkWidths.forEach((width, index) => checksSheet.getRangeByIndexes(0, index, 14, 1).format.columnWidth = width);

// Dashboard, formula-linked to the underlying sheets.
titleBlock(
  dashboard,
  "ABNB alternative-data → guidance comparison",
  "Decision target: revenue-guidance residual versus the same guided quarter one year earlier. Current snapshots are formatted but not approved forecast evidence.",
  "T",
);
const cardRanges = ["A5:C7", "E5:G7", "I5:K7", "M5:T7"];
const cardLabels = ["Validated sources", "Guidance events", "Historical eligible pairs", "Model status"];
cardRanges.forEach((address, index) => {
  const [start, end] = address.split(":");
  const startColumn = start.match(/[A-Z]+/)[0];
  const startRow = Number(start.match(/\d+/)[0]);
  const endColumn = end.match(/[A-Z]+/)[0];
  dashboard.mergeCells(`${startColumn}${startRow}:${endColumn}${startRow}`);
  dashboard.getRange(`${startColumn}${startRow}`).values = [[cardLabels[index]]];
  dashboard.getRange(`${startColumn}${startRow}:${endColumn}${startRow}`).format = { fill: colors.blue, font: { bold: true, color: colors.white } };
  dashboard.mergeCells(`${startColumn}${startRow + 1}:${endColumn}${startRow + 2}`);
});
dashboard.getRange("A6").formulas = [["='Checks'!B6"]];
dashboard.getRange("E6").formulas = [["='Checks'!B7"]];
dashboard.getRange("I6").formulas = [["='Checks'!B10"]];
dashboard.getRange("M6").formulas = [["='Checks'!A14"]];
dashboard.getRange("A6:C7").format = { fill: colors.lightTeal, font: { bold: true, color: colors.greenLink, size: 18 }, horizontalAlignment: "center", verticalAlignment: "center" };
dashboard.getRange("E6:G7").format = { fill: colors.lightTeal, font: { bold: true, color: colors.greenLink, size: 18 }, horizontalAlignment: "center", verticalAlignment: "center" };
dashboard.getRange("I6:K7").format = { fill: colors.paleRed, font: { bold: true, color: colors.greenLink, size: 18 }, horizontalAlignment: "center", verticalAlignment: "center" };
dashboard.getRange("M6:T7").format = { fill: colors.paleYellow, font: { bold: true, color: colors.greenLink, size: 11 }, horizontalAlignment: "center", verticalAlignment: "center", wrapText: true };

sectionHeader(dashboard, "A9:J9", "Comparison bridge");
dashboard.getRange("A10:J13").values = [
  ["1", "Alt-data feature", "YoY growth / breadth / mix / supply", null, "2", "Operating state", "Nights / ADR / GBV", null, "3", "Revenue guidance"],
  [null, "↓", null, null, null, "↓", null, null, null, "↓"],
  ["Target", "Seasonal baseline", "Same guided quarter prior-year midpoint", null, "Residual", "Current midpoint − baseline", null, null, "Test", "Incremental out-of-sample improvement"],
  [null, "Current result", "All 50 sources are discovery-only and historical-ineligible", null, null, null, null, null, null, null],
];
dashboard.getRange("A10:J13").format = { wrapText: true, verticalAlignment: "center" };
dashboard.getRange("A10:J10").format.fill = colors.lightBlue;
dashboard.getRange("A12:J12").format.fill = colors.gray;
dashboard.getRange("B13:J13").format.fill = colors.paleYellow;

sectionHeader(dashboard, "A16:J16", "Highest-priority source mappings");
dashboard.getRange("A17:J17").values = [["Rank", "Source ID", "Family", "ABNB KPI", "Proposed feature", "Score", "Sign", "Coverage end", "Approval", "Historical eligible"]];
tableHeader(dashboard.getRange("A17:J17"));
for (let index = 0; index < 10; index += 1) {
  const dashboardRow = 18 + index;
  const sourceRow = crosswalkStart + index;
  dashboard.getRange(`A${dashboardRow}:J${dashboardRow}`).formulas = [[
    `='Source Crosswalk'!A${sourceRow}`,
    `='Source Crosswalk'!B${sourceRow}`,
    `='Source Crosswalk'!E${sourceRow}`,
    `='Source Crosswalk'!G${sourceRow}`,
    `='Source Crosswalk'!I${sourceRow}`,
    `='Source Crosswalk'!T${sourceRow}`,
    `='Source Crosswalk'!J${sourceRow}`,
    `='Source Crosswalk'!M${sourceRow}`,
    `='Source Crosswalk'!U${sourceRow}`,
    `='Source Crosswalk'!V${sourceRow}`,
  ]];
}
dashboard.getRange("A18:J27").format.font = { color: colors.greenLink, size: 9 };
dashboard.getRange("F18:F27").format.numberFormat = "0.00";
dashboard.getRange("I18:I27").format.fill = colors.paleYellow;
dashboard.getRange("J18:J27").format.fill = colors.paleRed;
dashboard.getRange("A17:J27").format.wrapText = true;
dashboard.getRange("A17:J27").format.borders = { preset: "inside", style: "thin", color: colors.gray };

const chart = dashboard.charts.add("line", { chartType: "line", title: "Revenue guidance midpoint ($mm)", hasLegend: false });
const series = chart.series.add("Guidance midpoint");
series.categoryFormula = `'Guidance History'!$D$${guidanceStart}:$D$${guidanceEnd}`;
series.formula = `'Guidance History'!$I$${guidanceStart}:$I$${guidanceEnd}`;
series.fill = colors.teal;
chart.title = "Revenue guidance midpoint ($mm)";
chart.hasLegend = false;
chart.xAxis = { axisType: "textAxis", textStyle: { fontSize: 9 } };
chart.yAxis = { numberFormatCode: "$#,##0" };
chart.setPosition("L9", "T27");

sectionHeader(dashboard, "A30:T30", "Interpretation guardrails");
dashboard.getRange("A31:T35").values = [
  ["No historical claim", null, "The September 3 snapshots fail every earlier guidance cutoff and cannot be backfilled as historical evidence.", null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
  ["No approval yet", null, "All 50 manifests remain discovery_only_not_approved; promotion requires a separate approved experiment.", null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
  ["Provider concentration", null, "Forty-one additions are distinct Eurostat datasets but share one provider and licence regime.", null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
  ["Correct target", null, "Test features against the guidance residual, not the raw seasonal guidance level.", null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
  ["Next evidence step", null, "Archive immutable releases prospectively, then run a preregistered walk-forward comparison.", null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null, null],
];
for (let row = 31; row <= 35; row += 1) {
  dashboard.mergeCells(`A${row}:B${row}`);
  dashboard.mergeCells(`C${row}:T${row}`);
}
dashboard.getRange("A31:B35").format = { fill: colors.paleYellow, font: { bold: true, color: colors.navy } };
dashboard.getRange("C31:T35").format = { fill: "#FFFDF5", wrapText: true };
dashboard.getRange("A:A").format.columnWidth = 8;
dashboard.getRange("B:B").format.columnWidth = 34;
dashboard.getRange("C:C").format.columnWidth = 29;
dashboard.getRange("D:D").format.columnWidth = 31;
dashboard.getRange("E:E").format.columnWidth = 48;
dashboard.getRange("F:F").format.columnWidth = 12;
dashboard.getRange("G:G").format.columnWidth = 25;
dashboard.getRange("H:H").format.columnWidth = 15;
dashboard.getRange("I:I").format.columnWidth = 29;
dashboard.getRange("J:J").format.columnWidth = 18;
dashboard.getRange("K:K").format.columnWidth = 3;
dashboard.getRange("L:T").format.columnWidth = 12;
dashboard.getRange("18:27").format.rowHeight = 46;
dashboard.freezePanes.freezeRows(3);

// Compact verification before export.
const keyInspect = await workbook.inspect({
  kind: "table",
  sheetId: "Checks",
  range: "A5:G14",
  include: "values,formulas",
  tableMaxRows: 20,
  tableMaxCols: 10,
  maxChars: 10000,
});
console.log("CHECKS_INSPECT");
console.log(keyInspect.ndjson);
const crosswalkInspect = await workbook.inspect({
  kind: "table",
  sheetId: "Source Crosswalk",
  range: "A6:T12",
  include: "values,formulas",
  tableMaxRows: 10,
  tableMaxCols: 20,
  maxChars: 12000,
});
console.log("CROSSWALK_INSPECT");
console.log(crosswalkInspect.ndjson);
const guidanceInspect = await workbook.inspect({
  kind: "table",
  sheetId: "Guidance History",
  range: "D6:N18",
  include: "values,formulas",
  tableMaxRows: 20,
  tableMaxCols: 12,
  maxChars: 12000,
});
console.log("GUIDANCE_INSPECT");
console.log(guidanceInspect.ndjson);
const errorInspect = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 300 },
  summary: "final formula error scan",
});
console.log("FORMULA_ERROR_SCAN");
console.log(errorInspect.ndjson);

await fs.mkdir(previewDir, { recursive: true });
const previewRanges = {
  Dashboard: "A1:T35",
  "Guidance History": "A1:Q18",
  "Source Crosswalk": "A1:Z18",
  "Eligibility Matrix": "A1:P16",
  Methodology: "A1:H29",
  Checks: "A1:G14",
};
for (const [sheetName, range] of Object.entries(previewRanges)) {
  const preview = await workbook.render({ sheetName, range, scale: 1, format: "png" });
  const safeName = sheetName.toLowerCase().replaceAll(" ", "_");
  await fs.writeFile(path.join(previewDir, `${safeName}.png`), new Uint8Array(await preview.arrayBuffer()));
}

await fs.mkdir(outputDir, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(JSON.stringify({ outputPath, sheets: 6, sources: inputs.crosswalk.length, guidanceEvents: inputs.guidance.length }));
