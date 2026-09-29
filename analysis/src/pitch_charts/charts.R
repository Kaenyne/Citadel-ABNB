# pitch_charts / charts.R — chart candidates for the two-pager: stock reaction at prints (s), revenue drivers (r),
# nights and the RNPL bundle (n). Run from the repo root after prepare_data.py:
#   Rscript analysis/src/pitch_charts/charts.R
# Writes deck/figures/pitch_charts/<topic>/*.png (6.5 x 3.6 in, 300 dpi). Same house style as the thesis-3 set
# (margin_build/47_pitch_charts on krish/cost-leg): Figtree (SIL OFL, bundled in fonts/), Airbnb palette.

suppressPackageStartupMessages({
  library(ggplot2); library(dplyr); library(tidyr); library(readr); library(scales)
  library(ggtext); library(ragg); library(systemfonts); library(forcats); library(stringr); library(ggrepel)
})

args <- commandArgs(trailingOnly = FALSE)
here <- dirname(normalizePath(sub("--file=", "", args[grep("--file=", args)])))
ROOT <- normalizePath(file.path(here, "../../.."))
DATA <- file.path(ROOT, "data/processed/pitch_charts")
OUT  <- file.path(ROOT, "deck/figures/pitch_charts")
F <- file.path(here, "fonts")
register_font("Figtree", plain = file.path(F, "Figtree-Regular.ttf"), bold = file.path(F, "Figtree-Bold.ttf"))
register_font("Figtree SemiBold", plain = file.path(F, "Figtree-SemiBold.ttf"), bold = file.path(F, "Figtree-ExtraBold.ttf"))
rd <- function(f) suppressMessages(read_csv(file.path(DATA, f), show_col_types = FALSE))
ONLY <- Sys.getenv("CHARTS_ONLY", "")   # e.g. CHARTS_ONLY=s to draw one topic
meta <- rd("r00_meta.csv")   # which ADR line the revenue and guide charts use

RAUSCH <- "#FF5A5F"; BABU <- "#00A699"; ARCHES <- "#FC642D"; HOF <- "#484848"; FOGGY <- "#767676"
LIGHT <- "#D8D8D8"; GRID <- "#EDEDED"; INK_SOFT <- "#9A9A9A"; MID <- "#BDBDBD"; PALE <- "#F7F7F7"
sw  <- function(col, glyph = "&#9632;") sprintf("<span style='color:%s'>%s</span>", col, glyph)
pct1 <- function(x) sprintf("%.1f%%", x)
spct0 <- function(x) ifelse(round(x) > 0, paste0("+", round(x)), ifelse(round(x) < 0, paste0("−", abs(round(x))), "0"))
spct1 <- function(x) ifelse(x > 0.049, sprintf("+%.1f%%", x), ifelse(x < -0.049, sprintf("−%.1f%%", abs(x)), "0.0%"))
axpct <- function(x) ifelse(x > 0, paste0("+", x, "%"), ifelse(x < 0, paste0("−", abs(x), "%"), "0%"))
qlab <- function(q) q

theme_abnb <- function(base = 9.5, grid = "y") {
  t <- theme_minimal(base_family = "Figtree", base_size = base) +
    theme(
      plot.title = element_text(family = "Figtree", face = "bold", size = base * 1.38, colour = HOF, margin = margin(b = 3)),
      plot.subtitle = element_markdown(family = "Figtree", size = base * 0.98, colour = FOGGY, lineheight = 1.25, margin = margin(b = 12)),
      plot.caption = element_textbox_simple(family = "Figtree", size = base * 0.72, colour = INK_SOFT, lineheight = 1.2, margin = margin(t = 10)),
      plot.title.position = "plot", plot.caption.position = "plot",
      axis.text = element_text(colour = FOGGY, size = base * 0.86),
      axis.title = element_blank(), axis.ticks = element_blank(),
      panel.grid.minor = element_blank(), panel.grid.major = element_blank(),
      plot.background = element_rect(fill = "white", colour = NA), panel.background = element_rect(fill = "white", colour = NA),
      legend.position = "none", strip.text = element_text(family = "Figtree SemiBold", colour = HOF, size = base, hjust = 0),
      plot.margin = margin(16, 20, 12, 16)
    )
  if (grid == "y") t <- t + theme(panel.grid.major.y = element_line(colour = GRID, linewidth = 0.35))
  if (grid == "x") t <- t + theme(panel.grid.major.x = element_line(colour = GRID, linewidth = 0.35))
  if (grid == "xy") t <- t + theme(panel.grid.major = element_line(colour = GRID, linewidth = 0.35))
  t
}
# Subtitles are markdown with explicit line breaks: ggtext's auto-wrapping textbox mis-measured some lines and
# overlapped the title. wrap_md breaks on the visible text (tags stripped, entities counted as one character).
wrap_md <- function(s, width) {
  # "@@" glues a swatch to its label and keeps the span tag in one token; restored after wrapping
  s <- gsub("<span style", "<span@@style", s, fixed = TRUE)
  s <- gsub("</span> ", "</span>@@", s, fixed = TRUE)
  vis <- function(t) nchar(gsub("@@", " ", gsub("&#[0-9]+;", "X", gsub("<[^>]+>", "", t)), fixed = TRUE))
  lines <- character(0); cur <- character(0); len <- 0
  for (t in strsplit(s, " ", fixed = TRUE)[[1]]) {
    l <- vis(t)
    if (len > 0 && len + 1 + l > width) { lines <- c(lines, paste(cur, collapse = " ")); cur <- t; len <- l }
    else { cur <- c(cur, t); len <- len + l + (len > 0) }
  }
  gsub("@@", " ", paste(c(lines, paste(cur, collapse = " ")), collapse = "<br>"), fixed = TRUE)
}
save_chart <- function(p, topic, name, w = 6.5, h = 3.6) {
  if (!is.null(p$labels$subtitle)) p <- p + labs(subtitle = wrap_md(p$labels$subtitle, floor((w - 0.55) * 15.8)))
  if (!is.null(p$labels$title) && nchar(p$labels$title) > floor(w * 10)) message("  TITLE LONG (", nchar(p$labels$title), "): ", name)
  d <- file.path(OUT, topic); dir.create(d, recursive = TRUE, showWarnings = FALSE)
  ggsave(file.path(d, paste0(name, ".png")), p, device = agg_png, width = w, height = h, units = "in", dpi = 300, bg = "white")
  message("saved ", topic, "/", name)
}

