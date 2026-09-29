# pitch_charts / two_pager_stylemd.R — the three two-pager charts on the $128 short case in the STYLE.md look (repo-root STYLE.md),
# with Airbnb-derived colours in the palette slots. One style, one file: the STYLE section at the top holds palette, fonts, sizes,
# theme, helpers, the audit registry and the save routine; each graph is a function below it.
# Run from the repo root:
#   python analysis/src/pitch_charts/short_case_inputs.py && Rscript analysis/src/pitch_charts/two_pager_stylemd.R
# Writes deck/figures/pitch_charts/two_pager_stylemd/graph{1,2,3}_*.png, every one 7.2 x 4.9 in = 2160 x 1470 px at 300 dpi.
# No takeaway line and no source on the images: both go in the document (deck/figures/pitch_charts/two_pager_stylemd/DOC_CAPTIONS.md).

suppressPackageStartupMessages({
  library(ggplot2); library(dplyr); library(tidyr); library(readr); library(scales)
  library(ragg); library(systemfonts); library(stringr)
})

args <- commandArgs(trailingOnly = FALSE)
here <- dirname(normalizePath(sub("--file=", "", args[grep("--file=", args)])))
ROOT <- normalizePath(file.path(here, "../../.."))
DATA <- file.path(ROOT, "data/processed/pitch_charts")
# Which numbers to draw: CHART_CASE=caimanes (default; the team model, model/Caimanes_Citadel_ABNB_Model.xlsx via caimanes_inputs.py)
# or CHART_CASE=short128 (48_short_case_v3 via short_case_inputs.py). Output goes to a folder per case.
CASE <- Sys.getenv("CHART_CASE", "caimanes")
IN <- list(caimanes = c(nights = "n07_nights_caimanes.csv", bridge = "r07_margin_bridge_caimanes.csv"),
           short128 = c(nights = "n06_nights_short.csv", bridge = "r06_margin_bridge_short.csv"))[[CASE]]
stopifnot(!is.null(IN))
OUT  <- file.path(ROOT, "deck/figures/pitch_charts", paste0("two_pager_stylemd_", CASE)); dir.create(OUT, recursive = TRUE, showWarnings = FALSE)
read_data <- function(f) suppressMessages(read_csv(file.path(DATA, f), show_col_types = FALSE))

# ======================================================================================================================
# STYLE
# ======================================================================================================================
# Palette: STYLE.md's five-slot structure, Airbnb hues. Validated with the dataviz skill's validate_palette.js (light mode):
# worst adjacent CVD dE 10.7 (deutan), normal-vision floor 22.7, all slots in the lightness band. GREEN sits at 2.96:1 on
# white, so every GREEN mark carries a value label (the validator's "relief").
GREEN  <- "#00A699"   # Babu: adds to margin
RED    <- "#E0484E"   # Rausch, deepened for contrast: the product bundle, cuts to margin, "both guides missed"
VIOLET <- "#7B4BC9"   # Middle East
AMBER  <- "#D97500"   # World Cup
DEEP   <- "#9E1C23"   # RNPL cancellations (the bundle's own tail, so a darker red)
INK <- "#000000"; AXIS <- "#000000"; TITLE <- "#4a4a4a"; MUTED <- "#7a7a7a"; GRIDC <- "#e4e4e4"; LGRAY <- "#cfcfcf"
BAND <- "#f0f0f0"; CONTEXT <- "#bdbdbd"; SURFACE <- "#FFFFFF"; STAMP <- "#B00020"
# Type and strokes, authored for two-up display (7.2in canvas shown at ~3.2in): TS scales text, LW lines and markers.
TS <- 1.7; LW <- 1.5
PT_TITLE <- 7.8 * TS; PT_KEY <- 8 * TS; PT_AXIS <- 7.6 * TS; PT_NOTE <- 6.6 * TS; PT_LABEL <- 6.9 * TS
MM <- 1 / .pt                                     # ggplot text size is in mm
PT_END <- 1.3; PT_DOT <- 2.3
W <- 7.2; H <- 4.9
Y_POS <- "left"
# Fonts: titles in Helvetica (Arial on Windows, which has no Helvetica); everything inside the graph in Calibri.
# Calibri ships with Windows here (C:/Windows/Fonts/calibri*.ttf), so ragg finds it as a system font; STYLE.md's register_font step
# is only needed where Calibri lives inside the Office bundle.
stopifnot(nrow(systemfonts::match_fonts("Calibri")) == 1, grepl("calibri", systemfonts::match_fonts("Calibri")$path, ignore.case = TRUE))
F_TITLE <- "Arial"; F_BODY <- "Calibri"

