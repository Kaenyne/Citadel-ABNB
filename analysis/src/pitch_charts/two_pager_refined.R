# pitch_charts / two_pager_refined.R — the three two-pager charts on the $128 short case, refined Airbnb look (Figtree, Airbnb
# palette, "Graph N:" titles). Differences from two_pager_short.R: Graph 1 fades the three context rows and marks averages as
# diamonds; Graph 2 starts at 1Q25, draws forecasts pale, shows the RNPL cancellation tail as its own part and the Street as a
# dashed tick; Graph 3 keeps the thesis-3 lines (revenue, S&M, hosting & AI compute, AI support savings) and folds the rest into "Other costs (net)".
# Run from the repo root:
#   python analysis/src/pitch_charts/short_case_inputs.py && Rscript analysis/src/pitch_charts/two_pager_refined.R
# Writes deck/figures/pitch_charts/two_pager_refined/graph{1,2,3}_*.png, each 7.2 x 4.1 in at 300 dpi.

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
OUT  <- file.path(ROOT, "deck/figures/pitch_charts", paste0("two_pager_refined_", CASE)); dir.create(OUT, recursive = TRUE, showWarnings = FALSE)
F <- file.path(here, "fonts")
register_font("Figtree", plain = file.path(F, "Figtree-Regular.ttf"), bold = file.path(F, "Figtree-Bold.ttf"))
register_font("Figtree SemiBold", plain = file.path(F, "Figtree-SemiBold.ttf"), bold = file.path(F, "Figtree-ExtraBold.ttf"))
rd <- function(f) suppressMessages(read_csv(file.path(DATA, f), show_col_types = FALSE))

# ---- style ------------------------------------------------------------------------------------------------------------
TXT <- "#000000"; SURFACE <- "#FFFFFF"; MUTED <- "#767676"
RAUSCH <- "#FF5A5F"; BABU <- "#00A699"; HOF <- "#484848"; AMBER <- "#D97500"; VIOLET <- "#7B4BC9"; DEEP <- "#9E1C23"
LIGHT <- "#D8D8D8"; GRID <- "#EDEDED"; MID <- "#BDBDBD"; FADE <- "#D9D9D9"; PALE <- "#F7F7F7"; BAND <- "#FFF1F1"
BASE <- 10.5; TS <- 1.15; FC_ALPHA <- 0.55
W <- 7.2; H <- 4.1
spct1 <- function(x) ifelse(x > 0.049, sprintf("+%.1f%%", x), ifelse(x < -0.049, sprintf("−%.1f%%", abs(x)), "0.0%"))
axpct <- function(x) ifelse(x > 0, paste0("+", x, "%"), ifelse(x < 0, paste0("−", abs(x), "%"), "0%"))
bp <- function(x) paste0(ifelse(x > 0, "+", ifelse(x < 0, "−", "")), abs(round(x * 100)), "bp")

theme_tp <- function(base = BASE, grid = "y") {
  t <- theme_minimal(base_family = "Figtree", base_size = base) +
    theme(
      plot.title = element_text(family = "Figtree", face = "bold", size = base * 1.3, colour = TXT, margin = margin(b = 3)),
      plot.subtitle = element_text(family = "Figtree", size = base * 1.0, colour = TXT, margin = margin(b = 6)),
      plot.caption = element_text(family = "Figtree", size = base * 0.76, colour = MUTED, hjust = 0, margin = margin(t = 8)),
      plot.title.position = "plot", plot.caption.position = "plot",
      legend.position = "top", legend.justification = "left", legend.location = "plot", legend.direction = "horizontal",
      legend.title = element_blank(), legend.text = element_text(colour = TXT, size = base * 0.86, margin = margin(l = 3, r = 9)),
      legend.key.size = unit(0.32, "cm"), legend.margin = margin(0, 0, 6, 0), legend.box = "horizontal", legend.box.just = "left",
      legend.spacing.x = unit(2, "pt"), legend.box.spacing = unit(0, "pt"),
      axis.text = element_text(colour = TXT, size = base * 0.9),
      axis.title = element_blank(), axis.ticks = element_blank(),
      panel.grid.minor = element_blank(), panel.grid.major = element_blank(),
      plot.background = element_rect(fill = SURFACE, colour = NA), panel.background = element_rect(fill = SURFACE, colour = NA),
      strip.text = element_text(family = "Figtree SemiBold", colour = TXT, size = base * 1.05, hjust = 0),
      plot.margin = margin(14, 18, 10, 14)
    )
  if (grid == "y") t <- t + theme(panel.grid.major.y = element_line(colour = GRID, linewidth = 0.35))
  if (grid == "x") t <- t + theme(panel.grid.major.x = element_line(colour = GRID, linewidth = 0.35))
  t
}
save_tp <- function(p, name) {
  ggsave(file.path(OUT, paste0(name, ".png")), p, device = agg_png, width = W, height = H, units = "in", dpi = 300, bg = SURFACE)
  message("saved two_pager_refined/", name)
}

