# pitch_charts_pm / graph1_history.R — memo v4.1 Graph 1: nights y/y 1Q23-4Q27, the thesis in one chart.
# The team's STYLE.md nights chart (two_pager_stylemd.R graph_02) extended back to 1Q23 so it shows the multi-year slowdown,
# the bundle's 2026 bump, and the fade to ~6% in 2027 against the Street (Bloomberg 3Q26/4Q26 and FY27 nights).
# Same palette, fonts and sizes as two_pager_stylemd.R (copied, not sourced, because sourcing that file redraws all three charts).
# Run from the repo root:  Rscript analysis/src/pitch_charts_pm/graph1_history.R
# Inputs: data/processed/abnb_quarterly_kpis_from_study.csv (reported nights, 1Q22-2Q26),
#         data/processed/pitch_charts/n07_nights_caimanes.csv (bundle split 3Q25-2Q26, model v2 forecast 3Q26-4Q27, Street 3Q26/4Q26).
# Output: deck/Graphs/pm_feedback_v4_1/graph1_nights_history.png (7.2 x 4.9 in, 300 dpi).

suppressPackageStartupMessages({
  library(ggplot2); library(dplyr); library(tidyr); library(readr); library(ragg); library(stringr)
})
args <- commandArgs(trailingOnly = FALSE)
here <- dirname(normalizePath(sub("--file=", "", args[grep("--file=", args)])))
ROOT <- normalizePath(file.path(here, "../../.."))
OUT <- file.path(ROOT, "deck/Graphs/pm_feedback_v4_1"); dir.create(OUT, recursive = TRUE, showWarnings = FALSE)

# Street FY27 nights growth, Bloomberg consensus (team pull; see deck/drafts/memo_v4_1_2026-09-29/CHANGES.md for the vintage).
STREET_FY27 <- 8.9

# ---- style (from two_pager_stylemd.R) ----
RED <- "#E0484E"; VIOLET <- "#7B4BC9"; AMBER <- "#D97500"; DEEP <- "#9E1C23"
INK <- "#000000"; AXIS <- "#000000"; TITLE <- "#4a4a4a"; MUTED <- "#7a7a7a"; GRIDC <- "#e4e4e4"
BAND <- "#f0f0f0"; CONTEXT <- "#bdbdbd"; SURFACE <- "#FFFFFF"
TS <- 1.7; LW <- 1.5
PT_TITLE <- 7.8 * TS; PT_KEY <- 8 * TS; PT_AXIS <- 7.6 * TS; PT_NOTE <- 6.6 * TS; PT_LABEL <- 6.9 * TS
MM <- 1 / .pt; PT_END <- 1.3
W <- 7.2; H <- 4.9
F_TITLE <- "Arial"; F_BODY <- "Calibri"

# ---- data ----
hist <- read_csv(file.path(ROOT, "data/processed/abnb_quarterly_kpis_from_study.csv"), show_col_types = FALSE) |>
  select(quarter, nights_m) |>
  mutate(q = substr(quarter, 1, 2), yr = as.integer(substr(quarter, 3, 4))) |>
  group_by(q) |> arrange(yr, .by_group = TRUE) |> mutate(total = 100 * (nights_m / lag(nights_m) - 1)) |> ungroup() |>
  filter(yr %in% 23:24 | quarter %in% c("1Q25", "2Q25")) |>
  transmute(quarter, kind = "reported", total, underlying = total, bundle = 0, cancel = 0, wc = 0, me = 0, street = NA_real_)
n07 <- read_csv(file.path(ROOT, "data/processed/pitch_charts/n07_nights_caimanes.csv"), show_col_types = FALSE) |>
  filter(!str_detect(quarter, "24$"), !quarter %in% c("1Q25", "2Q25"))
nd <- bind_rows(hist, n07) |>
  mutate(yr = as.integer(substr(quarter, 3, 4)), q = substr(quarter, 1, 2)) |> arrange(yr, q) |>
  mutate(x = row_number(), fc = kind == "forecast")