pct  <- function(v) paste0(v, "%")
spct <- function(v) ifelse(v > 0, paste0("+", v, "%"), ifelse(v < 0, paste0("−", abs(v), "%"), "0%"))
spct1 <- function(x) ifelse(x > 0.049, sprintf("+%.1f%%", x), ifelse(x < -0.049, sprintf("−%.1f%%", abs(x)), "0.0%"))
bp <- function(x) paste0(ifelse(x > 0, "+", ifelse(x < 0, "−", "")), abs(round(x * 100)), "bp")
sy <- function(...) scale_y_continuous(..., position = Y_POS)
lab_note <- function(x, y, text, hjust = 0) annotate("text", x = x, y = y, label = text, hjust = hjust, family = F_BODY,
                                                     size = PT_NOTE * MM, colour = MUTED, lineheight = 0.9)

theme_chart <- function(grid = "y", key = TRUE) {
  t <- theme_minimal(base_family = F_BODY, base_size = PT_AXIS) +
    theme(
      plot.title = element_text(family = F_TITLE, face = "bold", size = PT_TITLE, colour = TITLE, hjust = 0, margin = margin(b = 6)),
      plot.title.position = "plot", plot.caption.position = "plot",
      plot.caption = element_text(family = F_BODY, size = PT_NOTE, colour = STAMP, hjust = 0, margin = margin(t = 6)),
      axis.text = element_text(family = F_BODY, colour = AXIS, size = PT_AXIS),
      axis.title = element_blank(), axis.ticks = element_blank(), axis.line = element_blank(),
      panel.grid = element_blank(),
      plot.background = element_rect(fill = SURFACE, colour = NA), panel.background = element_rect(fill = SURFACE, colour = NA),
      strip.text = element_text(family = F_BODY, face = "bold", colour = INK, size = PT_KEY, hjust = 0),
      legend.position = if (key) "top" else "none", legend.justification = "left", legend.location = "plot",
      legend.direction = "horizontal", legend.title = element_blank(),
      legend.text = element_text(family = F_BODY, colour = INK, size = PT_KEY, margin = margin(l = 4, r = 14)),
      legend.key.size = unit(0.42, "cm"), legend.margin = margin(0, 0, 8, 0), legend.box.spacing = unit(0, "pt"),
      legend.box = "horizontal", legend.box.just = "left", legend.spacing.x = unit(2, "pt"),
      plot.margin = margin(12, 16, 10, 2)                       # left ~0 so the title aligns with the doc caption
    )
  gl <- element_line(colour = GRIDC, linewidth = 0.3 * LW)
  if (grid == "y") t <- t + theme(panel.grid.major.y = gl)
  if (grid == "x") t <- t + theme(panel.grid.major.x = gl)
  t
}

# Audit registry: level OK renders clean; anything else prints a corner tag and folds the reason into the caption, so an
# unresolved chart cannot ship silently. Clear an entry only when the item is fixed.
VERIFY <- list(
  graph1 = list(level = "OK", why = ""),
  graph2 = list(level = "OK", why = "World Cup +0.5pt in 2Q26 kept by team decision, 28 Sep 2026 (host-market reviews measure ~0.1pt, PR #68)."),
  graph3 = list(level = "OK", why = "")
)
verify_overlay <- function(p, key) {
  v <- VERIFY[[key]]
  if (is.null(v) || v$level == "OK") return(p)
  p + labs(caption = str_wrap(paste0(v$level, ": ", v$why), 110)) +
    annotate("label", x = Inf, y = Inf, label = v$level, hjust = 1.05, vjust = 1.1, fill = STAMP, colour = SURFACE,
             family = F_TITLE, fontface = "bold", size = PT_NOTE * MM, linewidth = 0)
}
save_chart <- function(p, key, file) {
  p <- verify_overlay(p, key)
  ggsave(file.path(OUT, file), p, device = agg_png, width = W, height = H, units = "in", dpi = 300, bg = SURFACE)
  message("saved two_pager_stylemd/", file, "  [", VERIFY[[key]]$level, "]")
}