# ======================================================================================================================
# s: the stock trades on the guide
# ======================================================================================================================
if (ONLY %in% c("", "s")) {
SRC_S <- "Source: Airbnb shareholder letters; consensus reconstructed at each print (LSEG/Refinitiv, StreetAccount, FactSet); prices close to close (model/ABNB_historicals.xlsx, Earnings; data/processed/abnb_guidance_reaction_panel.csv)."
pr <- rd("s01_prints.csv") |> arrange(order)
hz <- rd("s02_group_horizons.csv"); fits <- rd("s03_fits.csv"); gates <- rd("s04_two_gates.csv"); call <- rd("s05_guide_call.csv")
GCOL <- c(above = BABU, below = RAUSCH, none = MID)
CALL_NOTE <- sprintf("Our 4Q26 guide call is pitch-forecasts C01 (audited: median $%sM, P(below) %.2f, set on bridge-v3 bookings), re-marked for the ADR line of 23 Sep with the team's C1 guide model, which scales the guide with bookings (×%.3f): median $%sM, 90%% band $%s–%sM, P(below the Street's $%sM) ≈%.2f on a normal fitted to C01's band.",
                     comma(call$c01_p50), call$c01_p_below, call$c1_ratio, comma(round(call$p50)), comma(round(call$p5)), comma(round(call$p95)), comma(call$street), call$p_below)
m1 <- hz |> filter(horizon == "exc_1d")
ma <- m1 |> filter(group == "above"); mb <- m1 |> filter(group == "below")

# s01 — the house version of deck/Graphs/image.png
d <- pr |> mutate(x = order, vj = ifelse(exc_1d >= 0, -0.45, 1.35))
p <- ggplot(d, aes(x = x, y = exc_1d)) +
  geom_hline(yintercept = 0, colour = FOGGY, linewidth = 0.35) +
  geom_col(aes(fill = guide_group), width = 0.7) +
  geom_text(aes(label = spct0(exc_1d), vjust = vj), family = "Figtree", size = 2.5, colour = HOF) +
  scale_fill_manual(values = GCOL) +
  scale_x_continuous(breaks = d$x, labels = d$quarter, expand = expansion(add = 0.6)) +
  scale_y_continuous(labels = axpct, breaks = seq(-15, 15, 5), limits = c(-15.5, 19)) +
  labs(title = "The print trades on the guide: below-Street guides fell 7 times in 8",
       subtitle = paste0("Day-1 return against the Nasdaq-100 (QQQ) at each print. ", sw(BABU), " next-quarter revenue guide above the Street  ",
                         sw(RAUSCH), " below  ", sw(MID), " no guide vs Street on record"),
       caption = paste0(sprintf("Mean day-1 move %s when the guide was above the Street (n %d), %s when below (n %d); rank-sum p %.2f. Guide = next-quarter revenue guide midpoint against consensus at the print. ",
                               spct1(ma$mean), ma$n, spct1(mb$mean), mb$n, ma$rank_sum_p), SRC_S)) +
  theme_abnb() + theme(axis.text.x = element_text(size = 6.8, angle = 45, hjust = 1, vjust = 1))
save_chart(p, "stock", "s01_day1_by_guide_bars", h = 3.7)

# s02 — scatter: guide vs Street against the day-1 move, with our 4Q26 call
f <- fits |> filter(sample == "ex_4Q21", x == "guide_vs_street_pct")
g <- pr |> filter(guide_group != "none")
gin <- g |> filter(quarter != "4Q21"); gout <- g |> filter(quarter == "4Q21")
XL <- c(-7.5, 7.2)
show <- c("4Q24", "2Q26", "2Q24", "1Q23", "3Q22", "4Q22", "2Q25", "1Q26", "3Q24")
p <- ggplot(gin, aes(x = guide_vs_street_pct, y = exc_1d)) +
  geom_hline(yintercept = 0, colour = LIGHT, linewidth = 0.35) + geom_vline(xintercept = 0, colour = LIGHT, linewidth = 0.35) +
  annotate("segment", x = call$p50_pct, xend = call$p50_pct, y = -17.2, yend = 17.5, colour = MID, linewidth = 0.45, linetype = "22") +
  annotate("segment", x = call$p5_pct, xend = call$p95_pct, y = -17.2, yend = -17.2, colour = HOF, linewidth = 1.6, lineend = "round") +
  annotate("point", x = call$p50_pct, y = -17.2, colour = RAUSCH, size = 3) +
  annotate("text", x = call$p95_pct + 0.3, y = -18, hjust = 0, vjust = 0, family = "Figtree", size = 2.5, colour = HOF, lineheight = 0.95,
           label = sprintf("Our 4Q26 guide call:\nmedian %s, 90%% band\nP(below Street) ≈%.2f", spct1(call$p50_pct), call$p_below)) +
  geom_abline(intercept = f$intercept, slope = f$slope, colour = RAUSCH, linewidth = 0.9) +
  geom_point(aes(colour = guide_group), size = 2.5) +
  geom_text_repel(data = gin |> filter(quarter %in% show), aes(label = quarter), family = "Figtree", size = 2.5, colour = FOGGY,
                  min.segment.length = 0.3, segment.colour = LIGHT, box.padding = 0.3, seed = 3) +
  annotate("text", x = XL[2], y = -9.5, hjust = 1, family = "Figtree", size = 2.5, colour = FOGGY,
           label = sprintf("4Q21 (guide +%.1f%%, day %s) off scale →", gout$guide_vs_street_pct, spct1(gout$exc_1d))) +
  scale_colour_manual(values = GCOL) +
  scale_x_continuous(labels = axpct, breaks = seq(-6, 6, 2)) + scale_y_continuous(labels = axpct, breaks = seq(-15, 15, 5)) +
  coord_cartesian(xlim = XL, ylim = c(-18, 18)) +
  labs(title = "The further the guide lands below the Street, the bigger the fall",
       subtitle = sprintf("Next-quarter revenue guide midpoint vs consensus (x) against the day-1 return vs QQQ (y), every print with a guide since 4Q21: about %.1f%% on the day per point", f$slope),
       caption = paste0(sprintf("Line: OLS on %d prints excluding 4Q21, slope %.2f, R² %.2f, p %.2f (with 4Q21: slope %.2f, R² %.2f). An association, not a price model. ",
                               f$n, f$slope, f$r2, f$p, fits$slope[fits$sample == "all" & fits$x == "guide_vs_street_pct"], fits$r2[fits$sample == "all" & fits$x == "guide_vs_street_pct"]),
                       CALL_NOTE, " ", SRC_S)) +
  theme_abnb(grid = "xy")
save_chart(p, "stock", "s02_guide_gap_scatter", h = 3.9)

# s03 — the beat doesn't move it, the guide does (same 18 prints in both panels)
f22 <- fits |> filter(sample == "1Q22_on")
d22 <- pr |> filter(order >= pr$order[pr$quarter == "1Q22"]) |>
  select(quarter, exc_1d, guide_group, rev_surprise, guide_vs_street_pct) |>
  pivot_longer(c(rev_surprise, guide_vs_street_pct), names_to = "x", values_to = "val") |>
  left_join(f22 |> select(x, slope, intercept, r2, p), by = "x") |>
  mutate(panel = factor(ifelse(x == "rev_surprise", "Reported revenue vs consensus", "Next-quarter guide vs consensus"),
                        levels = c("Reported revenue vs consensus", "Next-quarter guide vs consensus")))
lines <- d22 |> group_by(panel, x) |> summarise(lo = min(val), hi = max(val), slope = first(slope), intercept = first(intercept), r2 = first(r2), p = first(p), .groups = "drop") |>
  mutate(lab = sprintf("R² %.2f, p %.2f", r2, p))
p <- ggplot(d22, aes(x = val, y = exc_1d)) +
  geom_hline(yintercept = 0, colour = LIGHT, linewidth = 0.35) +
  geom_segment(data = lines, aes(x = lo, xend = hi, y = intercept + slope * lo, yend = intercept + slope * hi),
               colour = ifelse(lines$x == "rev_surprise", MID, RAUSCH), linewidth = 0.9) +
  geom_point(colour = HOF, size = 2.1) +
  geom_text(data = lines, aes(x = hi, y = 17, label = lab), hjust = 1, family = "Figtree", size = 2.8, colour = HOF) +
  facet_wrap(~panel, scales = "free_x") +
  scale_x_continuous(labels = axpct, breaks = scales::breaks_pretty(n = 5)) + scale_y_continuous(labels = axpct, breaks = seq(-15, 15, 5)) +
  labs(title = "The beat doesn't move the stock. The guide does",
       subtitle = "Day-1 return vs QQQ (y) against the size of the beat (left) and the guide gap (right), the same 18 prints, 1Q22 to 2Q26",
       caption = paste0("Revenue was at or above consensus at 17 of the 18 prints (within ±0.5% at four). Lines: OLS. ", SRC_S)) +
  theme_abnb(grid = "xy") + theme(panel.spacing = unit(1.8, "lines"))
save_chart(p, "stock", "s03_beat_vs_guide_panels", h = 3.8)

# s04 — dot strip: every print, by guide group, mean marked
d <- pr |> filter(guide_group != "none") |>
  mutate(y = ifelse(guide_group == "above", 2, 1), lab = ifelse(quarter %in% c("2Q26", "4Q24", "4Q22", "2Q24", "1Q23", "2Q25", "3Q22"), quarter, NA))
set.seed(4); d$yj <- d$y + runif(nrow(d), -0.13, 0.13)
mm <- m1 |> mutate(y = ifelse(group == "above", 2, 1))
p <- ggplot(d, aes(x = exc_1d, y = yj)) +
  geom_vline(xintercept = 0, colour = LIGHT, linewidth = 0.4) +
  geom_segment(data = mm, aes(x = mean, xend = mean, y = y - 0.3, yend = y + 0.3), colour = HOF, linewidth = 1.1, inherit.aes = FALSE) +
  geom_text(data = mm, aes(x = mean, y = y + 0.42, label = paste0("mean ", spct1(mean))), family = "Figtree SemiBold", size = 2.9, colour = HOF, inherit.aes = FALSE) +
  geom_point(aes(colour = guide_group), size = 3, alpha = 0.9) +
  geom_text(aes(label = lab), nudge_y = -0.22, family = "Figtree", size = 2.4, colour = FOGGY, na.rm = TRUE) +
  scale_colour_manual(values = GCOL) +
  scale_y_continuous(breaks = c(1, 2), labels = c(sprintf("Guide below the Street\n(n %d, %d fell)", mb$n, mb$n_neg), sprintf("Guide above the Street\n(n %d, %d fell)", ma$n, ma$n_neg)),
                     limits = c(0.55, 2.6)) +
  scale_x_continuous(labels = axpct, breaks = seq(-15, 15, 5)) +
  labs(title = "Below-Street guides averaged −5% on the day, above-Street +2%",
       subtitle = "Day-1 return vs QQQ at every print with a guide against consensus, 4Q21 to 2Q26",
       caption = paste0(sprintf("Rank-sum p %.2f (n %d vs %d). ", ma$rank_sum_p, ma$n, mb$n), SRC_S)) +
  theme_abnb(grid = "x") + theme(axis.text.y = element_text(colour = HOF, size = 8.6, hjust = 0, lineheight = 1.1))
save_chart(p, "stock", "s04_dot_strip_groups", h = 3.3)

# s05 — the move doesn't reverse: 1, 5, 20 trading days
hh <- hz |> mutate(hl = factor(recode(horizon, exc_1d = "Day 1", exc_5d = "5 days", exc_20d = "20 days"), levels = c("Day 1", "5 days", "20 days")),
                   x = as.numeric(hl) + ifelse(group == "above", -0.17, 0.17),
                   lab = paste0(spct1(mean), "\n", n_neg, " of ", n, " down"))
p <- ggplot(hh, aes(x = x, y = mean, fill = group)) +
  geom_hline(yintercept = 0, colour = FOGGY, linewidth = 0.35) +
  geom_col(width = 0.32) +
  geom_errorbar(aes(ymin = mean - se, ymax = mean + se), width = 0, colour = MID, linewidth = 0.5) +
  geom_text(aes(y = ifelse(mean >= 0, mean + se + 0.6, mean - se - 0.6), vjust = ifelse(mean >= 0, 0, 1), label = lab),
            family = "Figtree", size = 2.5, colour = HOF, lineheight = 0.95) +
  scale_fill_manual(values = GCOL) +
  scale_x_continuous(breaks = 1:3, labels = levels(hh$hl)) +
  scale_y_continuous(labels = axpct, breaks = seq(-15, 5, 5), limits = c(-16, 6.5)) +
  labs(title = "It doesn't bounce back: 8 of 8 still down 20 days later",
       subtitle = paste0("Mean return vs QQQ after the print. ", sw(BABU), " guide above the Street (n 11)  ", sw(RAUSCH), " guide below (n 8). Whiskers: ±1 standard error"),
       caption = paste0(sprintf("Rank-sum p: day 1 %.2f, 5 days %.2f, 20 days %.2f. Trading days, close to close from the pre-print close. ",
                               hz$rank_sum_p[hz$horizon == "exc_1d"][1], hz$rank_sum_p[hz$horizon == "exc_5d"][1], hz$rank_sum_p[hz$horizon == "exc_20d"][1]), SRC_S)) +
  theme_abnb()
save_chart(p, "stock", "s05_horizons_1_5_20", h = 3.6)

# s06 — two gates: guide below Street and nights guided down
gg <- gates |> filter(guide != "uncoded") |>
  mutate(key = paste(guide, nights_down),
         lab = c("below 1" = "Guide below Street,\nnights guided down", "below 0" = "Guide below Street,\nnights not guided down",
                 "above 1" = "Guide above Street,\nnights guided down", "above 0" = "Guide above Street,\nnights not guided down")[key],
         y = c("below 1" = 4, "below 0" = 3, "above 1" = 2, "above 0" = 1)[key])
pts <- gg |> select(key, y, prints) |> mutate(prints = str_split(prints, " (?=\\dQ)")) |> unnest(prints) |>
  mutate(q = word(prints, 1), v = as.numeric(sub("−", "-", word(prints, 2))))
p <- ggplot() +
  annotate("rect", xmin = -Inf, xmax = Inf, ymin = 3.5, ymax = 4.5, fill = "#FFF4F4") +
  geom_vline(xintercept = 0, colour = LIGHT, linewidth = 0.4) +
  geom_segment(data = gg, aes(x = mean, xend = mean, y = y - 0.3, yend = y + 0.3), colour = HOF, linewidth = 1.1) +
  geom_point(data = pts, aes(x = v, y = y, colour = key == "below 1"), size = 2.8, alpha = 0.9) +
  geom_text_repel(data = pts, aes(x = v, y = y, label = q), family = "Figtree", size = 2.3, colour = FOGGY, direction = "x",
                  nudge_y = -0.3, segment.colour = NA, seed = 1, box.padding = 0.1) +
  geom_text(data = gg, aes(x = 26, y = y, label = sprintf("%s mean\n%d of %d fell", spct1(mean), n_neg, n)), hjust = 1,
            family = "Figtree", size = 2.6, colour = HOF, lineheight = 0.95) +
  scale_colour_manual(values = c(`TRUE` = RAUSCH, `FALSE` = MID)) +
  scale_y_continuous(breaks = gg$y, labels = gg$lab, expand = expansion(add = 0.1)) +
  scale_x_continuous(labels = axpct, breaks = seq(-15, 15, 5), limits = c(-14, 26)) +
  labs(title = "When both gates close, the stock has fallen every time",
       subtitle = "Day-1 return vs QQQ by what the print guided: next-quarter revenue against the Street, and next-quarter nights growth against the reported quarter",
       caption = paste0("n 5, 3, 4 and 6; 1Q22 has no codable nights direction. Nights direction: management's next-quarter nights language coded up / stable / down, or the sign of the numeric guide where one was given (3Q25, 4Q25, 2Q26). Small cells: a base rate, not a model. ", SRC_S)) +
  theme_abnb(grid = "x") + theme(axis.text.y = element_text(colour = HOF, size = 8.2, hjust = 0, lineheight = 1.05))
save_chart(p, "stock", "s06_two_gates", h = 3.9)

# s07 — the 5 Nov setup: guide vs Street at each print, then our 4Q26 call
d <- pr |> filter(order >= pr$order[pr$quarter == "1Q22"]) |> mutate(x = row_number())
xc <- max(d$x) + 1.4
p <- ggplot(d, aes(x = x, y = guide_vs_street_pct)) +
  annotate("rect", xmin = xc - 0.7, xmax = xc + 0.7, ymin = -Inf, ymax = Inf, fill = PALE) +
  geom_hline(yintercept = 0, colour = FOGGY, linewidth = 0.35) +
  geom_col(aes(fill = guide_group), width = 0.66) +
  annotate("segment", x = xc, xend = xc, y = call$p5_pct, yend = call$p95_pct, colour = HOF, linewidth = 0.7) +
  annotate("point", x = xc, y = call$p50_pct, colour = RAUSCH, size = 3.2) +
  annotate("text", x = xc + 0.28, y = call$p50_pct, hjust = 0, family = "Figtree SemiBold", size = 2.7, colour = HOF, label = spct1(call$p50_pct)) +
  annotate("text", x = xc, y = 6.6, family = "Figtree", size = 2.6, colour = HOF, lineheight = 0.95,
           label = sprintf("Our call, 5 Nov\nP(below) ≈%.2f", call$p_below)) +
  geom_text(aes(label = spct1(guide_vs_street_pct), vjust = ifelse(guide_vs_street_pct >= 0, -0.5, 1.4)), family = "Figtree", size = 2.2, colour = FOGGY) +
  annotate("text", x = 16, y = 5.0, family = "Figtree", size = 2.6, colour = FOGGY, label = "Five straight guides above the Street") +
  scale_fill_manual(values = GCOL) +
  scale_x_continuous(breaks = c(d$x, xc), labels = c(d$quarter, "3Q26\nprint"), expand = expansion(add = c(0.6, 0.9))) +
  scale_y_continuous(labels = axpct, breaks = seq(-8, 6, 2), limits = c(min(-7.2, call$p5_pct - 0.4), 7.2)) +
  labs(title = "After five guides above the Street, we expect Q4's to land below",
       subtitle = paste0("Next-quarter revenue guide midpoint vs consensus at each print. ", sw(BABU), " above  ", sw(RAUSCH), " below. Our 4Q26 call: median and 90% interval"),
       caption = paste0(CALL_NOTE, " 4Q21 (+16.5%) omitted for scale. ", SRC_S)) +
  theme_abnb() + theme(axis.text.x = element_text(size = 6.8))
save_chart(p, "stock", "s07_guide_gap_history_and_call", h = 3.7)

# s08 — beat every time, move is a coin flip (two stacked rows)
d <- pr |> filter(order >= pr$order[pr$quarter == "1Q22"]) |> mutate(x = row_number())
dl <- bind_rows(d |> transmute(x, quarter, v = rev_surprise, row = "Reported revenue vs consensus", col = "rev"),
                d |> transmute(x, quarter, v = exc_1d, row = "Day-1 return vs QQQ", col = ifelse(exc_1d >= 0, "up", "down"))) |>
  mutate(row = factor(row, levels = c("Reported revenue vs consensus", "Day-1 return vs QQQ")))
p <- ggplot(dl, aes(x = x, y = v, fill = col)) +
  geom_hline(yintercept = 0, colour = FOGGY, linewidth = 0.35) +
  geom_col(width = 0.66) +
  geom_text(aes(label = ifelse(row == "Day-1 return vs QQQ", spct0(v), sprintf("%.1f", v)), vjust = ifelse(v >= 0, -0.45, 1.35)),
            family = "Figtree", size = 2.2, colour = FOGGY) +
  facet_wrap(~row, ncol = 1, scales = "free_y") +
  scale_fill_manual(values = c(rev = MID, up = BABU, down = RAUSCH)) +
  scale_x_continuous(breaks = d$x, labels = d$quarter, expand = expansion(add = 0.6)) +
  scale_y_continuous(labels = axpct, expand = expansion(mult = 0.22)) +
  labs(title = "Airbnb beats almost every quarter. The stock still fell after 11 of 18",
       subtitle = "Each print since 1Q22: the revenue surprise (top) and the day-1 move (bottom), in %",
       caption = paste0("Revenue at or above consensus at 17 of 18 prints; the 2Q22 miss was 0.3%. ", SRC_S)) +
  theme_abnb() + theme(axis.text.x = element_text(size = 6.8), panel.spacing = unit(0.9, "lines"))
save_chart(p, "stock", "s08_beat_vs_move_timeline", h = 3.9)
}

