import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = path.dirname(fileURLToPath(import.meta.url));
const workspace = path.resolve(outputDir, "../../..");
const outputPath = path.join(outputDir, "ABNB_edge_guidance_stock_reaction.xlsx");
const previewDir = path.join(outputDir, "previews");

const paths = {
  guidance: path.join(workspace, "research/readiness/20260903T053309Z_abnb_readiness/target_panel.csv"),
  transcriptIndex: path.join(workspace, "research/transcripts/transcript_index.csv"),
  edge: path.join(workspace, "research/edge-discovery/20260903T062839Z_abnb_edge_discovery/permission_resolution/browser_acquisition/browser_observations.csv"),
  hypothesisLedger: path.join(workspace, "research/hypothesis_ledger.csv"),
  nasdaqAbnb: path.join(outputDir, "abnb_nasdaq_history.json"),
  nasdaqSpy: path.join(outputDir, "spy_nasdaq_history.json"),
};

await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });

const [guidanceCsv, transcriptCsv, edgeCsv, abnbJsonText, spyJsonText] = await Promise.all([
  fs.readFile(paths.guidance, "utf8"),
  fs.readFile(paths.transcriptIndex, "utf8"),
  fs.readFile(paths.edge, "utf8"),
  fs.readFile(paths.nasdaqAbnb, "utf8"),
  fs.readFile(paths.nasdaqSpy, "utf8"),
]);

async function csvObjects(csvText) {
  const csvWorkbook = await Workbook.fromCSV(csvText, { sheetName: "Data" });
  const csvSheet = csvWorkbook.worksheets.getItem("Data");
  const matrix = csvSheet.getUsedRange().values;
  const headers = matrix[0].map((v) => String(v ?? ""));
  return matrix.slice(1).filter((row) => row.some((v) => v !== null && v !== "")).map((row) =>
    Object.fromEntries(headers.map((header, index) => [header, row[index] ?? ""])),
  );
}

const [guidanceRows, transcriptRows, edgeRows] = await Promise.all([
  csvObjects(guidanceCsv),
  csvObjects(transcriptCsv),
  csvObjects(edgeCsv),
]);

const toNumber = (value) => {
  if (value === null || value === undefined || value === "") return null;
  const parsed = Number(String(value).replace(/[$,]/g, ""));
  return Number.isFinite(parsed) ? parsed : null;
};

const dateOnly = (value) => {
  if (!value) return null;
  const match = String(value).match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (match) return new Date(Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3])));
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? null : new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()));
};

const nasdaqDate = (value) => {
  const [month, day, year] = String(value).split("/").map(Number);
  return new Date(Date.UTC(year, month - 1, day));
};

const quarterShift = (fiscalPeriod, quarters) => {
  const match = String(fiscalPeriod).match(/^(\d{4})Q([1-4])$/);
  if (!match) return "";
  const serial = Number(match[1]) * 4 + Number(match[2]) - 1 + quarters;
  return `${Math.floor(serial / 4)}Q${(serial % 4) + 1}`;
};

const excelCol = (n) => {
  let s = "";
  let x = n;
  while (x > 0) {
    x -= 1;
    s = String.fromCharCode(65 + (x % 26)) + s;
    x = Math.floor(x / 26);
  }
  return s;
};

const abnbPayload = JSON.parse(abnbJsonText);
const spyPayload = JSON.parse(spyJsonText);
const abnbMarketRows = abnbPayload?.data?.tradesTable?.rows ?? [];
const spyMarketRows = spyPayload?.data?.tradesTable?.rows ?? [];
if (abnbPayload?.status?.rCode !== 200 || spyPayload?.status?.rCode !== 200) {
  throw new Error("Nasdaq historical-price request did not return status 200.");
}

const spyByDate = new Map(spyMarketRows.map((row) => [row.date, row]));
const priceRows = abnbMarketRows.map((abnb) => {
  const spy = spyByDate.get(abnb.date);
  return {
    date: nasdaqDate(abnb.date),
    dateKey: abnb.date,
    abnbClose: toNumber(abnb.close),
    spyClose: toNumber(spy?.close),
    abnbVolume: toNumber(abnb.volume),
    spyVolume: toNumber(spy?.volume),
  };
}).filter((row) => row.spyClose !== null).sort((a, b) => a.date - b.date);

const priceIndexByIso = new Map(priceRows.map((row, index) => [row.date.toISOString().slice(0, 10), index]));
const transcriptByPeriod = new Map(transcriptRows.map((row) => [String(row.fiscal_period), row]));
const guidanceByGuidedPeriod = new Map(guidanceRows.map((row, index) => [String(row.guided_fiscal_period), index + 2]));

const guidanceEvents = guidanceRows.map((row, index) => {
  const eventDate = dateOnly(row.guidance_available_at_utc);
  const eventIso = eventDate.toISOString().slice(0, 10);
  const priceIndex = priceIndexByIso.get(eventIso);
  if (priceIndex === undefined || !priceRows[priceIndex + 1]) {
    throw new Error(`No complete Nasdaq reaction window for ${row.prediction_id} on ${eventIso}.`);
  }
  return {
    ...row,
    rowNumber: index + 2,
    eventDate,
    nextTradingDate: priceRows[priceIndex + 1].date,
    targetLow: toNumber(row.target_low),
    targetHigh: toNumber(row.target_high),
    targetMidpoint: toNumber(row.target_midpoint),
    transcript: transcriptByPeriod.get(String(row.issuing_fiscal_period)),
  };
});

const eventDates = guidanceEvents.map((row) => row.eventDate);
const firstEventAfter = (availableDate) => guidanceEvents.find((event) => event.eventDate > availableDate);
const eligibleEventCount = (availableDate) => eventDates.filter((eventDate) => eventDate > availableDate).length;

const edgeSafeAvailability = (row) => {
  const reportDate = String(row.pit_status).match(/report_dated_(\d{4}-\d{2}-\d{2})/);
  return reportDate ? dateOnly(reportDate[1]) : dateOnly(row.observed_at_utc);
};

const sourceLayer = {
  VANCOUVER_STR_LICENSES: "Supply / regulatory stock",
  MELB_PED_HOURLY: "Physical-world activity",
  NYC_311_TOURISM_STRESS: "Physical-world activity / stress",
  NYC_OSE_ENFORCEMENT_REPORTS: "Supply / regulatory enforcement",
};

const edgeTreatment = (row) => {
  if (row.source_id === "NYC_OSE_ENFORCEMENT_REPORTS" && String(row.period) === "2024") {
    return "Limited historical comparison";
  }
  return "Prospective only";
};

const edgeLimitation = (row) => {
  if (row.source_id === "NYC_OSE_ENFORCEMENT_REPORTS" && String(row.period) === "2024") {
    return "One annual vintage was public before four later ABNB events; no pre-event transition sequence exists.";
  }
  if (row.source_id === "NYC_OSE_ENFORCEMENT_REPORTS") {
    return "Published after the last event in the panel; suitable only for the next guidance cycle.";
  }
  return "Current portal snapshot is not proof of historical availability; do not backfill into past events.";
};

const COLOR = {
  navy: "#17365D",
  teal: "#1F7A8C",
  paleTeal: "#DDEBF7",
  paleBlue: "#EAF2F8",
  green: "#E2F0D9",
  greenText: "#006100",
  amber: "#FFF2CC",
  amberText: "#9C6500",
  red: "#FCE4D6",
  redText: "#9C0006",
  gray: "#E7E6E6",
  lightGray: "#F3F5F7",
  dark: "#1F2937",
  sourceBlue: "#0000FF",
  linkGreen: "#008000",
  white: "#FFFFFF",
};

