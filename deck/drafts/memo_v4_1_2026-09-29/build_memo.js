// Builds ABNB_Citadel_Pitch_Memo_v4_1.docx from memo_v4_1_text.md (same folder); copy of the v4 builder with v4.1 paths.
// Format mirrors the 24 Sep memo: US Letter, 0.5in margins, Aptos 11pt, justified, bold run-in headings,
// charts floated right at ~3.4in. Run from the repo root:
//   NODE_PATH=<dir with node_modules/docx> node deck/drafts/memo_v4_1_2026-09-29/build_memo.js
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, AlignmentType, LevelFormat,
  HorizontalPositionRelativeFrom, VerticalPositionRelativeFrom, HorizontalPositionAlign,
  TextWrappingType, TextWrappingSide, Table, TableRow, TableCell, WidthType, BorderStyle,
} = require("docx");

const HERE = __dirname;
const ROOT = path.resolve(HERE, "../../..");
const FONT = "Aptos";
const SIZE = 22; // half-points = 11pt
const SPACING = { after: 80, line: 252 }; // 1.05 lines; 4pt after (v4: 5pt) to hold two pages in Word

const graphs = process.env.FLOAT ? {
  // paragraph prefix that anchors the floating chart -> image file
  "**Why the bundle creates": path.join(ROOT, "deck/Graphs/pm_feedback_v4_1/graph1_captioned.png"),
  "**Our proof:": path.join(ROOT, "deck/Graphs/pm_feedback_v4_1/graph2_captioned.png"),
} : {};
const IMG_W_IN = parseFloat(process.env.IMG_W_IN || "3.45");
const TWOUP_W_IN = parseFloat(process.env.TWOUP_W_IN || "3.70");

function inlineImage(file, wIn) {
  const buf = fs.readFileSync(file);
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  const wpx = Math.round(wIn * 96), hpx = Math.round(wpx * h / w);
  return new ImageRun({ type: "png", data: buf, transformation: { width: wpx, height: hpx } });
}

function twoUp() {
  const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
  const borders = { top: none, bottom: none, left: none, right: none };
  const colW = 5400; // DXA, two columns = 10800 = 7.5in
  const cell = (file) => new TableCell({
    borders, width: { size: colW, type: WidthType.DXA }, margins: { top: 0, bottom: 0, left: 0, right: 0 },
    children: [new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 0 }, children: [inlineImage(file, TWOUP_W_IN)] })],
  });
  return new Table({
    width: { size: 10800, type: WidthType.DXA }, columnWidths: [colW, colW],
    borders: { top: none, bottom: none, left: none, right: none, insideHorizontal: none, insideVertical: none },
    rows: [new TableRow({ cantSplit: true, children: [
      cell(path.join(ROOT, "deck/Graphs/pm_feedback_v4_1/graph1_captioned.png")),
      cell(path.join(ROOT, "deck/Graphs/pm_feedback_v4_1/graph2_captioned.png")),
    ] })],
  });
}

function runs(text, extra = {}) {
  // **bold** and *italic* spans
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*)/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), font: FONT, size: SIZE, ...extra }));
    const t = m[0];
    if (t.startsWith("**")) out.push(new TextRun({ text: t.slice(2, -2), bold: true, font: FONT, size: SIZE, ...extra }));
    else out.push(new TextRun({ text: t.slice(1, -1), italics: true, font: FONT, size: SIZE, ...extra }));
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), font: FONT, size: SIZE, ...extra }));
  return out;
}

function floatingImage(file) {
  const buf = fs.readFileSync(file);
  // PNG width/height from IHDR
  const w = buf.readUInt32BE(16), h = buf.readUInt32BE(20);
  const wpx = Math.round(IMG_W_IN * 96), hpx = Math.round(wpx * h / w);
  return new ImageRun({
    type: "png", data: buf, transformation: { width: wpx, height: hpx },
    floating: {
      horizontalPosition: { relative: HorizontalPositionRelativeFrom.MARGIN, align: HorizontalPositionAlign.RIGHT },
      verticalPosition: { relative: VerticalPositionRelativeFrom.PARAGRAPH, offset: 0 },
      wrap: { type: TextWrappingType.SQUARE, side: TextWrappingSide.LEFT },
      margins: { left: 114300, top: 0, bottom: 45720 },
    },
  });
}

const lines = fs.readFileSync(path.join(HERE, "memo_v4_1_text.md"), "utf8").split("\n");
const children = [];
lines.forEach((line, i) => {
  if (!line.trim()) return;
  if (line.trim() === "[[GRAPHS]]") { children.push(twoUp()); children.push(new Paragraph({ spacing: { after: 60 }, children: [] })); return; }
  if (i === 0) {
    children.push(new Paragraph({ spacing: { after: 60 }, children: [new TextRun({ text: line, bold: true, font: FONT, size: 24 })] }));
    return;
  }
  let m;
  if ((m = line.match(/^   - (.*)$/))) {
    children.push(new Paragraph({ numbering: { reference: "bul", level: 1 }, alignment: AlignmentType.JUSTIFIED, spacing: { after: 40, line: 252 }, children: runs(m[1]) }));
  } else if ((m = line.match(/^- (.*)$/))) {
    children.push(new Paragraph({ numbering: { reference: "bul", level: 0 }, alignment: AlignmentType.JUSTIFIED, spacing: { after: 40, line: 252 }, children: runs(m[1]) }));
  } else if ((m = line.match(/^\d+\. (.*)$/))) {
    children.push(new Paragraph({ numbering: { reference: "num", level: 0 }, alignment: AlignmentType.JUSTIFIED, spacing: { after: 40, line: 252 }, children: runs(m[1]) }));
  } else {
    const kids = [];
    for (const [prefix, file] of Object.entries(graphs)) if (line.startsWith(prefix)) kids.push(floatingImage(file));
    kids.push(...runs(line));
    children.push(new Paragraph({ alignment: i === 2 ? AlignmentType.LEFT : AlignmentType.JUSTIFIED, spacing: SPACING, children: kids }));
  }
});

const doc = new Document({
  creator: "Caimanes",
  styles: { default: { document: { run: { font: FONT, size: SIZE } } } },
  numbering: {
    config: [
      { reference: "bul", levels: [
        { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 270, hanging: 180 } } } },
        { level: 1, format: LevelFormat.BULLET, text: "–", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 180 } } } },
      ] },
      { reference: "num", levels: [
        { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 270, hanging: 270 } } } },
      ] },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 720, right: 720, bottom: 720, left: 720 } } },
    children,
  }],
});

const out = path.join(HERE, process.env.OUT_NAME || "ABNB_Citadel_Pitch_Memo_v4_1.docx");
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(out, b); console.log("wrote", out); });