# ======================================================================================================================
# Graph 1 — Day-1 return vs QQQ at each print, grouped by what the print guided
# Doc caption: "When both guides miss, the stock has fallen every time (5 of 5, −8.0% average)."
# Source line: Airbnb shareholder letters; consensus at each print (LSEG, StreetAccount, FactSet); closing prices.
# ======================================================================================================================
graph_01_both_guides <- function() {
  gates <- read_data("s04_two_gates.csv") |> filter(guide != "uncoded") |>
    mutate(key = paste(guide, nights_down), hot = key == "below 1",
           lab = c("below 1" = "Revenue guide below Street,\nnights guided lower", "below 0" = "Revenue guide below Street,\nnights not lower",
                   "above 1" = "Revenue guide above Street,\nnights guided lower", "above 0" = "Revenue guide above Street,\nnights not lower")[key],
           y = c("below 1" = 4, "below 0" = 3, "above 1" = 2, "above 0" = 1)[key])
  pts <- gates |> select(key, y, hot, prints) |> mutate(prints = str_split(prints, " (?=\\dQ)")) |> unnest(prints) |>
    mutate(q = word(prints, 1), v = as.numeric(sub("−", "-", word(prints, 2))),
           grp = factor(ifelse(hot, "Both guides missed", "Other prints"), levels = c("Both guides missed", "Other prints")))
  # one label per dot (overlapping dots share one); a label flips above its dot when the last label below is too close
  GAP <- 2.9
  lb <- pts |> arrange(y, v) |> group_by(y, hot) |> mutate(cl = cumsum(v - lag(v, default = -Inf) >= 0.6)) |>
    group_by(y, hot, cl) |> summarise(v = mean(v), q = paste(q, collapse = ", "), .groups = "drop") |> arrange(y, v) |> mutate(up = FALSE)
  last <- c(below = -Inf, above = -Inf); row <- NA
  for (i in seq_len(nrow(lb))) {
    if (!identical(lb$y[i], row)) { last <- c(below = -Inf, above = -Inf); row <- lb$y[i] }
    lb$up[i] <- lb$v[i] - last[["below"]] < GAP && lb$v[i] - last[["above"]] >= GAP
    last[[if (lb$up[i]) "above" else "below"]] <- lb$v[i]
  }
  lb <- lb |> mutate(ly = ifelse(up, y + 0.3, y - 0.3))
  p <- ggplot() +
    annotate("rect", xmin = -Inf, xmax = Inf, ymin = 3.52, ymax = 4.48, fill = BAND) +
    geom_vline(xintercept = 0, colour = LGRAY, linewidth = 0.5 * LW) +
    geom_segment(data = gates, aes(x = mean, xend = mean, y = y - 0.17, yend = y + 0.17, linetype = "Group average"), colour = INK, linewidth = 0.8 * LW) +
    geom_point(data = pts, aes(x = v, y = y, colour = grp), size = PT_DOT * LW) +
    geom_label(data = lb |> filter(hot), aes(x = v, y = ly, label = q), colour = INK, fill = BAND, family = F_BODY, size = PT_LABEL * 0.88 * MM,
               linewidth = 0, label.padding = unit(0.05, "lines")) +
    geom_label(data = lb |> filter(!hot), aes(x = v, y = ly, label = q), colour = MUTED, fill = SURFACE, family = F_BODY, size = PT_LABEL * 0.88 * MM,
               linewidth = 0, label.padding = unit(0.05, "lines")) +
    geom_text(data = gates, aes(x = 27.5, y = y, label = sprintf("%s average\n%d of %d fell", spct1(mean), n_neg, n), fontface = ifelse(hot, "bold", "plain")),
              hjust = 1, family = F_BODY, size = PT_LABEL * MM, colour = INK, lineheight = 0.9) +
    scale_colour_manual(values = c("Both guides missed" = RED, "Other prints" = CONTEXT)) +
    scale_linetype_manual(values = c("Group average" = "solid")) +
    guides(colour = guide_legend(order = 1, override.aes = list(size = 3)),
           linetype = guide_legend(order = 2, override.aes = list(linewidth = 0.8 * LW), keywidth = unit(0.6, "cm"))) +
    sy(breaks = gates$y, labels = gates$lab, expand = expansion(add = c(0.32, 0.12))) +
    scale_x_continuous(labels = spct, breaks = seq(-15, 15, 5), limits = c(-17, 27.5), expand = expansion(add = 0)) +
    labs(title = "ABNB day-1 return vs QQQ at each print, by what the print guided") +
    theme_chart(grid = "x") + theme(axis.text.y = element_text(family = F_BODY, colour = INK, size = PT_AXIS * 0.92, hjust = 0, lineheight = 0.95))
  save_chart(p, "graph1", "graph1_both_guides_miss.png")
}

