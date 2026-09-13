"""Render the editable, restricted Markdown memo into exactly two PDF pages."""
from pathlib import Path
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak, KeepTogether
from pypdf import PdfReader

NAVY = colors.HexColor("#142D44")
TEAL = colors.HexColor("#176C70")
GRAY = colors.HexColor("#52616E")
PALE = colors.HexColor("#EDF3F5")


def inline(value):
    value = escape(value)
    value = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", value)
    value = re.sub(r"`([^`]+)`", r"<font name='Courier'>\1</font>", value)
    return value


def render(source: Path, output: Path):
    text = source.read_text(encoding="utf-8")
    if text.count("<!-- PAGEBREAK -->") != 1:
        raise ValueError("Memo source must explicitly contain one page break")
    styles = {
        "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=21, leading=24, textColor=NAVY, spaceAfter=9),
        "head": ParagraphStyle("head", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=TEAL, spaceBefore=9, spaceAfter=5, keepWithNext=True),
        "body": ParagraphStyle("body", fontName="Helvetica", fontSize=10.5, leading=13.5, textColor=NAVY, spaceAfter=6),
        "small": ParagraphStyle("small", fontName="Helvetica", fontSize=9, leading=11.5, textColor=GRAY, spaceAfter=5),
        "cell": ParagraphStyle("cell", fontName="Helvetica", fontSize=8.7, leading=10.6, textColor=NAVY),
        "th": ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=8.6, leading=10.6, textColor=colors.white),
    }
    doc = SimpleDocTemplate(str(output), pagesize=(8.5 * inch, 11 * inch),
                            leftMargin=0.60 * inch, rightMargin=0.60 * inch,
                            topMargin=0.54 * inch, bottomMargin=0.53 * inch,
                            title="Airbnb | Guide composition review", author="Citadel ABNB research - unsigned review")
    width = 7.30 * inch
    story = []
    paragraphs = []
    table_lines = []

    def flush_paragraph():
        if paragraphs:
            value = " ".join(paragraphs)
            kind = "small" if value.startswith(("Sources:", "Source:", "Notes:", "As of:", "Status:")) else "body"
            story.append(Paragraph(inline(value), styles[kind]))
            paragraphs.clear()

    def flush_table():
        if not table_lines:
            return
        rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in table_lines]
        rows = [r for r in rows if not all(re.fullmatch(r":?-+:?", c) for c in r)]
        n = len(rows[0])
        if any(len(r) != n for r in rows):
            raise ValueError("Ragged Markdown table")
        if n == 5:
            ratios = [0.31, 0.16, 0.17, 0.18, 0.18]
        elif n == 4:
            ratios = [0.40, 0.20, 0.20, 0.20]
        elif n == 2:
            ratios = [0.24, 0.76]
        else:
            ratios = [1 / n] * n
        formatted = [[Paragraph(inline(c), styles["th" if i == 0 else "cell"]) for c in r] for i, r in enumerate(rows)]
        table = Table(formatted, colWidths=[width * r for r in ratios], repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LINEBELOW", (0, -1), (-1, -1), 0.4, colors.HexColor("#CBD5DA")),
        ]))
        story.extend([table, Spacer(1, 7)])
        table_lines.clear()

    for line in text.splitlines():
        if line.startswith("|"):
            flush_paragraph()
            table_lines.append(line)
            continue
        flush_table()
        if not line.strip():
            flush_paragraph()
        elif line == "<!-- PAGEBREAK -->":
            flush_paragraph()
            story.append(PageBreak())
        elif line.startswith("# "):
            flush_paragraph()
            story.append(Paragraph(inline(line[2:]), styles["title"]))
        elif line.startswith("## "):
            flush_paragraph()
            story.append(Paragraph(inline(line[3:]), styles["head"]))
        else:
            paragraphs.append(line)
    flush_paragraph()
    flush_table()

    def page(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(TEAL)
        canvas.setLineWidth(1.2)
        canvas.line(0.60 * inch, 0.39 * inch, 7.90 * inch, 0.39 * inch)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(GRAY)
        canvas.drawString(0.60 * inch, 0.23 * inch, "ABNB | Unsigned benchmark | L3 conversion and FX/RNPL pending")
        canvas.drawRightString(7.90 * inch, 0.23 * inch, f"{doc.page} / 2")
        canvas.restoreState()

    doc.build(story, onFirstPage=page, onLaterPages=page)
    reader = PdfReader(str(output))
    if len(reader.pages) != 2:
        raise ValueError(f"Expected exactly two pages; rendered {len(reader.pages)}")
    for i, p in enumerate(reader.pages, 1):
        extracted = p.extract_text()
        if len(extracted) < 300 or "L3 conversion and FX/RNPL pending" not in extracted:
            raise ValueError(f"Incomplete page {i}")
    return {"pages": 2, "source": str(source), "pdf": str(output), "visual_inspection": "required"}
