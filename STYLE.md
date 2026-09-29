# Style — FINAL (2026-07-28)

One style, one file. The Bloomberg News / Businessweek idiom is the finalized
look for the exhibit pack, and it lives **inside
`charts.R`** — palette, theme, headline block, save routine and all twelve
graph functions in a single self-contained script:

```bash
Rscript charts.R     # -> graphs/
```

The old style-module system (`style_essay.R`, `style_bloomberg.R`,
`style_terminal.R`, the `STYLE=` env var) is retired; the modules are parked in
`_retired_styles/` and nothing reads them. To change the look, edit the STYLE
section at the top of `charts.R`. To change a graph, edit its function. There is
no second place to look.

## The look

| | |
|---|---|
| Top of figure | the descriptive title (no rule above it) — the PNGs sit in a Google-Doc sandwich: the doc's bold takeaway line above, the on-image title saying what the graph is, the source line below |
| Title | DESCRIPTIVE — what the graph is, units included — set SMALLER and GREY (#4a4a4a, 9.5pt-scale Helvetica bold) so it defers to the doc's bold black caption above the image |
| Key | for line charts: a swatch + series-name row under the title (`theme_chart(key = TRUE)`), replacing in-plot line labels; a measure note can ride on its left via the legend title (chart 1) |
| Y axis | **left-hand side** (2026-07-28 — the right-side Bloomberg tell confused two-up pairings), no axis line, no ticks, no title. Always via `sy()` / `sy_log10()`, which pin the side via `Y_POS` |
| X baseline | solid black, heavier than the grid |
| Grid | horizontal hairlines only (`theme_chart("x")` flips for horizontal bars; `"none"` for stacked areas) |
| Type | TWO FONTS: titles in Helvetica (the Bloomberg idiom); everything inside the graph — axes, ticks, annotations, key text — in **Calibri**, the font Nicholas Hamilton's paper uses (Word/Excel default) |
| Output | `graphs/`, EVERY png exactly 7.2 x 4.9in = 2160 x 1470 px (300 dpi), chart fills the canvas — no filler, no per-chart heights. Left margin ~0 so titles left-align with the doc caption above; first ticks protected by per-chart x-expansion. Displays at ~3.2in two-up |

There is no per-chart height override. It existed twice and was removed twice:
bottom filler under a top-aligned chart reads as an uncentered, broken image
in the doc (2026-07-28). If a chart's ink looks disproportionate,
fix its own layout — labels inside the plot, tight x-expansions — never the
canvas. Width and height never change — the doc lays charts out two-up, and
consistent size is what makes that read as one document.

## The palette

Five categorical slots plus neutrals. Slot names are semantic, not literal —
`RED` is the China slot in every chart, `BLUE` the US slot, and the actual hex
behind a slot is the style's business.

```
GREEN  #00A3A1  teal            INK    #000000   text, the FCF line
BLUE   #0F62FE  Bloomberg blue  AXIS   #000000   axis text, annotations (black)
RED    #D4145A  magenta-red     MUTED  #7a7a7a   captions, context series
VIOLET #7B4BC9  purple          GRIDC  #e4e4e4   gridlines
AMBER  #E85D00  orange          LGRAY  #cfcfcf   connectors, reference lines
                                BAND   #f0f0f0   event bands (GFC, COVID, wars)
```

**The order — teal, blue, red, purple, amber — is not arbitrary and must not be
re-ordered.** It clears the colourblind-separation checks on adjacent pairs:
worst adjacent ΔE 9.8 (deuteranopia) / 18.6 (normal vision), all five ≥ 3:1 on
white. If you add a sixth series, append rather than insert, and re-run the
check. Grey is deliberately not a categorical slot — it carries "everything
else" (Rest of world, the EU aggregate, the covered-by-FCF band) and reads as
recessive, which is the point.

## Rules that are not negotiable

**Single y-axis, always.** No chart has two y-scales. Where an exhibit needs two
measures of different scale (chart 7), it gets two stacked panels via
`facet_wrap(ncol = 1, scales = "free_y")`. Two axes let a reader infer a
relationship from where you happened to set the scales; two panels don't.

**Identity is never colour alone.** Line charts name their series in the key
row under the title (`theme_chart(key = TRUE)`) — never with floating in-plot
labels, which collide at two-up sizes and cost a placement fight per chart.
Stacked areas still label inside their bands (`lab_series`, chart 2), and the
dumbbell keeps its Before/After column headers (chart 6). Contextual notes
(`lab_note`) stay in-plot.

**Colour follows the entity.** China is the `RED` slot everywhere, the US
`BLUE`, Japan `GREEN`, Germany `VIOLET`. If a chart drops a series, the
survivors keep their colours.

**Forecasts are visibly forecasts.** Dashed segments (`linetype = "22"` or
`"12"`), pale fills (`alpha = 0.5`), open markers, and a note saying so.
De-escalation event markers draw dotted teal against dashed grey escalations
(chart 4).

**Endpoint markers earn their label.** A terminal dot on a line appears only
when its value label sits right at the point (charts 11, 14); an endpoint that
isn't labelled gets no marker. And dots stay small — every endpoint dot draws
at `PT_END` (1.3, pre-`LW`) in `charts.R`, just above the line weight, so it
reads as the end of the line rather than a data-point callout (2026-07-28).

**No captions on the images.** Sources and captions live in the Google Doc
next to each chart (decided 2026-07-28). Full provenance lives in the
chart's comment block, the CSV headers and DATA.md; forecast and splice markers
are drawn on the plot itself where a reader needs them. The audit stamp still
prints on anything unresolved, so a weak chart can't ship silently — stamps
disappear as ACTIONS items close. When writing doc source lines: Bloomberg only
for charts genuinely built on Bloomberg data (see the ledger in `charts.R`).

**Sized for two-up in the doc.** The PNGs sit two per row across an 8.5in page
(~3.2in each after margins — a 2.2x shrink from the 7.2in canvas), so all type
and strokes are authored scaled up via `TS` (text, 1.7x) and `LW` (lines and
markers, 1.5x) in `charts.R`. Effective sizes after the shrink: axis text ~7pt,
headline ~9pt bold, series labels ~7pt. Never add a label without re-checking
the render at ~45% zoom — collisions appear at these sizes that a full-size
look misses.

**Nothing visual is hard-coded in a graph function.** Colours, fonts, sizes and
the axis side come from the named constants, `theme_chart()`, `sy()` and the
helpers — not even `"white"` is allowed raw: a separator between stacked bars is
`SURFACE`. This is what keeps twelve charts reading as one system.

**No fabricated sources.** No Bloomberg wordmark, and no "Source: Bloomberg" on
charts whose data came from the IMF, World Bank, Eurostat, USGS or Treasury.
Imitating the idiom is fine; attributing our numbers to a wire service that
never produced them is not — in a competition submission, a judge who checks
the terminal and can't find the series will notice. Charts 4 and 10 carry
Bloomberg today because that is genuinely where their data came from; every tab
wired in from the terminal sheet (`fetch_sheet.py`) earns its chart the
Bloomberg line automatically.

## The title + key block

`HEAD` in `charts.R` holds one DESCRIPTIVE title per chart ("Gallium 99.99%
spot price, $/kg"), drawn bold at the top of the image — the layer that says
what the graph is. The doc supplies the takeaway line above the image and the
source line below it. No rule above the title: the doc's own text is the only
chrome up there.

The key row comes from ggplot's own legend, restyled by `theme_chart(key =
TRUE)`: horizontal, left-aligned under the title, swatch + name in Calibri.
Series order and display names are set with `breaks =` / `labels =` in the
chart's colour scale. Because it is a real legend, it can never collide with
data — that is the point.

## Fonts

Titles: Helvetica (system). Graph internals: Calibri — which ships INSIDE
Microsoft Office, not system-wide, so `charts.R` registers it from Word's
bundle (`systemfonts::register_font`, path in `DFONTS`) and `save_chart()`
renders through `ragg::agg_png`. The default png device cannot see registered
fonts and silently falls back to Helvetica — if the output ever stops looking
like Calibri, check that Office is still installed at the `DFONTS` path.

## The audit stamp

`save_chart()` calls `verify_overlay(p, key)`, which reads the `VERIFY` registry
in `charts.R` and prints the chart's audit verdict onto the PNG — a corner tag
plus the reason folded into the caption. Not optional: a chart cannot ship
silently unverified. Clean charts (level OK, no caption flag) render unstamped.
Evidence lives in [AUDIT.md](AUDIT.md), the work list in [ACTIONS.md](ACTIONS.md).

## Helpers

| Helper | Use |
|---|---|
| `read_data(f)` | reads `data/f`, stripping the `#` provenance header line |
| `save_chart(p, file, w, h)` | attaches headline + stamp, writes to `graphs/`, logs it |
| `sy(...)` / `sy_log10(...)` | y scales, pinned to the left-hand side via `Y_POS` |
| `theme_chart(grid, key)` | the theme; `grid` = `"y"` (default), `"x"`, `"none"`; `key = TRUE` adds the series-key row |
| `pct(v)` | `"10%"` axis labels |
| `lab_series(x, y, text, colour)` | bold direct series label |
| `lab_note(x, y, text)` | grey annotation, tighter line height |

## Adding a chart

1. Put the data in `data/` as a CSV whose `#` header line names the source, the
   pull date and any caveat. Document it in `DATA.md`.
2. Write `graph_NN_short_name()` in `charts.R`, in doc order. Head it with a
   comment block containing **the essay caption verbatim** plus the source line —
   that comment is the index other people search.
3. Use the helpers and constants only (see the non-negotiables).
4. Add a `VERIFY` entry (be honest — that is the audit trail), a descriptive
   title to `HEAD`, and the call at the bottom of the file. Line chart? Use
   `theme_chart(key = TRUE)` and set series names via the colour scale.
5. Render and **look at the PNG**. Label collisions, clipped text at the panel
   edge, and legends sitting on data are the three failures no code review
   catches.