stopifnot(nrow(nd) == 20, all(!is.na(nd$total)))
# annual growth from reported nights (FY23-25) and the model (FY26, FY27): checks against the memo's +13.8 / +9.7 / +8.4 / +6.4
yrs <- read_csv(file.path(ROOT, "data/processed/abnb_quarterly_kpis_from_study.csv"), show_col_types = FALSE) |>
  mutate(yr = as.integer(substr(quarter, 3, 4))) |> group_by(yr) |> summarise(n = sum(nights_m), k = n(), .groups = "drop")
fy <- function(y) 100 * (yrs$n[yrs$yr == y] / yrs$n[yrs$yr == y - 1] - 1)
ann <- tibble(yr = 23:27, g = c(fy(23), fy(24), fy(25), 9.03, 6.43), lab = c("FY23", "FY24", "FY25", "FY26E", "FY27E"))
stopifnot(abs(ann$g[1:3] - c(13.8, 9.7, 8.4)) < 0.06)
ann <- ann |> left_join(nd |> group_by(yr) |> summarise(x0 = min(x), x1 = max(x)), by = "yr")

xf <- min(nd$x[nd$fc])
NCOL <- c(Underlying = CONTEXT, Bundle = RED, `RNPL cancels` = DEEP, `World Cup` = AMBER, `Middle East` = VIOLET)
dl <- nd |> transmute(x, fc, Underlying = underlying, Bundle = bundle, `RNPL cancels` = cancel, `World Cup` = wc, `Middle East` = me) |>
  pivot_longer(-c(x, fc), names_to = "comp", values_to = "v") |> filter(v != 0) |> mutate(comp = factor(comp, levels = names(NCOL))) |>
  arrange(x, v < 0, comp) |> group_by(x) |>
  mutate(ptop = sum(v[v > 0]), hi = ifelse(v > 0, cumsum(pmax(v, 0)), ptop + (cumsum(pmin(v, 0)) - v)), lo = hi - abs(v), neg = v < 0) |> ungroup()
stopifnot(all(abs((dl |> group_by(x) |> summarise(b = min(c(lo[neg], ptop[1]))) |> arrange(x) |> pull(b)) - nd$total) < 1e-6))
st <- nd |> filter(!is.na(street))
top <- dl |> group_by(x) |> summarise(y = first(ptop)) |> left_join(nd |> select(x, total), by = "x") |>
  mutate(y = ifelse(abs(y + 0.75 - STREET_FY27) < 0.6 & x >= 17, STREET_FY27 + 0.1, y))   # lift a label off the FY27 line
fy27 <- ann |> filter(yr == 27)
YT <- 22.2   # annual strip height