# ======================================================================================================================
# Graph 2 — Nights and Seats Booked, year-over-year growth and its parts, 1Q25-4Q27 (forecast = the $128 short case)
# Doc caption: "As the bundle laps and RNPL cancellations arrive, nights growth falls to 5-7% against the Street's 10-11%."
# Source line: Airbnb letters and earnings calls; Bloomberg consensus (12 Sep 2026); team nights model and RNPL cohort engine.
# ======================================================================================================================
graph_02_nights <- function() {
  nd <- read_data(IN[["nights"]]) |> filter(!str_detect(quarter, "24$")) |> mutate(x = row_number(), fc = kind == "forecast")
  xf <- min(nd$x[nd$fc])
  NCOL <- c(Underlying = CONTEXT, Bundle = RED, `RNPL cancels` = DEEP, `World Cup` = AMBER, `Middle East` = VIOLET)
  dl <- nd |> transmute(x, fc, Underlying = underlying, Bundle = bundle, `RNPL cancels` = cancel, `World Cup` = wc, `Middle East` = me) |>
    pivot_longer(-c(x, fc), names_to = "comp", values_to = "v") |> filter(v != 0) |> mutate(comp = factor(comp, levels = names(NCOL))) |>
    arrange(x, v < 0, comp) |> group_by(x) |>
    mutate(ptop = sum(v[v > 0]), hi = ifelse(v > 0, cumsum(pmax(v, 0)), ptop + (cumsum(pmin(v, 0)) - v)), lo = hi - abs(v), neg = v < 0) |> ungroup()
  stopifnot(all(abs((dl |> group_by(x) |> summarise(b = min(c(lo[neg], ptop[1]))) |> arrange(x) |> pull(b)) - nd$total) < 1e-6))
  st <- nd |> filter(!is.na(street))
  top <- dl |> group_by(x) |> summarise(y = first(ptop)) |> left_join(nd |> select(x, total), by = "x")
  p <- ggplot() +
    annotate("rect", xmin = xf - 0.5, xmax = max(nd$x) + 0.5, ymin = 0, ymax = Inf, fill = BAND, alpha = 0.6) +
    lab_note(xf - 0.38, 13.3, "Forecast: pale bars") +
    geom_rect(data = dl |> filter(!neg), aes(xmin = x - 0.36, xmax = x + 0.36, ymin = lo, ymax = hi, fill = comp, alpha = fc), colour = SURFACE, linewidth = 0.25 * LW) +
    geom_rect(data = dl |> filter(neg), aes(xmin = x - 0.36, xmax = x + 0.36, ymin = lo, ymax = hi, fill = comp, colour = comp), alpha = 0.2, linewidth = 0.4 * LW, linetype = "22") +
    geom_hline(yintercept = 0, colour = INK, linewidth = 0.6 * LW) +
    geom_segment(data = st, aes(x = x - 0.46, xend = x + 0.46, y = street, yend = street, linetype = "Street"), colour = INK, linewidth = 0.55 * LW) +
    geom_text(data = st, aes(x = x, y = street + 0.55, label = sprintf("Street %.1f", street)), family = F_BODY, size = PT_LABEL * MM, colour = INK) +
    geom_point(data = nd, aes(x = x, y = total), size = PT_END * LW, colour = INK) +
    geom_text(data = top, aes(x = x, y = y + 0.6, label = sprintf("%.1f", total)), family = F_BODY, fontface = "bold", size = PT_LABEL * MM, colour = INK) +
    scale_fill_manual(values = NCOL) + scale_colour_manual(values = NCOL, guide = "none") +
    scale_alpha_manual(values = c(`FALSE` = 1, `TRUE` = 0.5), guide = "none") +
    scale_linetype_manual(values = c("Street" = "22")) +
    guides(fill = guide_legend(order = 1, override.aes = list(alpha = 1, colour = NA, linetype = 0)),
           linetype = guide_legend(order = 2, override.aes = list(linewidth = 0.55 * LW), keywidth = unit(0.7, "cm"))) +
    scale_x_continuous(breaks = nd$x, labels = nd$quarter, expand = expansion(add = 0.45)) +
    sy(labels = pct, breaks = seq(0, 12, 2), limits = c(0, 13.6), expand = expansion(add = c(0, 0.2))) +
    labs(title = "Nights and Seats Booked, year-over-year growth and its parts, %") +
    theme_chart(grid = "y") +
    theme(axis.text.x = element_text(family = F_BODY, colour = AXIS, size = PT_AXIS * 0.9),
          legend.text = element_text(family = F_BODY, colour = INK, size = PT_KEY * 0.86, margin = margin(l = 3, r = 8)))
  p <- p + annotate("text", x = 0.62, y = -Inf, label = "", size = 0)   # keeps the baseline flush with the x labels
  save_chart(p, "graph2", "graph2_nights_bundle_separated.png")
}