const workbook = Workbook.create();
const summary = workbook.worksheets.add("Executive Summary");
const guidance = workbook.worksheets.add("Guidance Events");
const reactions = workbook.worksheets.add("Price Reactions");
const edges = workbook.worksheets.add("Edge Observations");
const bridge = workbook.worksheets.add("Eligibility Bridge");
const ose = workbook.worksheets.add("OSE Trend");
const prices = workbook.worksheets.add("Price History");
const checks = workbook.worksheets.add("Checks");
const sources = workbook.worksheets.add("Sources");

for (const sheet of [summary, guidance, reactions, edges, bridge, ose, prices, checks, sources]) {
  sheet.showGridLines = false;
}

function titleBand(sheet, range, title) {
  sheet.getRange(range).merge();
  sheet.getRange(range).values = [[title]];
  sheet.getRange(range).format = {
    fill: COLOR.navy,
    font: { bold: true, color: COLOR.white, size: 16 },
    verticalAlignment: "center",
  };
  sheet.getRange(range).format.rowHeight = 28;
}

function sectionBand(sheet, range, title) {
  sheet.getRange(range).merge();
  sheet.getRange(range).values = [[title]];
  sheet.getRange(range).format = {
    fill: COLOR.teal,
    font: { bold: true, color: COLOR.white, size: 11 },
    verticalAlignment: "center",
  };
}

function headerStyle(range) {
  range.format = {
    fill: COLOR.navy,
    font: { bold: true, color: COLOR.white },
    wrapText: true,
    verticalAlignment: "center",
    borders: { preset: "all", style: "thin", color: "#B7C9D6" },
  };
  range.format.rowHeight = 34;
}

function bodyStyle(range) {
  range.format = {
    font: { color: COLOR.dark },
    verticalAlignment: "top",
    borders: { preset: "all", style: "thin", color: "#D9E2E8" },
  };
}

function addReturnConditionalFormatting(range) {
  range.conditionalFormats.add("cellIs", {
    operator: "greaterThan",
    formula: 0,
    format: { fill: COLOR.green, font: { color: COLOR.greenText } },
  });
  range.conditionalFormats.add("cellIs", {
    operator: "lessThan",
    formula: 0,
    format: { fill: COLOR.red, font: { color: COLOR.redText } },
  });
}

// Guidance Events
titleBand(guidance, "A1:S1", "ABNB Guidance Events — Preserved Point-in-Time Targets");
const guidanceHeaders = [
  "Prediction ID", "Issuing Quarter", "Guided Quarter", "Guidance Available UTC", "Event Date",
  "Guidance Type", "Low ($m)", "High ($m)", "Midpoint ($m)", "Prior-Q Midpoint ($m)",
  "Δ vs Prior-Q ($m)", "Δ vs Prior-Q (%)", "Same Guided Qtr PY ($m)", "Δ vs Seasonal ($m)",
  "Transcript Status", "Source ID", "Guidance Citation", "Confidence", "Evidence Notes",
];
guidance.getRange("A2:S2").values = [guidanceHeaders];
headerStyle(guidance.getRange("A2:S2"));
guidance.getRange(`A3:I${guidanceEvents.length + 2}`).values = guidanceEvents.map((event) => [
  event.prediction_id,
  event.issuing_fiscal_period,
  event.guided_fiscal_period,
  new Date(event.guidance_available_at_utc),
  event.eventDate,
  event.target_type,
  event.targetLow,
  event.targetHigh,
  event.targetMidpoint,
]);
guidance.getRange(`J3:N${guidanceEvents.length + 2}`).formulas = guidanceEvents.map((event, index) => {
  const excelRow = index + 3;
  const priorExcelRow = index === 0 ? null : excelRow - 1;
  const priorYearGuidedPeriod = quarterShift(event.guided_fiscal_period, -4);
  const priorYearSourceRow = guidanceByGuidedPeriod.get(priorYearGuidedPeriod);
  const priorYearExcelRow = priorYearSourceRow ? priorYearSourceRow + 1 : null;
  const priorFormula = priorExcelRow ? `=IFERROR(I${priorExcelRow},\"\")` : '=\"\"';
  const seasonalFormula = priorYearExcelRow ? `=IFERROR(I${priorYearExcelRow},\"\")` : '=\"\"';
  return [
    priorFormula,
    `=IF(OR(I${excelRow}=\"\",J${excelRow}=\"\"),\"\",I${excelRow}-J${excelRow})`,
    `=IF(OR(I${excelRow}=\"\",J${excelRow}=\"\"),\"\",I${excelRow}/J${excelRow}-1)`,
    seasonalFormula,
    `=IF(OR(I${excelRow}=\"\",M${excelRow}=\"\"),\"\",I${excelRow}-M${excelRow})`,
  ];
});
guidance.getRange(`O3:S${guidanceEvents.length + 2}`).values = guidanceEvents.map((event) => [
  `${event.transcript?.transcript_status ?? "not indexed"} / ${event.transcript?.license_status ?? "unknown license"}`,
  event.target_source_id,
  event.target_citation,
  event.target_confidence,
  event.discrepancy_notes,
]);
bodyStyle(guidance.getRange(`A3:S${guidanceEvents.length + 2}`));
guidance.getRange(`A3:I${guidanceEvents.length + 2}`).format.font = { color: COLOR.sourceBlue };
guidance.getRange(`O3:S${guidanceEvents.length + 2}`).format.font = { color: COLOR.sourceBlue };
guidance.getRange(`J3:N${guidanceEvents.length + 2}`).format.font = { color: "#000000" };
guidance.getRange(`D3:D${guidanceEvents.length + 2}`).setNumberFormat("yyyy-mm-dd hh:mm");
guidance.getRange(`E3:E${guidanceEvents.length + 2}`).setNumberFormat("yyyy-mm-dd");
guidance.getRange(`G3:K${guidanceEvents.length + 2}`).setNumberFormat('"$"#,##0.0');
guidance.getRange(`M3:N${guidanceEvents.length + 2}`).setNumberFormat('"$"#,##0.0');
guidance.getRange(`L3:L${guidanceEvents.length + 2}`).setNumberFormat("0.0%");
guidance.getRange(`Q3:Q${guidanceEvents.length + 2}`).format.font = { color: COLOR.linkGreen, underline: true };
guidance.getRange(`S3:S${guidanceEvents.length + 2}`).format.wrapText = true;
guidance.freezePanes.freezeRows(2);
guidance.freezePanes.freezeColumns(3);
guidance.tables.add(`A2:S${guidanceEvents.length + 2}`, true, "GuidanceEventsTable");
const guidanceWidths = [24, 14, 14, 20, 13, 16, 12, 12, 13, 17, 16, 14, 20, 18, 24, 15, 38, 12, 54];
guidanceWidths.forEach((width, index) => { guidance.getRange(`${excelCol(index + 1)}:${excelCol(index + 1)}`).format.columnWidth = width; });

