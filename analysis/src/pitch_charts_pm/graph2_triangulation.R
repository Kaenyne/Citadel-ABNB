# pitch_charts_pm / graph2_triangulation.R — memo v4.2 Graph 2: every 3Q26 read sits below the Street, on nights and on price.
# Replaces v4's backtest chart (stays index vs reported, 1Q24-2Q26), which read as weak calibration at memo size; the backtest
# result (about 0.7x naive error, both windows) stays in the text.
# Left: 3Q26 nights y/y by route against the Street's 28-estimate range. Right: ADR, ours vs Street, 3Q26 and 4Q26.
# Style copied from two_pager_stylemd.R. Run from the repo root:  Rscript analysis/src/pitch_charts_pm/graph2_triangulation.R
# Output: deck/Graphs/pm_feedback_v4_2/graph2_triangulation.png (7.2 x 4.9 in, 300 dpi).

suppressPackageStartupMessages({ library(ggplot2); library(dplyr); library(readr); library(ragg); library(patchwork) })
args <- commandArgs(trailingOnly = FALSE)
here <- dirname(normalizePath(sub("--file=", "", args[grep("--file=", args)])))
ROOT <- normalizePath(file.path(here, "../../.."))
OUT <- file.path(ROOT, "deck/Graphs/pm_feedback_v4_2"); dir.create(OUT, recursive = TRUE, showWarnings = FALSE)

RED <- "#E0484E"; INK <- "#000000"; TITLE <- "#4a4a4a"; MUTED <- "#7a7a7a"; GRIDC <- "#e4e4e4"; BAND <- "#f0f0f0"
CONTEXT <- "#bdbdbd"; SURFACE <- "#FFFFFF"
TS <- 1.7; LW <- 1.5
PT_TITLE <- 7.8 * TS; PT_KEY <- 8 * TS; PT_AXIS <- 7.6 * TS; PT_LABEL <- 6.9 * TS; MM <- 1 / .pt
F_TITLE <- "Arial"; F_BODY <- "Calibri"

# ---- data ----
# Street 3Q26 nights: Bloomberg, 12 Sep 2026, 28 estimates (stage_e_view_vs_street.csv); stays index v2 read and band from the
# same file; regional build = the team's pre-v2 base (DEC-0029, same file); 12 external series +9.2%
# (deck/drafts/thesis2_nights_adr_v1_2026-09-23.md); our model = model v2 Nights_Engine!B77.
se <- read_csv(file.path(ROOT, "data/processed/forecast_methods/reviews_index_v2/stage_e_view_vs_street.csv"), show_col_types = FALSE) |>
  filter(quarter == "3Q26")
base3q25 <- se$street_m / (1 + se$street_yoy / 100)
st_lo <- 100 * (se$street_low_m / base3q25 - 1); st_hi <- 100 * (se$street_high_m / base3q25 - 1); st_mean <- se$street_yoy
routes <- tibble(
  lab = c("Stays index\n(75M reviews, 123 cities)", "12 external series\n(hotels, flights, statistics)", "Regional build\n(North America vs rest)", "Our model"),
  v = c(se$v2_read_yoy, 9.2, se$base_yoy, 9.2),
  lo = c(se$v2_read_yoy - se$v2_band_pp, NA, NA, NA), hi = c(se$v2_read_yoy + se$v2_band_pp, NA, NA, NA),
  ours = c(FALSE, FALSE, FALSE, TRUE)) |> mutate(y = rev(seq_len(n())))
stopifnot(abs(st_lo - 10.03) < 0.02, abs(st_hi - 13.02) < 0.02, all(routes$v < st_lo))
# ADR: adr_engine_v3 (PR #67; update pack §2): ours 175.66 / 170.96; Street 177.06 / 171.33.
adr <- tibble(q = c("3Q26", "4Q26"), ours = c(175.66, 170.96), street = c(177.06, 171.33))