# ======================================================================================================================
# Graph 3 — Adjusted EBITDA margin, Street consensus to our model (3Q26, 4Q26, FY27), four steps each
# Doc caption: "Lower revenue and S&M take our margin below the Street in every period; hosting & AI compute adds to the gap."
# Source line: LSEG consensus (13 Sep 2026); Airbnb filings; team model. Other costs = payments, support payroll, product development, G&A.
# ======================================================================================================================
graph_03_margin <- function() {
  KEEP <- c("Lower revenue (costs flex down)" = "Lower revenue", "Sales & marketing" = "Sales & marketing", "Hosting & AI compute" = "Hosting & AI compute",
          "AI support automation" = "AI support savings")
  br <- read_data(IN[["bridge"]]) |>
    mutate(step = case_when(kind == "total" ~ label, label %in% names(KEEP) ~ unname(KEEP[label]), TRUE ~ "Other costs (net)")) |>
    group_by(period, step, kind) |> summarise(value_pp = sum(value_pp), .groups = "drop") |>
    mutate(ord = match(step, c("Street consensus", "Lower revenue", "Sales & marketing", "Hosting & AI compute", "AI support savings", "Other costs (net)", "Our model"))) |>
    arrange(period, ord) |> group_by(period) |>
    mutate(end = ifelse(kind == "total", value_pp, first(value_pp) + cumsum(ifelse(kind == "step", value_pp, 0))),
           start = ifelse(kind == "total", 0, end - value_pp), y = n() - row_number() + 1, next_y = lead(y),
           dir = case_when(kind == "total" ~ "total", value_pp >= 0 ~ "Adds to margin", TRUE ~ "Cuts margin")) |> ungroup()
  chk <- br |> group_by(period) |> summarise(d = abs(end[step == "Our model"] - end[step == "Other costs (net)"]))
  stopifnot(all(chk$d < 1e-9))
  steps <- br |> filter(kind == "step"); tots <- br |> filter(kind == "total"); conn <- br |> filter(!is.na(next_y))
  span <- br |> group_by(period) |> summarise(lo = min(c(start[kind == "step"], end)), hi = max(c(start[kind == "step"], end)), .groups = "drop") |>
    mutate(pad = (hi - lo) * 0.18)
  lab_df <- steps |> left_join(span, by = "period") |>
    mutate(x = ifelse(dir == "Adds to margin", pmax(start, end) + pad * 0.1, pmin(start, end) - pad * 0.1), hj = ifelse(dir == "Adds to margin", 0, 1), txt = bp(value_pp))
  tot_df <- tots |> left_join(span, by = "period") |> mutate(x = end + (hi - lo) * 0.08, txt = sprintf("%.1f%%", end))
  ylabs <- br |> distinct(y, step)
  p <- ggplot() +
    geom_blank(data = span, aes(x = lo - pad * 3.4, y = 1)) + geom_blank(data = span, aes(x = hi + pad * 3.4, y = 1)) +
    geom_segment(data = conn, aes(x = end, xend = end, y = y - 0.34, yend = next_y + 0.34), colour = LGRAY, linewidth = 0.3 * LW) +
    geom_rect(data = steps, aes(xmin = pmin(start, end), xmax = pmax(start, end), ymin = y - 0.34, ymax = y + 0.34, fill = dir)) +
    geom_point(data = tots, aes(x = end, y = y), colour = INK, size = PT_END * LW) +
    geom_text(data = lab_df, aes(x = x, y = y, label = txt, hjust = hj), family = F_BODY, size = PT_LABEL * MM, colour = INK) +
    geom_text(data = tot_df, aes(x = x, y = y, label = txt), hjust = 0, family = F_BODY, fontface = "bold", size = PT_LABEL * 1.15 * MM, colour = INK) +
    scale_fill_manual(values = c("Adds to margin" = GREEN, "Cuts margin" = RED)) +
    sy(breaks = ylabs$y, labels = ylabs$step, expand = expansion(add = 0.5)) +
    scale_x_continuous(labels = pct, breaks = scales::breaks_pretty(n = 4), expand = expansion(mult = 0)) +
    facet_wrap(~period, nrow = 1, scales = "free_x") + coord_cartesian(clip = "off") +
    labs(title = "Adjusted EBITDA margin, Street consensus to our model, %") +
    theme_chart(grid = "x") +
    theme(axis.text.y = element_text(family = F_BODY, colour = INK, size = PT_AXIS * 0.92, hjust = 0), panel.spacing = unit(1.6, "lines"),
          axis.text.x = element_text(family = F_BODY, colour = MUTED, size = PT_AXIS * 0.85))
  save_chart(p, "graph3", "graph3_margin_bridges.png")
}

graph_01_both_guides()
graph_02_nights()
graph_03_margin()
message("done: ", OUT)