// Price History
titleBand(prices, "A1:F1", "Free Official Market Data — Daily Closes and Volume");
prices.getRange("A2:F2").values = [["Date", "ABNB Close", "SPY Close", "ABNB Volume", "SPY Volume", "Provider"]];
headerStyle(prices.getRange("A2:F2"));
prices.getRange(`A3:F${priceRows.length + 2}`).values = priceRows.map((row) => [
  row.date, row.abnbClose, row.spyClose, row.abnbVolume, row.spyVolume, "Nasdaq public historical table",
]);
bodyStyle(prices.getRange(`A3:F${priceRows.length + 2}`));
prices.getRange(`A3:F${priceRows.length + 2}`).format.font = { color: COLOR.sourceBlue };
prices.getRange(`A3:A${priceRows.length + 2}`).setNumberFormat("yyyy-mm-dd");
prices.getRange(`B3:C${priceRows.length + 2}`).setNumberFormat('"$"#,##0.00');
prices.getRange(`D3:E${priceRows.length + 2}`).setNumberFormat("#,##0");
prices.freezePanes.freezeRows(2);
prices.tables.add(`A2:F${priceRows.length + 2}`, true, "PriceHistoryTable");
[13, 14, 14, 16, 16, 31].forEach((width, index) => { prices.getRange(`${excelCol(index + 1)}:${excelCol(index + 1)}`).format.columnWidth = width; });

// Price Reactions
titleBand(reactions, "A1:T1", "ABNB Guidance Event Reactions — Close to Next Trading-Day Close");
const reactionHeaders = [
  "Prediction ID", "Issuing Quarter", "Event Date", "Next Trading Date", "ABNB T0 Close", "ABNB T+1 Close",
  "ABNB Return", "SPY T0 Close", "SPY T+1 Close", "SPY Return", "Excess Return", "ABNB Direction",
  "Excess Direction", "Window Rationale", "Guidance Midpoint ($m)", "Δ Guidance vs Prior-Q ($m)",
  "Δ Guidance vs Prior-Q (%)", "Direction Comparison", "Edge Available at Event?", "Interpretation",
];
reactions.getRange("A2:T2").values = [reactionHeaders];
headerStyle(reactions.getRange("A2:T2"));
const priceLastRow = priceRows.length + 2;
reactions.getRange(`A3:D${guidanceEvents.length + 2}`).values = guidanceEvents.map((event) => [
  event.prediction_id, event.issuing_fiscal_period, event.eventDate, event.nextTradingDate,
]);
reactions.getRange(`E3:M${guidanceEvents.length + 2}`).formulas = guidanceEvents.map((event, index) => {
  const row = index + 3;
  return [
    `=IFERROR(VLOOKUP(C${row},'Price History'!$A$3:$E$${priceLastRow},2,FALSE),\"\")`,
    `=IFERROR(VLOOKUP(D${row},'Price History'!$A$3:$E$${priceLastRow},2,FALSE),\"\")`,
    `=IF(OR(E${row}=\"\",F${row}=\"\"),\"\",F${row}/E${row}-1)`,
    `=IFERROR(VLOOKUP(C${row},'Price History'!$A$3:$E$${priceLastRow},3,FALSE),\"\")`,
    `=IFERROR(VLOOKUP(D${row},'Price History'!$A$3:$E$${priceLastRow},3,FALSE),\"\")`,
    `=IF(OR(H${row}=\"\",I${row}=\"\"),\"\",I${row}/H${row}-1)`,
    `=IF(OR(G${row}=\"\",J${row}=\"\"),\"\",G${row}-J${row})`,
    `=IF(G${row}=\"\",\"\",IF(G${row}>0,\"Up\",IF(G${row}<0,\"Down\",\"Flat\")))`,
    `=IF(K${row}=\"\",\"\",IF(K${row}>0,\"Up\",IF(K${row}<0,\"Down\",\"Flat\")))`,
  ];
});
reactions.getRange(`N3:N${guidanceEvents.length + 2}`).values = guidanceEvents.map(() => [
  "Guidance timestamp is at the regular-market close; reaction = next close / event-date close − 1.",
]);
reactions.getRange(`O3:R${guidanceEvents.length + 2}`).formulas = guidanceEvents.map((event, index) => {
  const row = index + 3;
  const guidanceRow = index + 3;
  return [
    `=IF('Guidance Events'!I${guidanceRow}=\"\",\"\",'Guidance Events'!I${guidanceRow})`,
    `=IF('Guidance Events'!K${guidanceRow}=\"\",\"\",'Guidance Events'!K${guidanceRow})`,
    `=IF('Guidance Events'!L${guidanceRow}=\"\",\"\",'Guidance Events'!L${guidanceRow})`,
    `=IF(O${row}=\"\",\"Qualitative guidance\",IF(P${row}=\"\",\"No numeric prior-Q baseline\",IF(P${row}=0,\"Neutral\",IF(OR(AND(P${row}>0,K${row}>0),AND(P${row}<0,K${row}<0)),\"Aligned\",\"Diverged\"))))`,
  ];
});
const ose2024Available = dateOnly("2025-09-01");
reactions.getRange(`S3:T${guidanceEvents.length + 2}`).values = guidanceEvents.map((event) => {
  const hasEdge = event.eventDate > ose2024Available;
  return hasEdge
    ? ["Yes — OSE 2024 only", "One annual OSE report was public; insufficient vintages for a trend or predictive claim."]
    : ["No", "No approved edge observation was historically available; reaction is descriptive only."];
});
bodyStyle(reactions.getRange(`A3:T${guidanceEvents.length + 2}`));
reactions.getRange(`A3:D${guidanceEvents.length + 2}`).format.font = { color: COLOR.sourceBlue };
reactions.getRange(`N3:N${guidanceEvents.length + 2}`).format.font = { color: COLOR.sourceBlue };
reactions.getRange(`S3:T${guidanceEvents.length + 2}`).format.font = { color: COLOR.sourceBlue };
reactions.getRange(`E3:M${guidanceEvents.length + 2}`).format.font = { color: "#000000" };
reactions.getRange(`O3:R${guidanceEvents.length + 2}`).format.font = { color: COLOR.linkGreen };
reactions.getRange(`C3:D${guidanceEvents.length + 2}`).setNumberFormat("yyyy-mm-dd");
reactions.getRange(`E3:F${guidanceEvents.length + 2}`).setNumberFormat('"$"#,##0.00');
reactions.getRange(`H3:I${guidanceEvents.length + 2}`).setNumberFormat('"$"#,##0.00');
reactions.getRange(`G3:G${guidanceEvents.length + 2}`).setNumberFormat("0.00%");
reactions.getRange(`J3:K${guidanceEvents.length + 2}`).setNumberFormat("0.00%");
reactions.getRange(`O3:P${guidanceEvents.length + 2}`).setNumberFormat('"$"#,##0.0');
reactions.getRange(`Q3:Q${guidanceEvents.length + 2}`).setNumberFormat("0.0%");
reactions.getRange(`N3:N${guidanceEvents.length + 2}`).format.wrapText = true;
reactions.getRange(`T3:T${guidanceEvents.length + 2}`).format.wrapText = true;
addReturnConditionalFormatting(reactions.getRange(`G3:K${guidanceEvents.length + 2}`));
reactions.getRange(`R3:R${guidanceEvents.length + 2}`).conditionalFormats.add("containsText", {
  text: "Aligned",
  format: { fill: COLOR.green, font: { color: COLOR.greenText } },
});
reactions.getRange(`R3:R${guidanceEvents.length + 2}`).conditionalFormats.add("containsText", {
  text: "Diverged",
  format: { fill: COLOR.red, font: { color: COLOR.redText } },
});
reactions.getRange(`S3:S${guidanceEvents.length + 2}`).conditionalFormats.add("containsText", {
  text: "Yes",
  format: { fill: COLOR.amber, font: { color: COLOR.amberText } },
});
reactions.freezePanes.freezeRows(2);
reactions.freezePanes.freezeColumns(4);
reactions.tables.add(`A2:T${guidanceEvents.length + 2}`, true, "PriceReactionsTable");
const reactionWidths = [24, 14, 13, 16, 14, 14, 13, 13, 13, 12, 13, 14, 15, 45, 19, 23, 21, 22, 21, 54];
reactionWidths.forEach((width, index) => { reactions.getRange(`${excelCol(index + 1)}:${excelCol(index + 1)}`).format.columnWidth = width; });