p <- ggplot() +
  annotate("rect", xmin = xf - 0.5, xmax = max(nd$x) + 0.5, ymin = 0, ymax = 20.6, fill = BAND, alpha = 0.6) +
  geom_rect(data = dl |> filter(!neg), aes(xmin = x - 0.36, xmax = x + 0.36, ymin = lo, ymax = hi, fill = comp, alpha = fc), colour = SURFACE, linewidth = 0.2 * LW) +
  geom_rect(data = dl |> filter(neg), aes(xmin = x - 0.36, xmax = x + 0.36, ymin = lo, ymax = hi, fill = comp, colour = comp), alpha = 0.2, linewidth = 0.35 * LW, linetype = "22") +
  geom_hline(yintercept = 0, colour = INK, linewidth = 0.6 * LW) +
  # Street: 3Q26 and 4Q26 quarterly (Bloomberg, 12 Sep), FY27 annual across the 2027 quarters
  geom_segment(data = st, aes(x = x - 0.46, xend = x + 0.46, y = street, yend = street, linetype = "Street"), colour = INK, linewidth = 0.55 * LW) +
  geom_text(data = st, aes(x = x, y = street + 0.75, label = sprintf("%.1f", street)), family = F_BODY, size = PT_LABEL * 0.9 * MM, colour = INK) +
  annotate("segment", x = fy27$x0 - 0.46, xend = fy27$x1 + 0.46, y = STREET_FY27, yend = STREET_FY27, colour = INK, linewidth = 0.55 * LW, linetype = "22") +
  annotate("text", x = fy27$x1 - 1, y = STREET_FY27 + 0.85, label = sprintf("Street FY27 %.1f", STREET_FY27),
           family = F_BODY, size = PT_LABEL * 0.9 * MM, colour = INK) +
  geom_point(data = nd, aes(x = x, y = total), size = PT_END * LW, colour = INK) +
  geom_text(data = top, aes(x = x, y = y + 0.75, label = sprintf("%.1f", total)), family = F_BODY, fontface = "bold", size = PT_LABEL * 0.82 * MM, colour = INK) +
  # annual strip: full-year growth above each year's four bars
  geom_segment(data = ann, aes(x = x0 - 0.4, xend = x1 + 0.4, y = YT - 1.1, yend = YT - 1.1), colour = MUTED, linewidth = 0.3 * LW) +
  geom_text(data = ann, aes(x = (x0 + x1) / 2, y = YT, label = sprintf("%s  %+.1f%%", lab, g), fontface = ifelse(yr == 27, "bold", "plain")),
            family = F_BODY, size = PT_LABEL * 0.95 * MM, colour = INK) +
  scale_fill_manual(values = NCOL) + scale_colour_manual(values = NCOL, guide = "none") +
  scale_alpha_manual(values = c(`FALSE` = 1, `TRUE` = 0.5), guide = "none") +
  scale_linetype_manual(values = c("Street" = "22")) +
  guides(fill = guide_legend(order = 1, override.aes = list(alpha = 1, colour = NA, linetype = 0)),
         linetype = guide_legend(order = 2, override.aes = list(linewidth = 0.55 * LW), keywidth = unit(0.7, "cm"))) +
  scale_x_continuous(breaks = nd$x, labels = ifelse(nd$q == "1Q", paste0("1Q\n", nd$yr), nd$q), expand = expansion(add = 0.45)) +
  scale_y_continuous(labels = function(v) paste0(v, "%"), breaks = seq(0, 20, 4), limits = c(0, YT + 0.8), expand = expansion(add = c(0, 0))) +
  labs(title = "Nights and Seats Booked, year-over-year growth and its parts, %") +
  theme_minimal(base_family = F_BODY, base_size = PT_AXIS) +
  theme(plot.title = element_text(family = F_TITLE, face = "bold", size = PT_TITLE, colour = TITLE, hjust = 0, margin = margin(b = 6)),
        plot.title.position = "plot",
        axis.text = element_text(family = F_BODY, colour = AXIS, size = PT_AXIS),
        axis.text.x = element_text(family = F_BODY, colour = AXIS, size = PT_AXIS * 0.78, lineheight = 0.85),
        axis.title = element_blank(), axis.ticks = element_blank(), panel.grid = element_blank(),
        panel.grid.major.y = element_line(colour = GRIDC, linewidth = 0.3 * LW),
        plot.background = element_rect(fill = SURFACE, colour = NA), panel.background = element_rect(fill = SURFACE, colour = NA),
        legend.position = "top", legend.justification = "left", legend.location = "plot", legend.direction = "horizontal",
        legend.title = element_blank(), legend.text = element_text(family = F_BODY, colour = INK, size = PT_KEY * 0.86, margin = margin(l = 3, r = 8)),
        legend.key.size = unit(0.42, "cm"), legend.margin = margin(0, 0, 8, 0), legend.box.spacing = unit(0, "pt"),
        legend.box = "horizontal", legend.box.just = "left", legend.spacing.x = unit(2, "pt"),
        plot.margin = margin(12, 16, 10, 2))
ggsave(file.path(OUT, "graph1_nights_history.png"), p, device = agg_png, width = W, height = H, units = "in", dpi = 300, bg = SURFACE)
message("saved ", file.path(OUT, "graph1_nights_history.png"))
print(nd |> select(quarter, total, underlying, bundle), n = 20)
print(ann)