# ----------------------------------------------------------------------------------------------------------------------
# Graph 1. When both guides miss (history only)
# ----------------------------------------------------------------------------------------------------------------------
gates <- rd("s04_two_gates.csv") |> filter(guide != "uncoded") |>
  mutate(key = paste(guide, nights_down), hot = key == "below 1",
         lab = c("below 1" = "Revenue guide below Street,\nnights guided lower", "below 0" = "Revenue guide below Street,\nnights not lower",
                 "above 1" = "Revenue guide above Street,\nnights guided lower", "above 0" = "Revenue guide above Street,\nnights not lower")[key],
         y = c("below 1" = 4, "below 0" = 3, "above 1" = 2, "above 0" = 1)[key])
pts <- gates |> select(key, y, hot, prints) |> mutate(prints = str_split(prints, " (?=\\dQ)")) |> unnest(prints) |>
  mutate(q = word(prints, 1), v = as.numeric(sub("−", "-", word(prints, 2))),
         grp = factor(ifelse(hot, "Both guides missed", "Other prints"), levels = c("Both guides missed", "Other prints")))
# one label per dot (overlapping dots share one); a label flips above its dot when the last label below is closer than GAP points
GAP <- 2.6
labs1 <- pts |> arrange(y, v) |> group_by(y, hot) |> mutate(cl = cumsum(v - lag(v, default = -Inf) >= 0.6)) |>
  group_by(y, hot, cl) |> summarise(v = mean(v), q = paste(q, collapse = ", "), .groups = "drop") |> arrange(y, v) |> mutate(up = FALSE)