// Edge Observations
titleBand(edges, "A1:V1", "Approved Browser-Acquired Edge Observations — Processing and Point-in-Time Treatment");
const edgeHeaders = [
  "Observation ID", "Source ID", "Provider Dataset", "Metric", "Period", "Value", "Unit", "Filters",
  "Observed UTC", "Official URL", "Collection Mode", "License / Terms", "Period Completeness", "PIT Status",
  "Research Disposition", "Source Notes", "First Safe Availability", "Eligible Historical Events", "First Eligible Event",
  "Treatment", "Economic Layer", "Comparison Limitation",
];
edges.getRange("A2:V2").values = [edgeHeaders];
headerStyle(edges.getRange("A2:V2"));
edges.getRange(`A3:Q${edgeRows.length + 2}`).values = edgeRows.map((row) => [
  row.observation_id,
  row.source_id,
  row.provider_dataset,
  row.metric,
  row.period,
  toNumber(row.value),
  row.unit,
  row.filters,
  new Date(row.observed_at_utc),
  row.official_url,
  row.collection_mode,
  row.license_or_terms,
  row.period_completeness,
  row.pit_status,
  row.research_disposition,
  row.notes,
  edgeSafeAvailability(row),
]);
edges.getRange(`R3:R${edgeRows.length + 2}`).formulas = edgeRows.map((row, index) => {
  const excelRow = index + 3;
  return [`=COUNTIF('Guidance Events'!$E$3:$E$${guidanceEvents.length + 2},\">\"&Q${excelRow})`];
});
edges.getRange(`S3:V${edgeRows.length + 2}`).values = edgeRows.map((row) => {
  const available = edgeSafeAvailability(row);
  const firstEligible = firstEventAfter(available);
  return [
    firstEligible ? firstEligible.issuing_fiscal_period : "None in panel",
    edgeTreatment(row),
    sourceLayer[row.source_id] ?? "Unclassified",
    edgeLimitation(row),
  ];
});
bodyStyle(edges.getRange(`A3:V${edgeRows.length + 2}`));
edges.getRange(`A3:Q${edgeRows.length + 2}`).format.font = { color: COLOR.sourceBlue };
edges.getRange(`R3:R${edgeRows.length + 2}`).format.font = { color: "#000000" };
edges.getRange(`S3:V${edgeRows.length + 2}`).format.font = { color: COLOR.sourceBlue };
edges.getRange(`I3:I${edgeRows.length + 2}`).setNumberFormat("yyyy-mm-dd hh:mm");
edges.getRange(`Q3:Q${edgeRows.length + 2}`).setNumberFormat("yyyy-mm-dd");
edges.getRange(`F3:F${edgeRows.length + 2}`).setNumberFormat("#,##0.00####");
edges.getRange(`J3:J${edgeRows.length + 2}`).format.font = { color: COLOR.linkGreen, underline: true };
edges.getRange(`P3:P${edgeRows.length + 2}`).format.wrapText = true;
edges.getRange(`V3:V${edgeRows.length + 2}`).format.wrapText = true;
edges.getRange(`T3:T${edgeRows.length + 2}`).conditionalFormats.add("containsText", {
  text: "Limited",
  format: { fill: COLOR.amber, font: { color: COLOR.amberText } },
});
edges.getRange(`T3:T${edgeRows.length + 2}`).conditionalFormats.add("containsText", {
  text: "Prospective",
  format: { fill: COLOR.paleBlue, font: { color: COLOR.navy } },
});
edges.freezePanes.freezeRows(2);
edges.freezePanes.freezeColumns(4);
edges.tables.add(`A2:V${edgeRows.length + 2}`, true, "EdgeObservationsTable");
const edgeWidths = [14, 28, 32, 34, 13, 14, 14, 32, 20, 42, 24, 32, 25, 28, 26, 54, 20, 21, 18, 27, 28, 58];
edgeWidths.forEach((width, index) => { edges.getRange(`${excelCol(index + 1)}:${excelCol(index + 1)}`).format.columnWidth = width; });

// Eligibility Bridge
titleBand(bridge, "A1:I1", "Edge-to-Guidance Eligibility Bridge");
bridge.getRange("A2:I2").values = [[
  "Source ID", "Economic Layer", "Observations", "Availability Basis", "First Safe Availability",
  "Eligible Guidance Events", "Gate Status", "Minimum Evidence", "Approved Use",
]];
headerStyle(bridge.getRange("A2:I2"));
const bridgeConfig = [
  ["VANCOUVER_STR_LICENSES", "Supply / regulatory stock", "Current portal snapshot", "BA-001", "No frozen model threshold"],
  ["MELB_PED_HOURLY", "Physical-world activity", "Current portal snapshot", "BA-021", "No frozen model threshold"],
  ["NYC_311_TOURISM_STRESS", "Physical-world activity / stress", "Current mutable portal", "BA-033", "No frozen model threshold"],
  ["NYC_OSE_ENFORCEMENT_REPORTS", "Supply / regulatory enforcement", "2024 report dated 2025-09-01; 2025 report dated 2026-09-01", "BA-055", ">=8 post-regime events and >=4 transitions (H-006)"],
];
const edgeExcelRowById = new Map(edgeRows.map((row, index) => [row.observation_id, index + 3]));
bridge.getRange("A3:B6").values = bridgeConfig.map((row) => row.slice(0, 2));
bridge.getRange("C3:C6").formulas = bridgeConfig.map((row, index) => [
  `=COUNTIF('Edge Observations'!$B$3:$B$${edgeRows.length + 2},A${index + 3})`,
]);
bridge.getRange("D3:D6").values = bridgeConfig.map((row) => [row[2]]);
bridge.getRange("E3:F6").formulas = bridgeConfig.map((row) => {
  const refRow = edgeExcelRowById.get(row[3]);
  return [
    `='Edge Observations'!Q${refRow}`,
    `='Edge Observations'!R${refRow}`,
  ];
});
bridge.getRange("G3:I6").values = bridgeConfig.map((row) => {
  const isOse = row[0] === "NYC_OSE_ENFORCEMENT_REPORTS";
  return [
    isOse ? "Limited—descriptive" : "Prospective only",
    row[4],
    isOse ? "Monitor and compare narratively; do not fit or promote." : "Prospective monitoring from 2026-09-03 onward.",
  ];
});
bodyStyle(bridge.getRange("A3:I6"));
bridge.getRange("A3:B6").format.font = { color: COLOR.sourceBlue };
bridge.getRange("D3:D6").format.font = { color: COLOR.sourceBlue };
bridge.getRange("G3:I6").format.font = { color: COLOR.sourceBlue };
bridge.getRange("C3:C6").format.font = { color: "#000000" };
bridge.getRange("E3:F6").format.font = { color: COLOR.linkGreen };
bridge.getRange("E3:E6").setNumberFormat("yyyy-mm-dd");
bridge.getRange("D3:I6").format.wrapText = true;
bridge.getRange("G3:G6").conditionalFormats.add("containsText", {
  text: "Limited",
  format: { fill: COLOR.amber, font: { color: COLOR.amberText } },
});
bridge.getRange("G3:G6").conditionalFormats.add("containsText", {
  text: "Prospective",
  format: { fill: COLOR.paleBlue, font: { color: COLOR.navy } },
});
bridge.freezePanes.freezeRows(2);
bridge.tables.add("A2:I6", true, "EligibilityBridgeTable");
[30, 30, 14, 44, 20, 22, 24, 43, 48].forEach((width, index) => { bridge.getRange(`${excelCol(index + 1)}:${excelCol(index + 1)}`).format.columnWidth = width; });