# ----------------------------------------------------------------------------------------------------------------------
# shared: vertical waterfall (start total, steps, end total)
# ----------------------------------------------------------------------------------------------------------------------
waterfall <- function(start_lab, start_val, steps, end_lab, end_val, digits = 1, base = 9.5) {
  n <- nrow(steps)
  cum <- start_val + cumsum(steps$val)
  d <- bind_rows(
    tibble(x = 1, lab = start_lab, ymin = 0, ymax = start_val, kind = "total", val = start_val),
    tibble(x = 2:(n + 1), lab = steps$lab, ymin = pmin(c(start_val, head(cum, -1)), cum), ymax = pmax(c(start_val, head(cum, -1)), cum),
           kind = ifelse(steps$val >= 0, "up", "down"), val = steps$val),
    tibble(x = n + 2, lab = end_lab, ymin = 0, ymax = end_val, kind = "total", val = end_val)) |>
    mutate(lab = factor(lab, levels = lab))
  conn <- tibble(x = 1:(n + 1) + 0.32, xend = 2:(n + 2) - 0.32, y = c(start_val, cum))
  fmt <- function(v, k) ifelse(k == "total", sprintf(paste0("%.", digits, "f%%"), v),
                               ifelse(v >= 0, sprintf(paste0("+%.", digits, "f"), v), sprintf(paste0("−%.", digits, "f"), abs(v))))
  ggplot(d) +
    geom_hline(yintercept = 0, colour = FOGGY, linewidth = 0.35) +
    geom_segment(data = conn, aes(x = x, xend = xend, y = y, yend = y), colour = LIGHT, linewidth = 0.4) +
    geom_rect(aes(xmin = x - 0.32, xmax = x + 0.32, ymin = ymin, ymax = ymax, fill = kind)) +
    geom_text(aes(x = x, y = ymax, label = fmt(val, kind)), vjust = -0.5, family = "Figtree", fontface = ifelse(d$kind == "total", "bold", "plain"),
              size = base * 0.31, colour = HOF) +
    scale_fill_manual(values = c(total = HOF, up = BABU, down = RAUSCH)) +
    scale_x_continuous(breaks = d$x, labels = d$lab, expand = expansion(add = 0.5)) +
    scale_y_continuous(labels = function(x) paste0(x, "%"), expand = expansion(mult = c(0, 0.12))) +
    theme_abnb(base) + theme(axis.text.x = element_text(colour = HOF, size = base * 0.8, lineheight = 1.05))
}
BEACH <- "#FFB400"
PANEL_SHADE <- function(xmin, xmax, label = "Our model", y = Inf) list(
  annotate("rect", xmin = xmin, xmax = xmax, ymin = -Inf, ymax = Inf, fill = PALE),
  annotate("text", x = (xmin + xmax) / 2, y = y, vjust = 1.3, label = label, family = "Figtree", size = 2.7, colour = FOGGY))