last <- c(below = -Inf, above = -Inf); row <- NA
for (i in seq_len(nrow(labs1))) {
  if (!identical(labs1$y[i], row)) { last <- c(below = -Inf, above = -Inf); row <- labs1$y[i] }
  labs1$up[i] <- labs1$v[i] - last[["below"]] < GAP && labs1$v[i] - last[["above"]] >= GAP
  last[[if (labs1$up[i]) "above" else "below"]] <- labs1$v[i]
}
labs1 <- labs1 |> mutate(ly = ifelse(up, y + 0.31, y - 0.31))
p <- ggplot() +
  annotate("rect", xmin = -Inf, xmax = Inf, ymin = 3.52, ymax = 4.48, fill = BAND) +
  geom_vline(xintercept = 0, colour = MID, linewidth = 0.45) +
  geom_segment(data = gates, aes(x = mean, xend = mean, y = y - 0.19, yend = y + 0.19, linetype = "Group average"), colour = HOF, linewidth = 1.2) +
  geom_point(data = pts, aes(x = v, y = y, colour = grp), size = 3.1) +
  # labels sit on a patch of their row's background so the zero line never runs through them
  geom_label(data = labs1 |> filter(hot), aes(x = v, y = ly, label = q), colour = TXT, fill = BAND, family = "Figtree", size = 2.15 * TS,
             linewidth = 0, label.padding = unit(0.06, "lines")) +
  geom_label(data = labs1 |> filter(!hot), aes(x = v, y = ly, label = q), colour = MUTED, fill = SURFACE, family = "Figtree", size = 2.15 * TS,
             linewidth = 0, label.padding = unit(0.06, "lines")) +
  geom_text(data = gates, aes(x = 27, y = y, label = sprintf("%s average\n%d of %d fell", spct1(mean), n_neg, n),
                              fontface = ifelse(hot, "bold", "plain")), hjust = 1, family = "Figtree", size = 2.5 * TS, colour = TXT, lineheight = 0.95) +
  scale_colour_manual(values = c("Both guides missed" = RAUSCH, "Other prints" = FADE, `TRUE` = TXT, `FALSE` = MUTED),
                      breaks = c("Both guides missed", "Other prints")) +
  scale_linetype_manual(values = c("Group average" = "solid")) +
  guides(colour = guide_legend(order = 1, override.aes = list(size = 2.8)), linetype = guide_legend(order = 2, override.aes = list(linewidth = 1.2), keywidth = unit(0.5, "cm"))) +
  scale_y_continuous(breaks = gates$y, labels = gates$lab, expand = expansion(add = c(0.3, 0.1))) +
  scale_x_continuous(labels = axpct, breaks = seq(-15, 15, 5), limits = c(-14, 27)) +
  labs(title = "Graph 1: When both guides miss, the stock has fallen every time",
       subtitle = "Day-1 return vs QQQ at each print",
       caption = "Source: Airbnb shareholder letters; consensus at each print (LSEG, StreetAccount, FactSet); closing prices.") +
  theme_tp(grid = "none") + theme(axis.text.y = element_text(colour = TXT, size = BASE * 0.84, hjust = 0, lineheight = 1.05))
save_tp(p, "graph1_both_guides_miss")

# ----------------------------------------------------------------------------------------------------------------------
# Graph 2. Nights growth and what it is made of, 1Q25-4Q27 (forecast = the $128 short case)
# ----------------------------------------------------------------------------------------------------------------------
nd <- rd(IN[["nights"]]) |> filter(quarter != "1Q24", !str_detect(quarter, "24$")) |> mutate(x = row_number(), fc = kind == "forecast")
xf <- min(nd$x[nd$fc])
NCOL <- c(Underlying = MID, `Product bundle` = RAUSCH, `RNPL cancellations` = DEEP, `World Cup` = AMBER, `Middle East` = VIOLET)
dl <- nd |> transmute(x, fc, Underlying = underlying, `Product bundle` = bundle, `RNPL cancellations` = cancel, `World Cup` = wc, `Middle East` = me) |>
  pivot_longer(-c(x, fc), names_to = "comp", values_to = "v") |> filter(v != 0) |> mutate(comp = factor(comp, levels = names(NCOL))) |>
  arrange(x, v < 0, comp) |> group_by(x) |>
  mutate(ptop = sum(v[v > 0]), hi = ifelse(v > 0, cumsum(pmax(v, 0)), ptop + (cumsum(pmin(v, 0)) - v)), lo = hi - abs(v), neg = v < 0) |> ungroup()