// OSE Trend
titleBand(ose, "A1:L1", "NYC OSE Illegal Short-Term Rental Enforcement — 2024 to 2025");
ose.getRange("A2:H2").values = [["Metric", "Unit", "2024", "2025", "Absolute Change", "YoY Change", "Direction", "Interpretation"]];
headerStyle(ose.getRange("A2:H2"));
const ose2024 = new Map(edgeRows.filter((row) => row.source_id === "NYC_OSE_ENFORCEMENT_REPORTS" && String(row.period) === "2024").map((row) => [row.metric, toNumber(row.value)]));
const ose2025 = new Map(edgeRows.filter((row) => row.source_id === "NYC_OSE_ENFORCEMENT_REPORTS" && String(row.period) === "2025").map((row) => [row.metric, toNumber(row.value)]));
const oseMetrics = [
  ["illegal_str_complaints_received", "complaints", "Complaint flow fell; this can reflect compliance, reporting behavior, or underlying activity."],
  ["distinct_locations_receiving_complaints", "locations", "Fewer complained-about locations; reported figures are lower bounds."],
  ["inspections_total", "inspections", "Higher total inspection activity indicates stronger enforcement intensity."],
  ["inspections_attempted", "inspections", "Attempted inspections increased."],
  ["inspections_conducted", "inspections", "Completed inspections increased."],
  ["inspections_follow_up", "inspections", "Follow-up inspections nearly doubled."],
  ["summonses_or_violations_issued", "summonses", "Summonses/violations rose, consistent with tighter enforcement."],
  ["penalties_imposed", "USD", "Penalties imposed rose sharply; timing notes remain important."],
  ["penalties_paid", "USD", "Cash paid increased, but slower than imposed penalties."],
  ["share_penalties_paid", "ratio", "Collection share fell despite higher dollars paid."],
  ["immediately_hazardous_violation_locations", "locations", "Hazardous-violation locations increased."],
];
ose.getRange(`A3:D${oseMetrics.length + 2}`).values = oseMetrics.map(([metric, unit]) => [metric, unit, ose2024.get(metric), ose2025.get(metric)]);
ose.getRange(`E3:G${oseMetrics.length + 2}`).formulas = oseMetrics.map((_, index) => {
  const row = index + 3;
  return [
    `=D${row}-C${row}`,
    `=IF(C${row}=0,\"\",D${row}/C${row}-1)`,
    `=IF(E${row}>0,\"Up\",IF(E${row}<0,\"Down\",\"Flat\"))`,
  ];
});
ose.getRange(`H3:H${oseMetrics.length + 2}`).values = oseMetrics.map((row) => [row[2]]);
bodyStyle(ose.getRange(`A3:H${oseMetrics.length + 2}`));
ose.getRange(`A3:D${oseMetrics.length + 2}`).format.font = { color: COLOR.sourceBlue };
ose.getRange(`E3:G${oseMetrics.length + 2}`).format.font = { color: "#000000" };
ose.getRange(`H3:H${oseMetrics.length + 2}`).format.font = { color: COLOR.sourceBlue };
ose.getRange(`C3:F${oseMetrics.length + 2}`).setNumberFormat("#,##0.0");
ose.getRange(`F3:F${oseMetrics.length + 2}`).setNumberFormat("0.0%");
const penaltyRows = oseMetrics.map((row, index) => row[1] === "USD" ? index + 3 : null).filter(Boolean);
for (const row of penaltyRows) ose.getRange(`C${row}:E${row}`).setNumberFormat('"$"#,##0');
const ratioRow = oseMetrics.findIndex((row) => row[1] === "ratio") + 3;
ose.getRange(`C${ratioRow}:F${ratioRow}`).setNumberFormat("0.0%");
ose.getRange(`H3:H${oseMetrics.length + 2}`).format.wrapText = true;
addReturnConditionalFormatting(ose.getRange(`E3:F${oseMetrics.length + 2}`));
ose.getRange("J2:L2").values = [["Selected Metric", "2024", "2025"]];
headerStyle(ose.getRange("J2:L2"));
const selectedOseMetrics = [
  "illegal_str_complaints_received",
  "inspections_total",
  "summonses_or_violations_issued",
  "immediately_hazardous_violation_locations",
];
ose.getRange("J3:J6").values = selectedOseMetrics.map((metric) => [metric.replaceAll("_", " ")]);
ose.getRange("K3:L6").formulas = selectedOseMetrics.map((metric) => {
  const sourceRow = oseMetrics.findIndex((row) => row[0] === metric) + 3;
  return [`=C${sourceRow}`, `=D${sourceRow}`];
});
bodyStyle(ose.getRange("J3:L6"));
const oseChart = ose.charts.add("bar", { chartType: "bar", title: "Enforcement Activity Increased Despite Fewer Complaints", hasLegend: true });
const ose2024Series = oseChart.series.add("2024");
ose2024Series.categoryFormula = "'OSE Trend'!$J$3:$J$6";
ose2024Series.formula = "'OSE Trend'!$K$3:$K$6";
ose2024Series.fill = "#1F6D8C";
const ose2025Series = oseChart.series.add("2025");
ose2025Series.categoryFormula = "'OSE Trend'!$J$3:$J$6";
ose2025Series.formula = "'OSE Trend'!$L$3:$L$6";
ose2025Series.fill = "#ED7D31";
oseChart.title = "Enforcement Activity Increased Despite Fewer Complaints";
oseChart.titleTextStyle.fontSize = 12;
oseChart.hasLegend = true;
oseChart.xAxis = { axisType: "textAxis", textStyle: { fontSize: 9 } };
oseChart.yAxis = { numberFormatCode: "#,##0" };
oseChart.setPosition("J8", "R23");
ose.freezePanes.freezeRows(2);
ose.tables.add(`A2:H${oseMetrics.length + 2}`, true, "OSETrendTable");
[38, 14, 15, 15, 18, 14, 13, 62, 3, 38, 15, 15].forEach((width, index) => { ose.getRange(`${excelCol(index + 1)}:${excelCol(index + 1)}`).format.columnWidth = width; });

// Executive Summary
titleBand(summary, "A1:M1", "ABNB Edge Data vs Guidance and Stock Reactions");
summary.getRange("A2:M2").merge();
summary.getRange("A2:M2").values = [["As-of 2026-09-03 | 23 guidance events | free official sources only | descriptive research, not a promoted forecast"]];
summary.getRange("A2:M2").format = { fill: COLOR.paleBlue, font: { italic: true, color: COLOR.navy }, wrapText: true };