# ======================================================================================================================
# r: what drives revenue growth
# ======================================================================================================================
if (ONLY %in% c("", "r")) {
SRC_R <- paste0("Source: Airbnb shareholder letters (nights, ADR and ex-FX ADR growth), 10-Qs. Forecast: the official model on main (nights, take rate, costs; DEC-0042) with ",
                meta$adr_label, "; revenue = nights × ADR × take rate.")
rv <- rd("r01_revenue_decomposition.csv")
sv <- rd("r02_ours_vs_street.csv")
COMP <- c(c_nights = "Nights", c_adr_exfx = "ADR ex-FX", c_fx = "FX", c_take_rate = "Take rate")
CCOL <- c("Nights" = RAUSCH, "ADR ex-FX" = BABU, "FX" = BEACH, "Take rate" = MID)
leg_r <- paste0(sw(RAUSCH), " nights  ", sw(BABU), " ADR ex-FX  ", sw(BEACH), " FX  ", sw(MID), " take rate")
long_r <- function(d) d |> select(quarter, kind, revenue_yoy, all_of(names(COMP))) |>
  pivot_longer(all_of(names(COMP)), names_to = "comp", values_to = "v") |>
  mutate(comp = factor(COMP[comp], levels = rev(COMP)))
ptop <- function(d) with(d, pmax(c_nights, 0) + pmax(c_adr_exfx, 0) + pmax(c_fx, 0) + pmax(c_take_rate, 0))
NOTE_R <- "Contributions are log shares of each factor, scaled to sum to reported revenue growth. FX = reported minus ex-FX ADR growth (the letters' definition). Take rate = revenue ÷ same-quarter GBV; it moves with booking timing because revenue is recognised at check-in."

# r01 — stacked contributions, 1Q24 to 4Q27
d <- rv |> filter(!quarter %in% c("1Q23", "2Q23", "3Q23", "4Q23")) |> mutate(x = row_number())
dl <- long_r(d) |> left_join(d |> select(quarter, x), by = "quarter")
xf <- min(d$x[d$kind == "forecast"])
p <- ggplot(dl, aes(x = x, y = v)) +
  PANEL_SHADE(xf - 0.5, max(d$x) + 0.5, "Our model", 21) +
  geom_hline(yintercept = 0, colour = FOGGY, linewidth = 0.35) +
  geom_col(aes(fill = comp), width = 0.68) +
  geom_point(data = d, aes(x = x, y = revenue_yoy), colour = HOF, size = 1.9) +
  geom_text(data = d, aes(x = x, y = ptop(d) + 1.2, label = sprintf("%.0f%%", revenue_yoy)), family = "Figtree SemiBold", size = 2.6, colour = HOF) +
  scale_fill_manual(values = CCOL) +
  scale_x_continuous(breaks = d$x, labels = d$quarter, expand = expansion(add = 0.5)) +
  scale_y_continuous(labels = function(x) paste0(x, "%"), breaks = seq(-5, 20, 5), limits = c(-6, 21.5)) +
  labs(title = "2026's revenue growth leaned on price and currency, and both fade",
       subtitle = paste0("Contribution to revenue growth, percentage points. ", leg_r, ". ", sw(HOF, "&#9679;"), " revenue growth"),
       caption = paste(NOTE_R, SRC_R)) +
  theme_abnb() + theme(axis.text.x = element_text(size = 6.8))
save_chart(p, "revenue", "r01_drivers_stacked_1Q24_4Q27", h = 3.8)

# r02 — compact: the last six quarters and the two we trade
d <- rv |> filter(quarter %in% c("1Q25", "2Q25", "3Q25", "4Q25", "1Q26", "2Q26", "3Q26", "4Q26")) |> mutate(x = row_number())
dl <- long_r(d) |> left_join(d |> select(quarter, x), by = "quarter") |>
  mutate(show = abs(v) >= 1.2, lab = sprintf("%.1f", v), tc = ifelse(comp %in% c("Nights"), "white", HOF))
p <- ggplot(dl, aes(x = x, y = v)) +
  PANEL_SHADE(6.5, 8.5, "Our model", 21) +
  geom_hline(yintercept = 0, colour = FOGGY, linewidth = 0.35) +
  geom_col(aes(fill = comp), width = 0.7) +
  geom_text(data = dl |> filter(show), aes(label = lab, group = comp, colour = I(tc)), position = position_stack(vjust = 0.5), family = "Figtree", size = 2.4) +
  geom_text(data = d, aes(x = x, y = ptop(d) + 1.1, label = sprintf("%.1f%%", revenue_yoy)), family = "Figtree SemiBold", size = 2.8, colour = HOF) +
  scale_fill_manual(values = CCOL) +
  scale_x_continuous(breaks = d$x, labels = paste0(d$quarter, ifelse(d$kind == "forecast", "E", "")), expand = expansion(add = 0.5)) +
  scale_y_continuous(labels = function(x) paste0(x, "%"), breaks = seq(-5, 20, 5), limits = c(-5, 21.5)) +
  labs(title = "Price and FX drove the 2026 acceleration, and both fade",
       subtitle = paste0("Contribution to revenue growth, percentage points. ", leg_r),
       caption = paste(NOTE_R, SRC_R)) +
  theme_abnb()
save_chart(p, "revenue", "r02_drivers_stacked_compact", h = 3.7)

# r03 — small multiples: each driver's y/y, history and forecast, Street where it exists
d <- rv |> filter(!quarter %in% c("1Q23", "2Q23", "3Q23", "4Q23")) |> mutate(x = row_number())
dm <- d |> transmute(quarter, x, kind, `Nights` = nights_yoy, `ADR ex-FX` = adr_exfx_yoy, `FX on ADR (pp)` = adr_fx_pp, `Take rate` = take_rate_yoy) |>
  pivot_longer(-c(quarter, x, kind), names_to = "m", values_to = "v") |> mutate(m = factor(m, levels = c("Nights", "ADR ex-FX", "FX on ADR (pp)", "Take rate")))
sp <- sv |> filter(source == "Street") |> left_join(d |> select(quarter, x), by = "quarter") |>
  transmute(x, `Nights` = nights_yoy, `Take rate` = take_rate_yoy) |> pivot_longer(-x, names_to = "m", values_to = "v") |>
  mutate(m = factor(m, levels = levels(dm$m)))
xf <- min(d$x[d$kind == "forecast"])
brk <- d |> filter(quarter %in% c("1Q24", "1Q25", "1Q26", "1Q27"))
p <- ggplot(dm, aes(x = x, y = v)) +
  annotate("rect", xmin = xf - 0.5, xmax = max(d$x) + 0.5, ymin = -Inf, ymax = Inf, fill = PALE) +
  geom_hline(yintercept = 0, colour = LIGHT, linewidth = 0.35) +
  geom_line(data = dm |> filter(x <= xf), colour = HOF, linewidth = 0.8) +
  geom_line(data = dm |> filter(x >= xf - 1), colour = RAUSCH, linewidth = 0.8, linetype = "22") +
  geom_point(data = dm |> filter(kind == "forecast"), colour = RAUSCH, size = 1.4) +
  geom_point(data = sp, shape = 23, fill = "white", colour = HOF, size = 1.9, stroke = 0.7) +
  facet_wrap(~m, nrow = 1, scales = "free_y") +
  scale_x_continuous(breaks = brk$x, labels = brk$quarter) +
  scale_y_continuous(labels = function(x) paste0(x, "%")) +
  labs(title = "Nights, price and FX all slow from here",
       subtitle = paste0("Year-over-year growth. ", sw(HOF, "&#9644;"), " reported  ", sw(RAUSCH, "&#9644;"), " our model  ",
                         sw(HOF, "&#9671;"), " Street (3Q26 and 4Q26; the Street's ADR is not split by FX)"),
       caption = paste("FX on ADR in percentage points of ADR growth. Take rate = revenue ÷ same-quarter GBV; 3Q26-4Q26 take rate set to the Street's implied rate, then seasonal naive (DEC-0042).", SRC_R)) +
  theme_abnb(9, grid = "y") + theme(panel.spacing = unit(1.1, "lines"), axis.text.x = element_text(size = 6.6))
save_chart(p, "revenue", "r03_driver_small_multiples", w = 7.2, h = 3.4)

# r04 — ours vs Street on each driver, 3Q26 and 4Q26
sw4 <- sv |> pivot_longer(c(nights_yoy, adr_yoy, take_rate_yoy, revenue_yoy), names_to = "m", values_to = "v") |>
  mutate(m = factor(recode(m, nights_yoy = "Nights", adr_yoy = "ADR", take_rate_yoy = "Take rate", revenue_yoy = "Revenue"),
                    levels = rev(c("Nights", "ADR", "Take rate", "Revenue"))))
gap <- sw4 |> select(quarter, source, m, v) |> pivot_wider(names_from = source, values_from = v) |> mutate(d = Ours - Street, xl = pmax(Ours, Street) + 0.5)
p <- ggplot(sw4, aes(x = v, y = m)) +
  geom_segment(data = gap, aes(x = Street, xend = Ours, y = m, yend = m), colour = LIGHT, linewidth = 1.6) +
  geom_point(aes(colour = source), size = 3) +
  geom_text(data = gap, aes(x = xl, y = m, label = ifelse(abs(d) < 0.05, "same", sprintf("%+.1fpt", d))), hjust = 0, family = "Figtree",
            size = 2.7, colour = ifelse(abs(gap$d) < 0.05, FOGGY, ifelse(gap$d < 0, RAUSCH, BABU))) +
  facet_wrap(~quarter, nrow = 1) +
  scale_colour_manual(values = c(Ours = RAUSCH, Street = "#A9A9A9")) +
  scale_x_continuous(labels = function(x) paste0(x, "%"), limits = c(0, 18.5)) +
  labs(title = if (any(gap$d[gap$m == "ADR"] < -0.1)) "Nights is most of our gap to the Street, and ADR now adds to it" else "Against the Street, the revenue gap is all nights",
       subtitle = paste0("Year-over-year growth. ", sw(RAUSCH, "&#9679;"), " our model  ", sw("#A9A9A9", "&#9679;"), " Street"),
       caption = paste("Street: nights and ADR from Bloomberg MODL (12 Sep 2026, n 25-28), revenue LSEG (n 37); the Street's take rate is implied (revenue ÷ nights × ADR) and our model uses it by construction (DEC-0018).", SRC_R)) +
  theme_abnb(grid = "x") + theme(axis.text.y = element_text(colour = HOF), panel.spacing = unit(1.6, "lines"))
save_chart(p, "revenue", "r04_ours_vs_street_dumbbell", h = 3.2)

# r05, r06 — bridges from 2Q26 to the guided quarter and to the same quarter next year
bridge_r <- function(q0, q1) {
  a <- rv |> filter(quarter == q0); b <- rv |> filter(quarter == q1)
  tibble(lab = c("Nights", "ADR ex-FX", "FX", "Take rate"),
         val = c(b$c_nights - a$c_nights, b$c_adr_exfx - a$c_adr_exfx, b$c_fx - a$c_fx, b$c_take_rate - a$c_take_rate)) |>
    list(a = a, b = b)
}
br <- bridge_r("2Q26", "4Q26")
p <- waterfall("2Q26\nreported", br$a$revenue_yoy, br[[1]], "4Q26\nour model", br$b$revenue_yoy) +
  labs(title = sprintf("From %.1f%% to %.1f%%: nights and price both give back", br$a$revenue_yoy, br$b$revenue_yoy),
       subtitle = "Revenue growth, 2Q26 reported to our 4Q26 (the quarter management guides on 5 Nov): change in each driver's contribution, points",
       caption = paste(NOTE_R, SRC_R)) + theme(axis.text.x = element_text(size = 8))
save_chart(p, "revenue", "r05_bridge_2Q26_to_4Q26", h = 3.5)
br <- bridge_r("2Q26", "2Q27")
p <- waterfall("2Q26\nreported", br$a$revenue_yoy, br[[1]], "2Q27\nour model", br$b$revenue_yoy) +
  labs(title = sprintf("Revenue growth halves by 2Q27; nights are %.0f%% of the drop", 100 * br[[1]]$val[1] / sum(br[[1]]$val)),
       subtitle = sprintf("Revenue growth, 2Q26 reported (%.1f%%) to our 2Q27 (%.1f%%), same season a year on: change in each driver's contribution, points", br$a$revenue_yoy, br$b$revenue_yoy),
       caption = paste(NOTE_R, SRC_R)) + theme(axis.text.x = element_text(size = 8))
save_chart(p, "revenue", "r06_bridge_2Q26_to_2Q27", h = 3.5)

# r07 — FX on revenue as the letters state it, and the team's line forward
d <- rv |> filter(!quarter %in% c("1Q23", "2Q23", "3Q23", "4Q23")) |> mutate(x = row_number(), fxr = coalesce(fx_rev_letter, fx_rev_line),
                                                                               exfx = revenue_yoy - fxr)
xf <- min(d$x[d$kind == "forecast"])
p <- ggplot(d, aes(x = x)) +
  PANEL_SHADE(xf - 0.5, max(d$x) + 0.5, "Our model", 21.5) +
  geom_hline(yintercept = 0, colour = FOGGY, linewidth = 0.35) +
  geom_col(aes(y = fxr, fill = fxr >= 0), width = 0.62) +
  geom_line(aes(y = revenue_yoy), colour = HOF, linewidth = 0.9) +
  geom_line(aes(y = exfx), colour = HOF, linewidth = 0.7, linetype = "22") +
  geom_point(aes(y = revenue_yoy), colour = HOF, size = 1.6) +
  geom_text(aes(y = ifelse(fxr >= 0, fxr + 0.8, fxr - 0.8), label = ifelse(fxr == 0, "", ifelse(kind == "forecast", sprintf("%+.1f", fxr), sprintf("%+.0f", fxr)))), family = "Figtree", size = 2.4, colour = FOGGY) +
  annotate("text", x = 1.2, y = 19.5, hjust = 0, label = "Revenue growth", family = "Figtree", size = 2.7, colour = HOF) +
  annotate("text", x = 9.1, y = 12.2, hjust = 0.5, label = "ex-FX", family = "Figtree", size = 2.6, colour = HOF) +
  scale_fill_manual(values = c(`TRUE` = BEACH, `FALSE` = "#FFD980")) +
  scale_x_continuous(breaks = d$x, labels = d$quarter, expand = expansion(add = 0.5)) +
  scale_y_continuous(labels = function(x) paste0(x, "%"), breaks = seq(-5, 20, 5), limits = c(-4, 22)) +
  labs(title = "FX added 3–4 points to revenue growth in 1H26. By 4Q26 it is about one",
       subtitle = paste0(sw(BEACH), " FX effect on revenue growth, points, as each letter states it (whole points)  ", sw(HOF, "&#9644;"), " revenue growth  ",
                         sw(HOF, "- -"), " ex-FX"),
       caption = paste("Forecast FX: management's ~3 points for 3Q26; the team's revenue-FX line from 4Q26 (DEC-0010, spot held, +0.98; confidence set +0.3 to +2.2). Revenue FX differs from FX on ADR because revenue is recognised at check-in and is after hedges.", SRC_R)) +
  theme_abnb() + theme(axis.text.x = element_text(size = 6.8))
save_chart(p, "revenue", "r07_fx_on_revenue", h = 3.6)

# r08 — what the ADR line does to margin: gap to the Street, before and after
wm <- rd("r03_what_moved.csv")
mw <- wm |> select(period, source, margin) |> pivot_wider(names_from = source, values_from = margin) |>
  mutate(new = this_line - street, old = main_v2 - street, y = match(period, rev(c("3Q26", "4Q26", "FY26", "FY27"))),
         lab = sprintf("%.1f%% vs Street %.1f%%", this_line, street))
fy26 <- mw |> filter(period == "FY26")
p <- ggplot(mw, aes(y = y)) +
  geom_vline(xintercept = 0, colour = HOF, linewidth = 0.5) +
  annotate("text", x = 0.05, y = 4.62, hjust = 0, label = "Street", family = "Figtree", size = 2.7, colour = HOF) +
  geom_segment(aes(x = old, xend = new, yend = y), colour = LIGHT, linewidth = 1.4,
               arrow = arrow(length = unit(0.08, "in"), type = "closed"), arrow.fill = LIGHT) +
  geom_point(aes(x = old), shape = 21, fill = "white", colour = RAUSCH, size = 2.8, stroke = 0.9) +
  geom_point(aes(x = new), colour = RAUSCH, size = 3.1) +
  geom_text(aes(x = new, label = sprintf("%+.1fpt", new)), vjust = -1.1, family = "Figtree SemiBold", size = 2.6, colour = HOF) +
  geom_text(aes(x = 0.35, label = lab), hjust = 0, family = "Figtree", size = 2.6, colour = FOGGY) +
  scale_y_continuous(breaks = mw$y, labels = mw$period, expand = expansion(add = c(0.5, 0.75))) +
  scale_x_continuous(labels = function(x) paste0(x, "pt"), limits = c(min(mw$new) - 0.5, 2.9), breaks = seq(-4, 0, 1)) +
  labs(title = sprintf("The new ADR line takes FY26 margin to %.1f%%, under the 35.5%% floor", fy26$this_line),
       subtitle = paste0("Adjusted EBITDA margin against the Street, points. ", sw(RAUSCH, "&#9675;"), " before (ADR engine v2 on main)  ",
                         sw(RAUSCH, "&#9679;"), " after (the 23 Sep ADR line)"),
       caption = paste("Margin is an output: revenue = nights × ADR × take rate, with the official model's cash costs carried flat in dollars (DEC-0022). If costs flexed with revenue (the C4 question), the drop would be smaller. FY26 = 1H26 reported + our 2H26; management guided FY26 adjusted EBITDA margin of at least 35.5%. Street: LSEG quarterly means (13 Sep); FY27 36.45% implied (DEC-0013).", SRC_R)) +
  theme_abnb(grid = "x") + theme(axis.text.y = element_text(colour = HOF, size = 9))
save_chart(p, "revenue", "r08_margin_vs_street_before_after", h = 3.3)

# r09 — revenue against the Street, every forecast quarter
rq <- rd("r04_revenue_vs_street_quarterly.csv") |> mutate(x = match(quarter, unique(quarter)))
rn <- rq |> filter(source == "this_line"); ro <- rq |> filter(source == "main_v2")
p <- ggplot(rn, aes(x = x, y = vs_street_pct)) +
  geom_hline(yintercept = 0, colour = HOF, linewidth = 0.5) +
  geom_col(fill = RAUSCH, width = 0.58) +
  geom_point(data = ro, shape = 21, fill = "white", colour = HOF, size = 2.4, stroke = 0.8) +
  geom_text(aes(label = sprintf("%.1f%%", vs_street_pct)), vjust = 1.6, family = "Figtree SemiBold", size = 2.7, colour = HOF) +
  geom_text(aes(y = 0, label = sprintf("$%s", comma(round(revenue)))), vjust = -0.6, family = "Figtree", size = 2.4, colour = FOGGY) +
  scale_x_continuous(breaks = rn$x, labels = rn$quarter, expand = expansion(add = 0.5)) +
  scale_y_continuous(labels = function(x) paste0(x, "%"), limits = c(min(rn$vs_street_pct) - 0.9, 0.9)) +
  labs(title = sprintf("Our revenue is %.1f–%.1f%% under the Street in every quarter to 4Q27", -max(rn$vs_street_pct), -min(rn$vs_street_pct)),
       subtitle = paste0("Revenue against LSEG consensus (0% = the Street). ", sw(RAUSCH), " the 23 Sep ADR line (our revenue, $M, above the bar)  ",
                         sw(HOF, "&#9675;"), " before, on ADR engine v2"),
       caption = paste("Street: LSEG quarterly means, 13 Sep 2026 pull (n 36-37 for 2026, 19-21 for 2027). 3Q26-4Q26 take rate is the Street's own implied rate, so those gaps are nights and ADR only.", SRC_R)) +
  theme_abnb()
save_chart(p, "revenue", "r09_revenue_vs_street_quarterly", h = 3.4)
}