stopifnot(all(abs((dl |> group_by(x) |> summarise(b = min(c(lo[neg], ptop[1]))) |> arrange(x) |> pull(b)) - nd$total) < 1e-6))
st2 <- nd |> filter(!is.na(street))
top <- nd |> mutate(y = underlying + bundle + pmax(wc, 0) + pmax(me, 0))
p <- ggplot(dl, aes(x = x, y = v)) +
  annotate("rect", xmin = xf - 0.5, xmax = max(nd$x) + 0.5, ymin = -Inf, ymax = Inf, fill = PALE) +
  annotate("text", x = xf - 0.35, y = 13.6, hjust = 0, label = "Forecast (pale)", family = "Figtree", size = 2.5 * TS, colour = MUTED) +
  geom_rect(data = dl |> filter(!neg), aes(xmin = x - 0.36, xmax = x + 0.36, ymin = lo, ymax = hi, fill = comp, alpha = fc), colour = SURFACE, linewidth = 0.3) +
  # negative parts: an outlined, lightly filled box removed from the top of the bar; the net bar ends where the box ends
  geom_rect(data = dl |> filter(neg), aes(xmin = x - 0.36, xmax = x + 0.36, ymin = lo, ymax = hi, fill = comp, colour = comp), alpha = 0.22, linewidth = 0.5, linetype = "22") +
  geom_hline(yintercept = 0, colour = HOF, linewidth = 0.45) +
  geom_segment(data = st2, aes(x = x - 0.46, xend = x + 0.46, y = street, yend = street, linetype = "Street consensus"), colour = HOF, linewidth = 0.7) +
  geom_text(data = st2, aes(x = x, y = street + 0.55, label = sprintf("Street %.1f", street)), family = "Figtree", size = 2.2 * TS, colour = TXT) +
  geom_point(data = nd, aes(x = x, y = total, shape = "Nights growth"), size = 2, colour = HOF) +
  geom_text(data = top, aes(x = x, y = y + 0.7, label = sprintf("%.1f", total)), family = "Figtree SemiBold", size = 2.3 * TS, colour = TXT) +
  scale_fill_manual(values = NCOL) + scale_colour_manual(values = NCOL, guide = "none") +
  scale_alpha_manual(values = c(`FALSE` = 1, `TRUE` = FC_ALPHA), guide = "none") +
  scale_shape_manual(values = c("Nights growth" = 16)) +
  scale_linetype_manual(values = c("Street consensus" = "22")) +
  guides(fill = guide_legend(order = 1, override.aes = list(alpha = 1, colour = NA, linetype = 0)), shape = guide_legend(order = 2, override.aes = list(size = 2.2)),
         linetype = guide_legend(order = 3, override.aes = list(linewidth = 0.7), keywidth = unit(0.55, "cm"))) +
  scale_x_continuous(breaks = nd$x, labels = nd$quarter, expand = expansion(add = 0.5)) +
  scale_y_continuous(labels = function(x) paste0(x, "%"), breaks = seq(0, 12, 2), limits = c(0, 13.8), expand = expansion(add = c(0, 0.2))) +
  labs(title = "Graph 2: Nights growth with the product bundle's effect separated",
       subtitle = if (CASE == "caimanes") "As the bundle laps and RNPL cancellations land, growth slows to 7.3% in 4Q26 and ~6% in FY27" else "The bundle laps and RNPL cancellations arrive, taking growth to 5–7% against the Street's 10–11%",
       caption = "Year-over-year, points. Dashed boxes are subtracted; each bar ends at net growth. Source: Airbnb; Bloomberg (12 Sep 2026); team model.") +
  theme_tp() + theme(axis.text.x = element_text(colour = TXT, size = BASE * 0.8), legend.text = element_text(colour = TXT, size = BASE * 0.76, margin = margin(l = 2, r = 6)))
save_tp(p, "graph2_nights_bundle_separated")

# ----------------------------------------------------------------------------------------------------------------------
# Graph 3. Adjusted EBITDA margin bridges, Street consensus to our model: four steps
# ----------------------------------------------------------------------------------------------------------------------
KEEP <- c("Lower revenue (costs flex down)" = "Lower revenue", "Sales & marketing" = "Sales & marketing", "Hosting & AI compute" = "Hosting & AI compute",
          "AI support automation" = "AI support savings")