const cardRanges = ["A4:B7", "C4:D7", "E4:F7", "G4:H7"];
const cardLabels = ["GUIDANCE EVENTS", "NUMERIC RANGES", "EDGE OBSERVATIONS", "APPROVED PROVIDERS"];
const cardFormulas = [
  `=COUNTA('Guidance Events'!$A$3:$A$${guidanceEvents.length + 2})`,
  `=COUNT('Guidance Events'!$I$3:$I$${guidanceEvents.length + 2})`,
  `=COUNTA('Edge Observations'!$A$3:$A$${edgeRows.length + 2})`,
  "=COUNTA('Eligibility Bridge'!$A$3:$A$6)",
];
for (let i = 0; i < cardRanges.length; i += 1) {
  const [start, end] = cardRanges[i].split(":");
  const startCol = start.match(/[A-Z]+/)[0];
  const startRow = Number(start.match(/\d+/)[0]);
  const endCol = end.match(/[A-Z]+/)[0];
  const endRow = Number(end.match(/\d+/)[0]);
  summary.getRange(`${startCol}${startRow}:${endCol}${startRow}`).merge();
  summary.getRange(`${startCol}${startRow}:${endCol}${startRow}`).values = [[cardLabels[i]]];
  summary.getRange(`${startCol}${startRow}:${endCol}${startRow}`).format = { fill: COLOR.teal, font: { bold: true, color: COLOR.white }, horizontalAlignment: "center" };
  summary.getRange(`${startCol}${startRow + 1}:${endCol}${endRow}`).merge();
  summary.getRange(`${startCol}${startRow + 1}:${endCol}${endRow}`).formulas = [[cardFormulas[i]]];
  summary.getRange(`${startCol}${startRow + 1}:${endCol}${endRow}`).format = { fill: COLOR.lightGray, font: { bold: true, color: COLOR.navy, size: 20 }, horizontalAlignment: "center", verticalAlignment: "center", borders: { preset: "outside", style: "thin", color: "#B7C9D6" } };
}

const card2Ranges = ["A9:B12", "C9:D12", "E9:F12", "G9:H12"];
const card2Labels = ["EVENTS WITH EDGE AVAILABLE", "AVG ABNB REACTION", "AVG EXCESS REACTION", "MEDIAN EXCESS REACTION"];
const card2Formulas = [
  `=COUNTIF('Price Reactions'!$S$3:$S$${guidanceEvents.length + 2},\"Yes — OSE 2024 only\")`,
  `=AVERAGE('Price Reactions'!$G$3:$G$${guidanceEvents.length + 2})`,
  `=AVERAGE('Price Reactions'!$K$3:$K$${guidanceEvents.length + 2})`,
  `=MEDIAN('Price Reactions'!$K$3:$K$${guidanceEvents.length + 2})`,
];
for (let i = 0; i < card2Ranges.length; i += 1) {
  const [start, end] = card2Ranges[i].split(":");
  const startCol = start.match(/[A-Z]+/)[0];
  const startRow = Number(start.match(/\d+/)[0]);
  const endCol = end.match(/[A-Z]+/)[0];
  const endRow = Number(end.match(/\d+/)[0]);
  summary.getRange(`${startCol}${startRow}:${endCol}${startRow}`).merge();
  summary.getRange(`${startCol}${startRow}:${endCol}${startRow}`).values = [[card2Labels[i]]];
  summary.getRange(`${startCol}${startRow}:${endCol}${startRow}`).format = { fill: COLOR.navy, font: { bold: true, color: COLOR.white, size: 9 }, horizontalAlignment: "center", wrapText: true };
  summary.getRange(`${startCol}${startRow + 1}:${endCol}${endRow}`).merge();
  summary.getRange(`${startCol}${startRow + 1}:${endCol}${endRow}`).formulas = [[card2Formulas[i]]];
  summary.getRange(`${startCol}${startRow + 1}:${endCol}${endRow}`).format = { fill: COLOR.lightGray, font: { bold: true, color: COLOR.navy, size: 18 }, horizontalAlignment: "center", verticalAlignment: "center", borders: { preset: "outside", style: "thin", color: "#B7C9D6" } };
}
summary.getRange("C10:H12").setNumberFormat("0.00%");

sectionBand(summary, "A14:M14", "Four-Layer Interpretation");
summary.getRange("A15:B18").merge();
summary.getRange("A15:B18").values = [["1. ECONOMIC NOWCAST\nOSE complaints fell 13.6% in 2025, while inspections, summonses, penalties, and hazardous-location counts rose. This is an enforcement-pressure signal, not a direct bookings measure."]];
summary.getRange("C15:E18").merge();
summary.getRange("C15:E18").values = [["2. GUIDANCE POLICY\nThe guidance panel preserves management’s next-quarter revenue ranges and qualitative calls. Numeric changes are compared with prior-quarter and same-season guidance baselines."]];
summary.getRange("F15:H18").merge();
summary.getRange("F15:H18").values = [["3. EXPECTATIONS\nNo point-in-time sell-side consensus series is present. Direction comparisons therefore use guidance baselines only and must not be described as earnings surprise versus Street expectations."]];
summary.getRange("I15:M18").merge();
summary.getRange("I15:M18").values = [["4. MARKET REACTION\nABNB and SPY returns use event-date close to next-trading-day close. Excess return is ABNB minus SPY. Alignment with guidance direction is descriptive and does not establish causality."]];
summary.getRange("A15:M18").format = { fill: COLOR.paleBlue, font: { color: COLOR.dark }, wrapText: true, verticalAlignment: "top", borders: { preset: "all", style: "thin", color: "#B7C9D6" } };
summary.getRange("15:18").format.rowHeight = 24;

sectionBand(summary, "A20:M20", "Decision-Relevant Findings");
summary.getRange("A21:M24").merge();
summary.getRange("A21:M24").values = [[
  "• 15 candidate sources were explored; 4 free official providers yielded 65 safe aggregate observations.\n" +
  "• Only the 2024 NYC OSE annual report was available before any event in this panel, covering four later guidance events. One annual vintage and no consecutive pre-event transitions are below H-006’s minimum evidence gate.\n" +
  "• Vancouver, Melbourne, NYC 311, and the 2025 OSE report are prospective-only. They are formatted for monitoring, not retroactively inserted into historical tests.\n" +
  "• No edge source is promoted and no fitted model or trading claim is made. The workbook is an auditable comparison and monitoring baseline.",
]];
summary.getRange("A21:M24").format = { fill: COLOR.amber, font: { color: COLOR.dark }, wrapText: true, verticalAlignment: "top", borders: { preset: "outside", style: "thin", color: "#C9B458" } };

sectionBand(summary, "A26:M26", "Event Reaction Trend");
summary.getRange("A27:C27").values = [["Issuing Quarter", "ABNB Return", "Excess Return"]];
headerStyle(summary.getRange("A27:C27"));
summary.getRange(`A28:C${27 + guidanceEvents.length}`).formulas = guidanceEvents.map((_, index) => {
  const sourceRow = index + 3;
  return [
    `='Price Reactions'!B${sourceRow}`,
    `='Price Reactions'!G${sourceRow}`,
    `='Price Reactions'!K${sourceRow}`,
  ];
});
summary.getRange(`B28:C${27 + guidanceEvents.length}`).setNumberFormat("0.0%");
bodyStyle(summary.getRange(`A28:C${27 + guidanceEvents.length}`));
addReturnConditionalFormatting(summary.getRange(`B28:C${27 + guidanceEvents.length}`));
const reactionChart = summary.charts.add("line", summary.getRange(`A27:C${27 + guidanceEvents.length}`));
reactionChart.title = "ABNB Earnings Reactions vs Market-Adjusted Returns";
reactionChart.titleTextStyle.fontSize = 12;
reactionChart.hasLegend = true;
reactionChart.xAxis = { axisType: "textAxis", textStyle: { fontSize: 8 } };
reactionChart.yAxis = { numberFormatCode: "0%" };
reactionChart.setPosition("E27", "M43");