# ======================================================================================================================
# n: nights, the product bundle, the World Cup and RNPL cancellations
# ======================================================================================================================
if (ONLY %in% c("", "n")) {
SRC_N <- "Source: Airbnb letters and 10-Qs (printed nights); team nights line (docs/pitch-model-v2/lines/final_nights.md, nights_v2_design.md); RNPL cohort module (analysis/src/rnpl_short_audit)."
nd <- rd("n01_nights_decomposition.csv") |> mutate(x = row_number())
ct <- rd("n02_cancellation_tail.csv"); cr <- rd("n03_cancel_rate.csv"); uf <- rd("n04_unearned_fees_vs_gbv.csv"); wcr <- rd("n05_worldcup_reviews.csv")
xf <- min(nd$x[nd$kind == "forecast"])
NCOL <- c(Underlying = MID, Bundle = RAUSCH, `World Cup` = BEACH, `Middle East` = FOGGY)
leg_n <- paste0(sw(MID), " underlying  ", sw(RAUSCH), " product bundle (RNPL, fees, cancellation policy)  ", sw(BEACH), " World Cup  ", sw(FOGGY), " Middle East")
NOTE_BUNDLE <- "Bundle = the three features management sized at 'over 200 basis points' of nights growth in 4Q25 and 'approximately three points' in 1Q26 (calls), split by leg and region as in the nights line, each leg lapping on its launch anniversary. World Cup: +0.5pt in 2Q26 is our model's assumption (the size of its 2Q27 lap); management never sized it and host-market reviews point to ~0.1pt. Middle East: ~1pt headwind in 1Q26 (1Q26 letter), lapped in 1Q27."

# n01 — hero: nights growth decomposed, 1Q24 to 4Q27
dl <- nd |> transmute(x, quarter, Underlying = underlying, Bundle = bundle, `World Cup` = wc, `Middle East` = me) |>
  pivot_longer(-c(x, quarter), names_to = "comp", values_to = "v") |> mutate(comp = factor(comp, levels = rev(names(NCOL))))
st2 <- nd |> filter(!is.na(street))
p <- ggplot(dl, aes(x = x, y = v)) +
  PANEL_SHADE(xf - 0.5, max(nd$x) + 0.5, "Our model", 14.3) +
  geom_hline(yintercept = 0, colour = FOGGY, linewidth = 0.35) +
  geom_col(aes(fill = comp), width = 0.68) +
  geom_point(data = nd, aes(x = x, y = total), colour = HOF, size = 1.9) +
  geom_text(data = nd, aes(x = x, y = pmax(total, underlying + bundle + pmax(wc, 0)) + 0.75, label = sprintf("%.1f", total)), family = "Figtree SemiBold", size = 2.4, colour = HOF) +
  geom_point(data = st2, aes(x = x + 0.3, y = street), shape = 23, fill = "white", colour = HOF, size = 2.1, stroke = 0.7) +
  geom_text(data = st2, aes(x = x + 0.3, y = street + 0.5, label = sprintf("Street\n%.1f", street)), vjust = 0, family = "Figtree", size = 2.2, colour = FOGGY, lineheight = 0.9) +
  scale_fill_manual(values = NCOL) +
  scale_x_continuous(breaks = nd$x, labels = nd$quarter, expand = expansion(add = 0.5)) +
  scale_y_continuous(labels = function(x) paste0(x, "%"), breaks = seq(0, 14, 2), limits = c(-1.3, 14.5)) +
  labs(title = "Without the bundle, nights grow about 7%, not 10%",
       subtitle = paste0("Nights and Seats Booked, year-over-year growth and what it is made of, points. ", leg_n),
       caption = paste(NOTE_BUNDLE, SRC_N)) +
  theme_abnb() + theme(axis.text.x = element_text(size = 6.8))
save_chart(p, "nights", "n01_nights_decomposed_hero", h = 3.9)

# n02 — the same story as two lines: reported/forecast vs underlying
p <- ggplot(nd, aes(x = x)) +
  PANEL_SHADE(xf - 0.5, max(nd$x) + 0.5, "Our model", 13.2) +
  geom_ribbon(data = nd |> filter(quarter %in% c("2Q25", "3Q25", "4Q25", "1Q26", "2Q26", "3Q26", "4Q26", "1Q27", "2Q27")),
              aes(ymin = underlying, ymax = underlying + bundle), fill = RAUSCH, alpha = 0.16) +
  geom_line(aes(y = underlying), colour = FOGGY, linewidth = 0.9, linetype = "22") +
  geom_line(aes(y = total), colour = HOF, linewidth = 1) +
  geom_point(aes(y = total), colour = HOF, size = 1.6) +
  geom_point(data = st2, aes(y = street), shape = 23, fill = "white", colour = HOF, size = 2.2, stroke = 0.7) +
  geom_text(data = st2, aes(y = street, label = sprintf("Street %.1f", street)), nudge_x = 0.4, hjust = 0, family = "Figtree", size = 2.5, colour = FOGGY) +
  annotate("text", x = 8.2, y = 11.2, label = "Bundle: +2 to +3 points", family = "Figtree SemiBold", size = 2.8, colour = RAUSCH) +
  annotate("text", x = 4.25, y = 12.35, hjust = 0, label = "Reported, then our model", family = "Figtree", size = 2.6, colour = HOF) +
  annotate("text", x = 10, y = 6.25, label = "Underlying", family = "Figtree", size = 2.6, colour = FOGGY) +
  scale_x_continuous(breaks = nd$x, labels = nd$quarter, expand = expansion(add = 0.5)) +
  scale_y_continuous(labels = function(x) paste0(x, "%"), breaks = seq(4, 14, 2), limits = c(4, 13.5)) +
  labs(title = "The bundle lifted nights growth by 2–3 points. From 2Q27 it is gone",
       subtitle = paste0("Nights and Seats Booked, year-over-year. ", sw(HOF, "&#9644;"), " reported, then our model  ", sw(FOGGY, "- -"),
                         " underlying (ex bundle, World Cup and Middle East)  ", sw(RAUSCH), " bundle"),
       caption = paste(NOTE_BUNDLE, SRC_N)) +
  theme_abnb() + theme(axis.text.x = element_text(size = 6.8))
save_chart(p, "nights", "n02_reported_vs_underlying_lines", h = 3.7)

# n03 — the bundle's legs and when each laps
LCOL <- c(`US RNPL` = "#D93B40", `International RNPL` = "#FF9A9D", `US fees + cancellation policy` = "#00827A", `International fees + cancellation policy` = "#7FD3CC")
lq <- c("3Q25", "4Q25", "1Q26", "2Q26", "3Q26", "4Q26", "1Q27", "2Q27")
dg <- nd |> filter(quarter %in% lq) |> mutate(x = row_number()) |>
  transmute(x, quarter, bundle, kind, `US RNPL` = na_rnpl, `US fees + cancellation policy` = na_fee, `International fees + cancellation policy` = exna_fee, `International RNPL` = exna_rnpl)
dgl <- dg |> pivot_longer(-c(x, quarter, bundle, kind), names_to = "leg", values_to = "v") |> mutate(leg = factor(leg, levels = rev(names(LCOL))))
laps <- tibble(x = c(5, 6, 7), y = c(3.25, 1.55, 1.15),
               lab = c("US RNPL laps\n(launched Aug 2025)", "Fee and cancellation\nlegs lap (Oct 2025)", "International RNPL laps\n(Feb 2026)"))
p <- ggplot(dgl, aes(x = x, y = v)) +
  PANEL_SHADE(4.5, 8.5, "Our model", 3.75) +
  geom_col(aes(fill = leg), width = 0.66) +
  geom_text(data = dg, aes(x = x, y = bundle + 0.12, label = sprintf("%.1f", bundle)), vjust = 0, family = "Figtree SemiBold", size = 2.7, colour = HOF) +
  geom_text(data = laps, aes(x = x, y = y, label = lab), family = "Figtree", size = 2.3, colour = FOGGY, lineheight = 0.9) +
  annotate("text", x = 2, y = 2.75, label = "Management: ‘over\n200 basis points’", family = "Figtree", size = 2.3, colour = HOF, lineheight = 0.9) +
  annotate("text", x = 3, y = 3.5, label = "‘approximately\nthree points’", family = "Figtree", size = 2.3, colour = HOF, lineheight = 0.9) +
  scale_fill_manual(values = LCOL) +
  scale_x_continuous(breaks = dg$x, labels = dg$quarter, expand = expansion(add = 0.5)) +
  scale_y_continuous(labels = function(x) paste0(x, "pt"), limits = c(0, 3.9), expand = expansion(mult = c(0, 0))) +
  labs(title = "Each leg of the bundle laps on its first anniversary",
       subtitle = paste0("Contribution of the product bundle to nights growth, points of total nights. ", sw("#D93B40"), " US RNPL  ", sw("#FF9A9D"), " international RNPL  ",
                         sw("#00827A"), " US fees + cancellation policy  ", sw("#7FD3CC"), " international"),
       caption = paste("Legs: RNPL +2.40 and fees-plus-cancellation +2.29 points of North America nights (fitted, PR #32), times NA's share of nights; ex-NA 1.65 points (1Q26 call less NA), split 45/55 fees/RNPL (assumed, pinned by the 4Q25 figure). US RNPL laps in full in 3Q26; international RNPL is 40% lapped in 1Q27. 4Q25 includes the NA fee and cancellation legs launched in October.", SRC_N)) +
  theme_abnb()
save_chart(p, "nights", "n03_bundle_legs_lap_schedule", h = 3.8)

# n04 — excess RNPL cancellations by quarter, split by booking cohort
cb <- ct |> filter(scenario == "base") |> mutate(x = row_number())
cbl <- cb |> transmute(x, quarter, `Booked the same quarter` = same_quarter_m, `Booked in earlier quarters` = earlier_cohorts_m) |>
  pivot_longer(-c(x, quarter), names_to = "g", values_to = "v") |> mutate(g = factor(g, levels = c("Booked in earlier quarters", "Booked the same quarter")))
rng <- ct |> filter(scenario != "base") |> select(scenario, quarter, excess_cancels_m) |> pivot_wider(names_from = scenario, values_from = excess_cancels_m) |>
  left_join(cb |> select(quarter, x, excess_cancels_m, earlier_cohorts_m), by = "quarter")
p <- ggplot(cbl, aes(x = x, y = v)) +
  PANEL_SHADE(4.5, max(cb$x) + 0.5, "Our model", 2.62) +
  geom_col(aes(fill = g), width = 0.62) +
  geom_errorbar(data = rng, aes(x = x + 0.36, ymin = bull, ymax = bear), inherit.aes = FALSE, width = 0, colour = MID, linewidth = 0.45) +
  geom_text(data = rng, aes(x = x, y = excess_cancels_m + 0.07, label = ifelse(earlier_cohorts_m > 0, sprintf("%.0f%%", earlier_cohorts_m / excess_cancels_m * 100), "")),
            family = "Figtree", size = 2.4, colour = HOF) +
  scale_fill_manual(values = c(`Booked the same quarter` = "#FF9A9D", `Booked in earlier quarters` = RAUSCH)) +
  scale_x_continuous(breaks = cb$x, labels = cb$quarter, expand = expansion(add = 0.5)) +
  scale_y_continuous(labels = function(x) paste0(x, "m"), limits = c(0, 2.7), expand = expansion(mult = c(0, 0))) +
  labs(title = "Half of RNPL cancellations now come from earlier bookings",
       subtitle = paste0("Excess RNPL cancellations recognised in each quarter, millions of nights, base case. ", sw(RAUSCH), " from earlier quarters' bookings (% labelled)  ",
                         sw("#FF9A9D"), " same quarter. Whisker: bull to bear"),
       caption = paste("Modelled, not disclosed: the cohort engine's base assumes RNPL bookings cancel 4 points more often than others (bear 6, bull 2) on an RNPL share of GBV of ~20% (1Q26 letter) rising to 23%. Reported nights subtract a cancellation in the quarter it happens, not the quarter it was booked. The 2Q26 10-Q says RNPL bookings 'have experienced higher cancellation rates than historic bookings'.", SRC_N)) +
  theme_abnb()
save_chart(p, "nights", "n04_excess_cancellations_by_cohort", h = 3.7)

# n05 — the cancellation drag on nights growth, before and after
cw <- ct |> select(scenario, quarter, drag_pp) |> pivot_wider(names_from = scenario, values_from = drag_pp) |> mutate(x = row_number())
p <- ggplot(cw, aes(x = x)) +
  PANEL_SHADE(4.5, max(cw$x) + 0.5, "Forward: not in our base; it is the short case", -1.3) +
  geom_hline(yintercept = 0, colour = FOGGY, linewidth = 0.35) +
  geom_ribbon(aes(ymin = bear, ymax = bull), fill = RAUSCH, alpha = 0.14) +
  geom_line(aes(y = base), colour = RAUSCH, linewidth = 1) +
  geom_point(aes(y = base), colour = RAUSCH, size = 1.9) +
  geom_text(aes(y = base, label = sprintf("%.2f", base)), vjust = 1.9, family = "Figtree", size = 2.4, colour = HOF) +
  annotate("text", x = 2.5, y = -1.37, label = "Already inside printed nights", family = "Figtree", size = 2.7, colour = FOGGY) +
  annotate("text", x = 9.4, y = -0.52, hjust = 0, label = "Bear: +6pt propensity,\nno rebooking", family = "Figtree", size = 2.4, colour = FOGGY, lineheight = 0.9) +
  scale_x_continuous(breaks = cw$x, labels = cw$quarter, expand = expansion(add = c(0.5, 0.8))) +
  scale_y_continuous(labels = function(x) paste0(x, "pt"), breaks = seq(-1.5, 0, 0.5), limits = c(-1.5, 0.15)) +
  labs(title = "RNPL cancellations cost ~0.5pt of nights growth a quarter in 2026",
       subtitle = paste0("Drag on year-over-year nights growth from excess RNPL cancellations, points. ", sw(RAUSCH, "&#9644;"), " base (+4pt propensity, 25% rebooked)  ",
                         sw(RAUSCH), " bull to bear"),
       caption = paste("Drag = excess cancellations recognised in the quarter less the year-ago quarter's, net of rebooking, over year-ago nights (the module's M3+M4 from 3Q26; the same rule on its cohort matrix before). Our base nights line carries no drag (D1 no-stacking rule); the drag is what separates it from the short case. The one test that could have seen it, a 34-market calendar study, was null (p 0.26).", SRC_N)) +
  theme_abnb() + theme(axis.text.x = element_text(size = 7.4))
save_chart(p, "nights", "n05_cancellation_drag_pp", h = 3.7)

# n06 — implied platform cancellation rate
cr2 <- cr |> mutate(x = match(quarter, unique(cr$quarter)))
ends <- cr2 |> filter(quarter == "4Q27")
p <- ggplot(cr2, aes(x = x, y = platform_cancel_rate_pct, colour = scenario)) +
  geom_hline(yintercept = 16, colour = LIGHT, linewidth = 0.5) +
  geom_hline(yintercept = 17, colour = HOF, linewidth = 0.45, linetype = "22") +
  annotate("text", x = 4.6, y = 15.97, vjust = 1, hjust = 0, label = "16%: ‘historically’ (management, 4Q25 call)", family = "Figtree", size = 2.5, colour = FOGGY) +
  annotate("text", x = 5.6, y = 17.04, vjust = 0, hjust = 0, label = "17%: where management said it is ‘going’", family = "Figtree", size = 2.5, colour = HOF) +
  geom_line(linewidth = 1) + geom_point(size = 1.6) +
  geom_text(data = ends, aes(label = sprintf("%s: RNPL cancels +%.0fpt  %.1f%%", c(bear = "Bear", base = "Base", bull = "Bull")[scenario], propensity_pp, platform_cancel_rate_pct)),
            hjust = 0, nudge_x = 0.25, family = "Figtree", size = 2.5, colour = HOF) +
  scale_colour_manual(values = c(bear = RAUSCH, base = "#FF9A9D", bull = MID)) +
  scale_x_continuous(breaks = 1:10, labels = unique(cr$quarter), expand = expansion(add = c(0.4, 3.6))) +
  scale_y_continuous(labels = function(x) paste0(x, "%"), limits = c(15.85, 17.45)) +
  labs(title = "Management’s ‘16% going to 17%’ is the top of our range",
       subtitle = "Implied platform cancellation rate: 16% historical plus the RNPL share of nights times RNPL's excess cancellation propensity",
       caption = paste("Illustrative arithmetic, not a disclosed series: Airbnb does not report a cancellation rate. RNPL share of nights from the module (share of GBV ~4% and ~9% assumed for 3Q25-4Q25, 'roughly 20%' in 1Q26, 'over 20%' in 2Q26, then 21-27% by scenario). The management quote is from a call transcript mirror (ledger D018); its unit of account is not stated.", SRC_N)) +
  theme_abnb() + theme(axis.text.x = element_text(size = 7.4))
save_chart(p, "nights", "n06_implied_cancellation_rate", h = 3.6)

# n07 — cash stopped following bookings: unearned fees vs GBV
ul <- uf |> mutate(x = row_number()) |> select(x, quarter, gbv_yoy, uf_yoy, uf_minus_gbv) |>
  pivot_longer(c(gbv_yoy, uf_yoy), names_to = "s", values_to = "v") |>
  mutate(xx = x + ifelse(s == "gbv_yoy", -0.18, 0.18))
gp <- uf |> mutate(x = row_number())
p <- ggplot(ul, aes(x = xx, y = v)) +
  annotate("rect", xmin = 3.5, xmax = 6.5, ymin = -Inf, ymax = Inf, fill = "#FFF4F4") +
  annotate("text", x = 5, y = 22.3, label = "RNPL live in the US (Aug 2025), then international (Feb 2026)", family = "Figtree", size = 2.5, colour = FOGGY) +
  geom_hline(yintercept = 0, colour = FOGGY, linewidth = 0.35) +
  geom_col(aes(fill = s), width = 0.34) +
  geom_text(aes(y = v, label = sprintf("%.0f", v), vjust = ifelse(v >= 0, -0.45, 1.3)), family = "Figtree", size = 2.4, colour = FOGGY) +
  geom_text(data = gp, aes(x = x, y = -4.3, label = sprintf("gap %+.0f", uf_minus_gbv)), family = "Figtree SemiBold", size = 2.5,
            colour = ifelse(gp$uf_minus_gbv < -10, RAUSCH, HOF), inherit.aes = FALSE) +
  scale_fill_manual(values = c(gbv_yoy = MID, uf_yoy = RAUSCH)) +
  scale_x_continuous(breaks = gp$x, labels = gp$quarter) +
  scale_y_continuous(labels = function(x) paste0(x, "%"), limits = c(-5.2, 23.5), breaks = seq(0, 20, 5)) +
  labs(title = "Bookings grew 16–19% in 1H26; the fees paid on them didn’t",
       subtitle = paste0("Year-over-year growth. ", sw(MID), " gross booking value  ", sw(RAUSCH), " unearned fees (fees collected on bookings not yet stayed, quarter end)"),
       caption = paste("An RNPL guest pays later, so the fee sits outside unearned fees until payment (FY2025 10-K Note 2). 5 Nov tell, pre-registered: 3Q26 unearned fees y/y minus GBV y/y at or below −18 points supports the unpaid-stock reading; wider than −8 weakens it. Source: Airbnb 10-Qs and 10-K balance sheets; GBV from the letters (data/processed/rnpl_short_audit/verify_bs_yoy_gap_table.csv).")) +
  theme_abnb()
save_chart(p, "nights", "n07_unearned_fees_vs_gbv", h = 3.6)

# n08 — the World Cup in the host cities
w <- wcr |> mutate(m = match(month, unique(month)), lab = format(as.Date(paste0(month, "-01")), "%b"))
wg <- w |> select(m, cls, yoy_pct) |> pivot_wider(names_from = cls, values_from = yoy_pct)
p <- ggplot(w, aes(x = m, y = yoy_pct, colour = cls)) +
  annotate("rect", xmin = 3.6, xmax = 5.4, ymin = -Inf, ymax = Inf, fill = "#FFF8E6") +
  annotate("text", x = 4.5, y = 19.6, label = "Tournament, 11 Jun–19 Jul", family = "Figtree", size = 2.6, colour = FOGGY) +
  geom_hline(yintercept = 0, colour = LIGHT, linewidth = 0.35) +
  geom_segment(data = wg, aes(x = m, xend = m, y = control, yend = host), colour = LIGHT, linewidth = 1.4, inherit.aes = FALSE) +
  geom_line(linewidth = 1) + geom_point(size = 2.2) +
  geom_text(data = w |> filter(m == 5), aes(label = c(host = "19 host markets", control = "19 control markets")[cls]), hjust = 0, nudge_x = 0.15, family = "Figtree", size = 2.7, colour = HOF) +
  scale_colour_manual(values = c(host = BEACH, control = MID)) +
  scale_x_continuous(breaks = 1:5, labels = unique(w$lab), expand = expansion(add = c(0.3, 1.5))) +
  scale_y_continuous(labels = function(x) paste0(x, "%"), limits = c(-3, 20.5)) +
  labs(title = "The World Cup lift was real in the host cities, and small for the platform",
       subtitle = "Inside Airbnb review counts, a proxy for completed stays, year-over-year, 2026",
       caption = "Host markets ran ~4 points ahead of controls before the tournament and ~8 points ahead (difference-in-differences) during it: about 120-180k extra nights, ~0.1 point of global 2Q26 nights growth, against the 0.5 point our model laps in 2Q27. Reviews lag stays by days to weeks. Source: Inside Airbnb review dumps; branch krish/worldcup-premium (uncommitted, 22 Sep 2026), RESULTS.md §3c.") +
  theme_abnb()
save_chart(p, "nights", "n08_worldcup_host_vs_control", h = 3.5)

# n09 — forecast paths: base, base with the cancellation tail, short case, Street
hist <- nd |> filter(kind == "reported")
fc <- nd |> filter(kind == "forecast")
last <- hist |> slice_tail(n = 1)
path <- function(col, nm) bind_rows(last |> transmute(x, v = total), fc |> transmute(x, v = .data[[col]])) |> mutate(s = nm)
paths <- bind_rows(path("total", "base"), path("with_tail", "tail"), path("short_case", "short"))
lab_end <- paths |> group_by(s) |> slice_tail(n = 1) |> ungroup() |>
  mutate(lab = c(base = "Our base", tail = "Base less the\ncancellation tail", short = "Short case")[s],
         y = c(base = 7.0, tail = 5.25, short = 4.0)[s])
p <- ggplot() +
  PANEL_SHADE(xf - 0.5, max(nd$x) + 0.5, "Forecast", 13.4) +
  geom_ribbon(data = fc, aes(x = x, ymin = env_lo_pct, ymax = env_hi_pct), fill = RAUSCH, alpha = 0.12) +
  geom_line(data = hist, aes(x = x, y = total), colour = HOF, linewidth = 1) +
  geom_point(data = hist, aes(x = x, y = total), colour = HOF, size = 1.6) +
  geom_line(data = paths, aes(x = x, y = v, colour = s, linetype = s), linewidth = 0.95) +
  geom_point(data = paths |> filter(x >= xf), aes(x = x, y = v, colour = s), size = 1.5) +
  geom_point(data = st2, aes(x = x, y = street), shape = 23, fill = "white", colour = HOF, size = 2.4, stroke = 0.8) +
  geom_text(data = st2, aes(x = x, y = street + 0.75, label = sprintf("Street %.1f", street)), family = "Figtree", size = 2.4, colour = HOF) +
  geom_text(data = lab_end, aes(x = x + 0.25, y = y, label = lab, colour = s), hjust = 0, family = "Figtree", size = 2.5, lineheight = 0.9) +
  scale_colour_manual(values = c(base = RAUSCH, tail = RAUSCH, short = FOGGY)) +
  scale_linetype_manual(values = c(base = "solid", tail = "22", short = "12")) +
  scale_x_continuous(breaks = nd$x, labels = nd$quarter, expand = expansion(add = c(0.5, 2.6))) +
  scale_y_continuous(labels = function(x) paste0(x, "%"), breaks = seq(0, 14, 2), limits = c(1, 13.8)) +
  labs(title = "We see nights at 6% by 2Q27; the Street prices acceleration",
       subtitle = paste0("Nights and Seats Booked, year-over-year. ", sw(HOF, "&#9644;"), " reported  ", sw(RAUSCH, "&#9644;"), " our base, with its parameter envelope  ",
                         sw(RAUSCH, "- -"), " base less the RNPL cancellation tail  ", sw(FOGGY, "···"), " short case  ", sw(HOF, "&#9671;"), " Street"),
       caption = paste("Base: DEC-0029 (3Q26), DEC-0019 (4Q26), DEC-0025 (2027). Tail: the RNPL module's M3+M4 at +4pt propensity. Short case: a judgement path (margin build 44_short_case_v2, branch krish/cost-leg), zero fitted parameters. Street: Bloomberg MODL, 12 Sep 2026, n 28; no Street nights beyond 4Q26.", SRC_N)) +
  theme_abnb() + theme(axis.text.x = element_text(size = 6.8))
save_chart(p, "nights", "n09_forecast_paths", h = 3.8)

# n10, n11 — nights bridges from 2Q26
nb <- function(q1) {
  a <- nd |> filter(quarter == "2Q26"); b <- nd |> filter(quarter == q1)
  list(a = a, b = b, steps = tibble(lab = c("Underlying", "Bundle laps", "World Cup", "Middle East"),
                                    val = c(b$underlying - a$underlying, b$bundle - a$bundle, b$wc - a$wc, b$me - a$me)) |> filter(abs(val) > 0.005))
}
b <- nb("4Q26")
p <- waterfall("2Q26\nreported", b$a$total, b$steps, "4Q26\nour base", b$b$total, digits = 2) +
  labs(title = sprintf("The 4Q26 slowdown is the bundle lapping: %.1f of the %.1f points", abs(b$steps$val[b$steps$lab == "Bundle laps"]), b$a$total - b$b$total),
       subtitle = "Nights growth, 2Q26 reported to our 4Q26 (the quarter management guides on 5 Nov): what changes, points",
       caption = paste(NOTE_BUNDLE, SRC_N))
save_chart(p, "nights", "n10_bridge_2Q26_to_4Q26", h = 3.5)
b <- nb("2Q27")
p <- waterfall("2Q26\nreported", b$a$total, b$steps, "2Q27\nour base", b$b$total, digits = 2) +
  labs(title = sprintf("A year on, the bundle and World Cup are %.1f of the %.1f points", -sum(b$steps$val[b$steps$lab != "Underlying"]), b$a$total - b$b$total),
       subtitle = "Nights growth, 2Q26 reported to our 2Q27, same season a year on: what changes, points",
       caption = paste(NOTE_BUNDLE, SRC_N))
save_chart(p, "nights", "n11_bridge_2Q26_to_2Q27", h = 3.5)
}

message("done: ", OUT)