# ---- left: nights ----
pn <- ggplot() +
  annotate("rect", xmin = st_lo, xmax = st_hi, ymin = -Inf, ymax = Inf, fill = BAND) +
  annotate("text", x = (st_lo + st_hi) / 2, y = 4.75, label = "Street range\n(28 estimates)", family = F_BODY, size = PT_LABEL * 1.1 * MM,
           colour = INK, lineheight = 0.9) +
  annotate("segment", x = st_mean, xend = st_mean, y = 0.55, yend = 4.35, colour = INK, linewidth = 0.55 * LW, linetype = "22") +
  annotate("text", x = st_mean, y = 0.3, label = sprintf("mean %.1f", st_mean), family = F_BODY, size = PT_LABEL * 1.1 * MM, colour = INK) +
  geom_segment(data = routes |> filter(!is.na(lo)), aes(x = lo, xend = hi, y = y, yend = y), colour = CONTEXT, linewidth = 2.2 * LW) +
  geom_point(data = routes, aes(x = v, y = y, colour = ours), size = 2.6 * LW) +
  geom_text(data = routes, aes(x = v, y = y + 0.38, label = sprintf("%.1f", v), fontface = ifelse(ours, "bold", "plain")),
            family = F_BODY, size = PT_LABEL * 1.2 * MM, colour = INK) +
  scale_colour_manual(values = c(`TRUE` = RED, `FALSE` = INK), guide = "none") +
  scale_y_continuous(breaks = routes$y, labels = routes$lab, limits = c(0.1, 5.15), expand = expansion(0)) +
  scale_x_continuous(labels = function(v) paste0(v, "%"), breaks = seq(6, 14, 2), limits = c(6, 14), expand = expansion(0)) +
  labs(title = "3Q26 nights, y/y %") +
  theme_minimal(base_family = F_BODY, base_size = PT_AXIS) +
  theme(plot.title = element_text(family = F_TITLE, face = "bold", size = PT_TITLE * 1.0, colour = TITLE, hjust = 0),
        plot.title.position = "plot", axis.title = element_blank(), axis.ticks = element_blank(), panel.grid = element_blank(),
        panel.grid.major.x = element_line(colour = GRIDC, linewidth = 0.3 * LW),
        axis.text.y = element_text(family = F_BODY, colour = INK, size = PT_AXIS * 0.98, hjust = 0, lineheight = 0.85),
        axis.text.x = element_text(family = F_BODY, colour = INK, size = PT_AXIS * 1.0))

# ---- right: ADR ----
al <- bind_rows(adr |> transmute(q, who = "Street", v = street), adr |> transmute(q, who = "Ours", v = ours)) |>
  mutate(x = as.numeric(factor(q)))
pa <- ggplot(al) +
  geom_segment(data = adr |> mutate(x = row_number()), aes(x = x, xend = x, y = ours, yend = street), colour = CONTEXT, linewidth = 1.2 * LW) +
  geom_point(aes(x = x, y = v, colour = who, shape = who), size = 2.6 * LW) +
  geom_text(aes(x = x + 0.12, y = v, label = sprintf("$%.2f", v), fontface = ifelse(who == "Ours", "bold", "plain")),
            hjust = 0, family = F_BODY, size = PT_LABEL * 1.1 * MM, colour = INK) +
  scale_colour_manual(values = c(Ours = RED, Street = INK)) + scale_shape_manual(values = c(Ours = 16, Street = 95)) +
  scale_x_continuous(breaks = 1:2, labels = adr$q, limits = c(0.55, 3.45), expand = expansion(0)) +
  scale_y_continuous(labels = function(v) paste0("$", v), breaks = seq(170, 178, 2), limits = c(169.5, 178.5)) +
  labs(title = "ADR, $") +
  theme_minimal(base_family = F_BODY, base_size = PT_AXIS) +
  theme(plot.title = element_text(family = F_TITLE, face = "bold", size = PT_TITLE * 1.0, colour = TITLE, hjust = 0),
        plot.title.position = "plot", axis.title = element_blank(), axis.ticks = element_blank(), panel.grid = element_blank(),
        panel.grid.major.y = element_line(colour = GRIDC, linewidth = 0.3 * LW),
        axis.text = element_text(family = F_BODY, colour = INK, size = PT_AXIS * 1.0),
        legend.position = "inside", legend.position.inside = c(0.66, 0.52), legend.direction = "vertical", legend.title = element_blank(),
        legend.text = element_text(family = F_BODY, colour = INK, size = PT_KEY * 1.0), legend.margin = margin(0, 0, 0, 0))

p <- (pn | pa) + plot_layout(widths = c(2.0, 1.1)) &
  theme(plot.background = element_rect(fill = SURFACE, colour = NA), plot.margin = margin(10, 12, 8, 2))
ggsave(file.path(OUT, "graph2_triangulation.png"), p, device = agg_png, width = 7.2, height = 4.9, units = "in", dpi = 300, bg = SURFACE)
message("saved ", file.path(OUT, "graph2_triangulation.png"), sprintf("  street %.2f-%.2f mean %.2f", st_lo, st_hi, st_mean))