sectionBand(summary, "A52:M52", "Guidance Midpoint Trend");
summary.getRange("A53:B53").values = [["Issuing Quarter", "Guidance Midpoint ($m)"]];
headerStyle(summary.getRange("A53:B53"));
summary.getRange(`A54:B${53 + guidanceEvents.length}`).formulas = guidanceEvents.map((_, index) => {
  const sourceRow = index + 3;
  return [`='Guidance Events'!B${sourceRow}`, `=IF('Guidance Events'!I${sourceRow}=\"\",\"\",'Guidance Events'!I${sourceRow})`];
});
summary.getRange(`B54:B${53 + guidanceEvents.length}`).setNumberFormat('"$"#,##0');
bodyStyle(summary.getRange(`A54:B${53 + guidanceEvents.length}`));
const guidanceChart = summary.charts.add("line", summary.getRange(`A53:B${53 + guidanceEvents.length}`));
guidanceChart.title = "Next-Quarter Revenue Guidance Midpoints ($m)";
guidanceChart.titleTextStyle.fontSize = 12;
guidanceChart.hasLegend = false;
guidanceChart.xAxis = { axisType: "textAxis", textStyle: { fontSize: 8 } };
guidanceChart.yAxis = { numberFormatCode: '"$"#,##0' };
guidanceChart.setPosition("E52", "M68");
summary.getRange("A78:M80").merge();
summary.getRange("A78:M80").values = [["Reading rule: use only observations with first safe availability strictly before an earnings cutoff. Current snapshots are never treated as historical vintages. Stock reactions summarize what happened after guidance; they are not predictor inputs."]];
summary.getRange("A78:M80").format = { fill: COLOR.gray, font: { italic: true, color: COLOR.dark }, wrapText: true, verticalAlignment: "center" };
[16, 15, 16, 15, 16, 16, 16, 16, 16, 16, 16, 16, 16].forEach((width, index) => { summary.getRange(`${excelCol(index + 1)}:${excelCol(index + 1)}`).format.columnWidth = width; });
summary.freezePanes.freezeRows(2);

// Checks
titleBand(checks, "A1:G1", "Workbook Quality and Reconciliation Checks");
checks.getRange("A2:G2").values = [["Check", "Actual", "Expected", "Difference", "Tolerance", "Status", "Notes"]];
headerStyle(checks.getRange("A2:G2"));
const numericGuidanceCount = guidanceEvents.filter((event) => event.targetMidpoint !== null).length;
const oseRowByMetric = new Map(oseMetrics.map((row, index) => [row[0], index + 3]));
const checkDefinitions = [
  ["Guidance event count", `=COUNTA('Guidance Events'!$A$3:$A$${guidanceEvents.length + 2})`, guidanceEvents.length, 0, "All preserved events loaded."],
  ["Numeric guidance midpoint count", `=COUNT('Guidance Events'!$I$3:$I$${guidanceEvents.length + 2})`, numericGuidanceCount, 0, "Qualitative rows remain blank by design."],
  ["Price-history row count", `=COUNTA('Price History'!$A$3:$A$${priceRows.length + 2})`, priceRows.length, 0, "ABNB and SPY matched by trading date."],
  ["Edge observation count", `=COUNTA('Edge Observations'!$A$3:$A$${edgeRows.length + 2})`, edgeRows.length, 0, "65 aggregate browser observations expected."],
  ["ABNB reaction windows populated", `=COUNT('Price Reactions'!$G$3:$G$${guidanceEvents.length + 2})`, guidanceEvents.length, 0, "Every event must have T0 and T+1 closes."],
  ["SPY reaction windows populated", `=COUNT('Price Reactions'!$J$3:$J$${guidanceEvents.length + 2})`, guidanceEvents.length, 0, "Every event must have benchmark closes."],
  ["Historically edge-covered events", `=COUNTIF('Price Reactions'!$S$3:$S$${guidanceEvents.length + 2},\"Yes — OSE 2024 only\")`, 4, 0, "Only OSE 2024 was available before four later events."],
  ["OSE 2024 inspection reconciliation", `='OSE Trend'!C${oseRowByMetric.get("inspections_total")}-SUM('OSE Trend'!C${oseRowByMetric.get("inspections_attempted")},'OSE Trend'!C${oseRowByMetric.get("inspections_conducted")},'OSE Trend'!C${oseRowByMetric.get("inspections_follow_up")})`, 0, 0, "Total equals attempted + conducted + follow-up."],
  ["OSE 2025 inspection reconciliation", `='OSE Trend'!D${oseRowByMetric.get("inspections_total")}-SUM('OSE Trend'!D${oseRowByMetric.get("inspections_attempted")},'OSE Trend'!D${oseRowByMetric.get("inspections_conducted")},'OSE Trend'!D${oseRowByMetric.get("inspections_follow_up")})`, 0, 0, "Total equals attempted + conducted + follow-up."],
  ["OSE 2024 paid-share reconciliation", `='OSE Trend'!C${oseRowByMetric.get("share_penalties_paid")}-'OSE Trend'!C${oseRowByMetric.get("penalties_paid")}/'OSE Trend'!C${oseRowByMetric.get("penalties_imposed")}`, 0, 0.000001, "Reported ratio reconciles to paid / imposed."],
  ["OSE 2025 paid-share reconciliation", `='OSE Trend'!D${oseRowByMetric.get("share_penalties_paid")}-'OSE Trend'!D${oseRowByMetric.get("penalties_paid")}/'OSE Trend'!D${oseRowByMetric.get("penalties_imposed")}`, 0, 0.000001, "Reported ratio reconciles to paid / imposed."],
];
checks.getRange(`A3:C${checkDefinitions.length + 2}`).values = checkDefinitions.map((row) => [row[0], null, row[2]]);
checks.getRange(`B3:B${checkDefinitions.length + 2}`).formulas = checkDefinitions.map((row) => [row[1]]);
checks.getRange(`D3:F${checkDefinitions.length + 2}`).formulas = checkDefinitions.map((_, index) => {
  const row = index + 3;
  return [
    `=IF(AND(ISNUMBER(B${row}),ISNUMBER(C${row})),B${row}-C${row},IF(B${row}=C${row},0,1))`,
    `=${checkDefinitions[index][3]}`,
    `=IF(ABS(D${row})<=E${row},\"PASS\",\"FAIL\")`,
  ];
});
checks.getRange(`G3:G${checkDefinitions.length + 2}`).values = checkDefinitions.map((row) => [row[4]]);
bodyStyle(checks.getRange(`A3:G${checkDefinitions.length + 2}`));
checks.getRange(`A3:A${checkDefinitions.length + 2}`).format.font = { color: COLOR.sourceBlue };
checks.getRange(`B3:F${checkDefinitions.length + 2}`).format.font = { color: "#000000" };
checks.getRange(`G3:G${checkDefinitions.length + 2}`).format.font = { color: COLOR.sourceBlue };
checks.getRange(`B3:E${checkDefinitions.length + 2}`).setNumberFormat("0.000000");
checks.getRange(`F3:F${checkDefinitions.length + 2}`).conditionalFormats.add("containsText", {
  text: "PASS",
  format: { fill: COLOR.green, font: { bold: true, color: COLOR.greenText } },
});
checks.getRange(`F3:F${checkDefinitions.length + 2}`).conditionalFormats.add("containsText", {
  text: "FAIL",
  format: { fill: COLOR.red, font: { bold: true, color: COLOR.redText } },
});
checks.freezePanes.freezeRows(2);
checks.tables.add(`A2:G${checkDefinitions.length + 2}`, true, "ChecksTable");
[38, 16, 16, 16, 14, 14, 58].forEach((width, index) => { checks.getRange(`${excelCol(index + 1)}:${excelCol(index + 1)}`).format.columnWidth = width; });