raw <- rd(IN[["bridge"]])
br <- raw |> mutate(step = case_when(kind == "total" ~ label, label %in% names(KEEP) ~ unname(KEEP[label]), TRUE ~ "Other costs (net)")) |>
  group_by(period, step, kind) |> summarise(value_pp = sum(value_pp), .groups = "drop") |>
  mutate(ord = match(step, c("Street consensus", "Lower revenue", "Sales & marketing", "Hosting & AI compute", "AI support savings", "Other costs (net)", "Our model"))) |>
  arrange(period, ord) |> group_by(period) |>
  mutate(end = ifelse(kind == "total", value_pp, first(value_pp) + cumsum(ifelse(kind == "step", value_pp, 0))),
         start = ifelse(kind == "total", 0, end - value_pp), y = n() - row_number() + 1, next_y = lead(y),
         dir = case_when(kind == "total" ~ "total", value_pp >= 0 ~ "Adds to margin", TRUE ~ "Cuts margin")) |> ungroup()
stopifnot(all(abs(br$end[br$step == "Our model"] - (br |> filter(kind == "step") |> group_by(period) |> summarise(e = last(end)) |> pull(e))) < 1e-9))
steps <- br |> filter(kind == "step"); tots <- br |> filter(kind == "total"); conn <- br |> filter(!is.na(next_y))
span <- br |> group_by(period) |> summarise(lo = min(c(start[kind == "step"], end)), hi = max(c(start[kind == "step"], end)), .groups = "drop") |>
  mutate(pad = (hi - lo) * 0.18)
lab_df <- steps |> left_join(span, by = "period") |>
  mutate(x = ifelse(dir == "Adds to margin", pmax(start, end) + pad * 0.1, pmin(start, end) - pad * 0.1), hj = ifelse(dir == "Adds to margin", 0, 1), txt = bp(value_pp))
tot_df <- tots |> left_join(span, by = "period") |> mutate(x = end + (hi - lo) * 0.08, txt = sprintf("%.1f%%", end))
ylabs <- br |> distinct(y, step)
B3 <- 9.6
p <- ggplot() +
  geom_blank(data = span, aes(x = lo - pad * 3.3, y = 1)) + geom_blank(data = span, aes(x = hi + pad * 3.2, y = 1)) +
  geom_segment(data = conn, aes(x = end, xend = end, y = y - 0.34, yend = next_y + 0.34), colour = LIGHT, linewidth = 0.4) +
  geom_rect(data = steps, aes(xmin = pmin(start, end), xmax = pmax(start, end), ymin = y - 0.34, ymax = y + 0.34, fill = dir)) +
  geom_point(data = tots, aes(x = end, y = y, shape = "Margin"), colour = HOF, size = 2.4) +
  geom_text(data = lab_df, aes(x = x, y = y, label = txt, hjust = hj), family = "Figtree", size = B3 * 0.31, colour = TXT) +
  geom_text(data = tot_df, aes(x = x, y = y, label = txt), hjust = 0, family = "Figtree", fontface = "bold", size = B3 * 0.4, colour = TXT) +
  scale_fill_manual(values = c("Adds to margin" = BABU, "Cuts margin" = RAUSCH)) +
  scale_shape_manual(values = c(Margin = 16)) +
  guides(fill = guide_legend(order = 1, override.aes = list(alpha = 1, colour = NA, linetype = 0)), shape = guide_legend(order = 2)) +
  scale_y_continuous(breaks = ylabs$y, labels = ylabs$step, expand = expansion(add = 0.5)) +
  scale_x_continuous(labels = function(x) paste0(x, "%"), breaks = scales::breaks_pretty(n = 4), expand = expansion(mult = 0)) +
  facet_wrap(~period, nrow = 1, scales = "free_x") + coord_cartesian(clip = "off") +
  labs(title = "Graph 3: Adjusted EBITDA margin bridges, Street consensus to our model",
       subtitle = "S&M, hosting & AI compute and lower revenue drive the gap; AI support savings claw back little",
       caption = paste0("Other costs = payments, support payroll, product development and G&A. Each panel has its own scale. Source: LSEG (", if (CASE == "caimanes") "13" else "11", " Sep 2026); filings; team model.")) +
  theme_tp(B3, grid = "x") + theme(axis.text.y = element_text(colour = TXT, size = B3 * 0.95, hjust = 0), panel.spacing = unit(1.8, "lines"))
save_tp(p, "graph3_margin_bridges")

message("done: ", OUT)