// Sources
titleBand(sources, "A1:I1", "Source and Methodology Register");
sources.getRange("A2:I2").values = [["Source ID", "Category", "Provider", "Dataset / Page", "URL or Local Path", "Retrieved / Dated", "License / Access", "Workbook Use", "Limitations"]];
headerStyle(sources.getRange("A2:I2"));
const sourceRows = [
  ["EDGE_VANCOUVER", "Edge data", "City of Vancouver", "Business licences 2013–2024 / current portal", "https://opendata.vancouver.ca/explore/dataset/business-licences-2013-to-2024/information/", "2026-09-03", "Open Government Licence – Vancouver", "Prospective monitoring", "Current portal view is not an original historical vintage."],
  ["EDGE_MELBOURNE", "Edge data", "City of Melbourne", "Pedestrian counting system", "https://data.melbourne.vic.gov.au/", "2026-09-03", "Open data portal", "Prospective physical-activity monitoring", "Coverage differs by year and sensor availability."],
  ["EDGE_NYC311", "Edge data", "NYC Open Data", "311 service requests / tourism-stress aggregate", "https://data.cityofnewyork.us/", "2026-09-03", "NYC Open Data terms", "Prospective monitoring", "Current mutable data; complaints are not bookings."],
  ["EDGE_NYCOSE", "Edge data", "NYC Mayor’s Office of Special Enforcement", "Local Law 87 annual enforcement reports", "https://www.nyc.gov/site/specialenforcement/reporting-law.page", "2024 report: 2025-09-01; 2025 report: 2026-09-01", "Public official reports", "Limited historical comparison and prospective monitoring", "Only one annual report was available before any covered ABNB event."],
  ["GUIDANCE_PANEL", "Guidance", "Airbnb / SEC", "Point-in-time target panel", paths.guidance, "As preserved in panel", "Public filings / investor materials", "Guidance ranges, cutoffs, and citations", "Transcript fact tables are empty; guidance is anchored to preserved SEC/Airbnb evidence."],
  ["TRANSCRIPT_INDEX", "Transcript metadata", "User-provided FactSet CallStreet files", "Transcript index", paths.transcriptIndex, "Indexed 2026-09-03", "User-provided restricted", "Metadata/status only; no long transcript excerpts reproduced", "Published-at timestamps are not independently verified in the index."],
  ["NASDAQ_ABNB", "Market data", "Nasdaq", "ABNB historical quotes", "https://www.nasdaq.com/market-activity/stocks/abnb/historical", "Retrieved 2026-09-03", "Free public historical page", "ABNB daily closes and volumes", "Unadjusted displayed closes; close-to-next-close event study only."],
  ["NASDAQ_SPY", "Market data", "Nasdaq", "SPY historical quotes", "https://www.nasdaq.com/market-activity/etf/spy/historical", "Retrieved 2026-09-03", "Free public historical page", "SPY benchmark closes and volumes", "Simple benchmark subtraction is descriptive, not a factor model."],
  ["HYPOTHESIS_LEDGER", "Governance", "Internal research ledger", "Frozen hypotheses and minimum-evidence gates", paths.hypothesisLedger, "2026-09-03", "Local research artifact", "Eligibility and interpretation rules", "No model fitting or promotion is authorized by this workbook."],
];
sources.getRange(`A3:I${sourceRows.length + 2}`).values = sourceRows;
bodyStyle(sources.getRange(`A3:I${sourceRows.length + 2}`));
sources.getRange(`A3:I${sourceRows.length + 2}`).format.font = { color: COLOR.sourceBlue };
sources.getRange(`E3:E${sourceRows.length + 2}`).format.font = { color: COLOR.linkGreen, underline: true };
sources.getRange(`D3:I${sourceRows.length + 2}`).format.wrapText = true;
sources.freezePanes.freezeRows(2);
sources.tables.add(`A2:I${sourceRows.length + 2}`, true, "SourcesTable");
[24, 20, 33, 38, 70, 30, 34, 44, 58].forEach((width, index) => { sources.getRange(`${excelCol(index + 1)}:${excelCol(index + 1)}`).format.columnWidth = width; });

// Apply light alternating body fills without overwriting conditional formats.
for (const sheet of [guidance, reactions, edges, bridge, ose, prices, checks, sources]) {
  const used = sheet.getUsedRange();
  if (used) used.format.verticalAlignment = "top";
}

const previewRanges = {
  "Executive Summary": "A1:M80",
  "Guidance Events": `A1:S${guidanceEvents.length + 2}`,
  "Price Reactions": `A1:T${guidanceEvents.length + 2}`,
  "Edge Observations": "A1:V24",
  "Eligibility Bridge": "A1:I6",
  "OSE Trend": "A1:R23",
  "Price History": "A1:F35",
  "Checks": `A1:G${checkDefinitions.length + 2}`,
  "Sources": `A1:I${sourceRows.length + 2}`,
};

for (const [sheetName, range] of Object.entries(previewRanges)) {
  const preview = await workbook.render({ sheetName, range, scale: 0.9, format: "png" });
  const safeName = sheetName.toLowerCase().replaceAll(" ", "_");
  await fs.writeFile(path.join(previewDir, `${safeName}.png`), new Uint8Array(await preview.arrayBuffer()));
}

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(outputPath);

const sheetInspection = await workbook.inspect({
  kind: "sheet,drawing",
  include: "id,name",
  maxChars: 10000,
});
const formulaInspection = await workbook.inspect({
  kind: "formula",
  sheetId: "Price Reactions",
  range: `E3:R${guidanceEvents.length + 2}`,
  maxChars: 12000,
  options: { maxResults: 80 },
});

console.log(JSON.stringify({
  outputPath,
  previewDir,
  guidanceEvents: guidanceEvents.length,
  numericGuidanceCount,
  edgeObservations: edgeRows.length,
  priceRows: priceRows.length,
  firstPriceDate: priceRows[0].date.toISOString().slice(0, 10),
  lastPriceDate: priceRows.at(-1).date.toISOString().slice(0, 10),
  eligibleEdgeEvents: guidanceEvents.filter((event) => event.eventDate > ose2024Available).length,
  summaryValues: summary.getRange("A1:H12").values,
  checkValues: checks.getRange(`A2:G${checkDefinitions.length + 2}`).values,
  sheetInspection: sheetInspection.ndjson,
  formulaInspection: formulaInspection.ndjson,
}, null, 2));
