# pitch_charts / two_pager.R — the three charts in the two-pager, in the two-pager style: a numbered title that says what
# the chart shows, a short subtitle, a simple key at the top, factual labels only, one source line, all text black.
# Run from the repo root after prepare_data.py:  Rscript analysis/src/pitch_charts/two_pager.R
# Writes deck/figures/pitch_charts/two_pager/graph{1,2,3}_*.png. Candidates in charts.R are left as they are.

suppressPackageStartupMessages({
  library(ggplot2); library(dplyr); library(tidyr); library(readr); library(scales)
  library(ragg); library(systemfonts); library(stringr); library(ggrepel)
})

args <- commandArgs(trailingOnly = FALSE)
here <- dirname(normalizePath(sub("--file=", "", args[grep("--file=", args)])))
ROOT <- normalizePath(file.path(here, "../../.."))
DATA <- file.path(ROOT, "data/processed/pitch_charts")
OUT  <- file.path(ROOT, "deck/figures/pitch_charts/two_pager"); dir.create(OUT, recursive = TRUE, showWarnings = FALSE)
F <- file.path(here, "fonts")
register_font("Figtree", plain = file.path(F, "Figtree-Regular.ttf"), bold = file.path(F, "Figtree-Bold.ttf"))
register_font("Figtree SemiBold", plain = file.path(F, "Figtree-SemiBold.ttf"), bold = file.path(F, "Figtree-ExtraBold.ttf"))
rd <- function(f) suppressMessages(read_csv(file.path(DATA, f), show_col_types = FALSE))

TXT <- "#000000"                                      # every piece of text on the two-pager charts
RAUSCH <- "#FF5A5F"; BABU <- "#00A699"; HOF <- "#484848"; FOGGY <- "#767676"; BEACH <- "#FFB400"
LIGHT <- "#D8D8D8"; GRID <- "#EDEDED"; MID <- "#BDBDBD"; PALE <- "#F7F7F7"
BASE <- 10.5                                           # was 9.5 in the candidate set
TS <- 1.15                                             # in-plot label scale vs the candidate set
spct1 <- function(x) ifelse(x > 0.049, sprintf("+%.1f%%", x), ifelse(x < -0.049, sprintf("−%.1f%%", abs(x)), "0.0%"))
axpct <- function(x) ifelse(x > 0, paste0("+", x, "%"), ifelse(x < 0, paste0("−", abs(x), "%"), "0%"))
bp <- function(x) paste0(ifelse(x > 0, "+", ifelse(x < 0, "−", "")), abs(round(x * 100)), "bp")

theme_tp <- function(base = BASE, grid = "y") {
  t <- theme_minimal(base_family = "Figtree", base_size = base) +
    theme(
      plot.title = element_text(family = "Figtree", face = "bold", size = base * 1.3, colour = TXT, margin = margin(b = 3)),
      plot.subtitle = element_text(family = "Figtree", size = base * 1.0, colour = TXT, margin = margin(b = 6)),
      plot.caption = element_text(family = "Figtree", size = base * 0.76, colour = TXT, hjust = 0, margin = margin(t = 8)),
      plot.title.position = "plot", plot.caption.position = "plot",
      legend.position = "top", legend.justification = "left", legend.location = "plot", legend.direction = "horizontal",
      legend.title = element_blank(), legend.text = element_text(colour = TXT, size = base * 0.9, margin = margin(l = 3, r = 10)),
      legend.key.size = unit(0.32, "cm"), legend.margin = margin(0, 0, 6, 0), legend.box = "horizontal", legend.box.just = "left",
      legend.spacing.x = unit(2, "pt"), legend.box.spacing = unit(0, "pt"),
      axis.text = element_text(colour = TXT, size = base * 0.9),
      axis.title = element_blank(), axis.ticks = element_blank(),
      panel.grid.minor = element_blank(), panel.grid.major = element_blank(),
      plot.background = element_rect(fill = "white", colour = NA), panel.background = element_rect(fill = "white", colour = NA),
      strip.text = element_text(family = "Figtree SemiBold", colour = TXT, size = base * 1.02, hjust = 0),
      plot.margin = margin(16, 20, 10, 16)
    )
  if (grid == "y") t <- t + theme(panel.grid.major.y = element_line(colour = GRID, linewidth = 0.35))
  if (grid == "x") t <- t + theme(panel.grid.major.x = element_line(colour = GRID, linewidth = 0.35))
  t
}
save_tp <- function(p, name, w = 6.5, h = 3.6) {
  ggsave(file.path(OUT, paste0(name, ".png")), p, device = agg_png, width = w, height = h, units = "in", dpi = 300, bg = "white")
  message("saved two_pager/", name)
}

# ----------------------------------------------------------------------------------------------------------------------
# Graph 1. When both guides miss
# ----------------------------------------------------------------------------------------------------------------------
gates <- rd("s04_two_gates.csv") |> filter(guide != "uncoded") |>
  mutate(key = paste(guide, nights_down),
         lab = c("below 1" = "Revenue guide below Street,\nnights guided lower", "below 0" = "Revenue guide below Street,\nnights not lower",
                 "above 1" = "Revenue guide above Street,\nnights guided lower", "above 0" = "Revenue guide above Street,\nnights not lower")[key],
         y = c("below 1" = 4, "below 0" = 3, "above 1" = 2, "above 0" = 1)[key])
pts <- gates |> select(key, y, prints) |> mutate(prints = str_split(prints, " (?=\\dQ)")) |> unnest(prints) |>
  mutate(q = word(prints, 1), v = as.numeric(sub("−", "-", word(prints, 2))),
         grp = factor(ifelse(key == "below 1", "Both guides missed", "Other prints"), levels = c("Both guides missed", "Other prints")))
p <- ggplot() +
  annotate("rect", xmin = -Inf, xmax = Inf, ymin = 3.5, ymax = 4.5, fill = "#FFF4F4") +
  geom_vline(xintercept = 0, colour = LIGHT, linewidth = 0.4) +
  geom_point(data = gates, aes(x = mean, y = y, shape = "Group average"), size = 6.5, colour = HOF) +
  geom_point(data = pts, aes(x = v, y = y, colour = grp), size = 3, alpha = 0.9) +
  geom_text_repel(data = pts, aes(x = v, y = y, label = q), family = "Figtree", size = 2.3 * TS, colour = TXT, direction = "x",
                  nudge_y = -0.32, segment.colour = NA, seed = 1, box.padding = 0.1) +
  geom_text(data = gates, aes(x = 27, y = y, label = sprintf("%s average\n%d of %d fell", spct1(mean), n_neg, n)), hjust = 1,
            family = "Figtree", size = 2.6 * TS, colour = TXT, lineheight = 0.95) +
  scale_colour_manual(values = c("Both guides missed" = RAUSCH, "Other prints" = MID)) +
  scale_shape_manual(values = c("Group average" = 124)) +
  guides(colour = guide_legend(order = 1, override.aes = list(size = 2.8, alpha = 1)), shape = guide_legend(order = 2, override.aes = list(size = 4.5))) +
  scale_y_continuous(breaks = gates$y, labels = gates$lab, expand = expansion(add = 0.12)) +
  scale_x_continuous(labels = axpct, breaks = seq(-15, 15, 5), limits = c(-14, 27)) +
  labs(title = "Graph 1: When both guides miss, the stock has fallen every time",
       subtitle = "Day-1 return vs QQQ at each print",
       caption = "Source: Airbnb shareholder letters; consensus at each print (LSEG, StreetAccount, FactSet); closing prices.") +
  theme_tp(grid = "x") + theme(axis.text.y = element_text(colour = TXT, size = BASE * 0.86, hjust = 0, lineheight = 1.05))
save_tp(p, "graph1_both_guides_miss", w = 6.8, h = 3.9)

# ----------------------------------------------------------------------------------------------------------------------
# Graph 2. Nights growth with the product bundle's effect separated
# ----------------------------------------------------------------------------------------------------------------------
nd <- rd("n01_nights_decomposition.csv") |> mutate(x = row_number())
xf <- min(nd$x[nd$kind == "forecast"])
NCOL <- c(Underlying = MID, `Product bundle` = RAUSCH, `World Cup` = BEACH, `Middle East` = FOGGY)
dl <- nd |> transmute(x, quarter, Underlying = underlying, `Product bundle` = bundle, `World Cup` = wc, `Middle East` = me) |>
  pivot_longer(-c(x, quarter), names_to = "comp", values_to = "v") |> mutate(comp = factor(comp, levels = names(NCOL)))
st2 <- nd |> filter(!is.na(street))
mk <- bind_rows(nd |> transmute(x, y = total, k = "Nights growth"), st2 |> transmute(x = x + 0.3, y = street, k = "Street consensus"))
p <- ggplot(dl, aes(x = x, y = v)) +
  annotate("rect", xmin = xf - 0.5, xmax = max(nd$x) + 0.5, ymin = -Inf, ymax = Inf, fill = PALE) +
  annotate("text", x = (xf - 0.5 + max(nd$x) + 0.5) / 2, y = 14.4, vjust = 1.3, label = "Forecast", family = "Figtree", size = 2.7 * TS, colour = TXT) +
  geom_hline(yintercept = 0, colour = FOGGY, linewidth = 0.35) +
  geom_col(aes(fill = comp), width = 0.68, position = position_stack(reverse = TRUE)) +
  geom_point(data = mk, aes(x = x, y = y, shape = k), size = 2.2, colour = HOF, fill = "white", stroke = 0.7) +
  geom_text(data = nd, aes(x = x, y = pmax(total, underlying + bundle + pmax(wc, 0)) + 0.8, label = sprintf("%.1f", total)), family = "Figtree SemiBold", size = 2.4 * TS, colour = TXT) +
  geom_text(data = st2, aes(x = x + 0.3, y = street + 0.5, label = sprintf("%.1f", street)), vjust = 0, family = "Figtree", size = 2.3 * TS, colour = TXT) +
  scale_fill_manual(values = NCOL) +
  scale_shape_manual(values = c("Nights growth" = 16, "Street consensus" = 23)) +
  guides(fill = guide_legend(order = 1), shape = guide_legend(order = 2, override.aes = list(size = 2.3))) +
  scale_x_continuous(breaks = nd$x, labels = nd$quarter, expand = expansion(add = 0.5)) +
  scale_y_continuous(labels = function(x) paste0(x, "%"), breaks = seq(0, 14, 2), limits = c(-1.3, 14.6)) +
  labs(title = "Graph 2: Nights growth with the product bundle's effect separated",
       subtitle = "RNPL inflated 1H26 nights; the effect fades in 4Q26 and FY27",
       caption = "Source: Airbnb letters and earnings calls; Bloomberg consensus (12 Sep 2026); team nights model. Year-over-year growth, points.") +
  theme_tp() + theme(axis.text.x = element_text(colour = TXT, size = BASE * 0.76), legend.text = element_text(colour = TXT, size = BASE * 0.82, margin = margin(l = 3, r = 8)))
save_tp(p, "graph2_nights_bundle_separated", w = 7.0, h = 4.0)

# ----------------------------------------------------------------------------------------------------------------------
# Graph 3. Adjusted EBITDA margin bridges, Street consensus to our model
# ----------------------------------------------------------------------------------------------------------------------
br <- rd("r05_margin_bridge.csv") |>
  group_by(period) |> mutate(i = row_number(), n = n(), y = n - i + 1,
                             dir = case_when(kind == "total" ~ "total", value_pp >= 0 ~ "Adds to margin", TRUE ~ "Cuts margin"),
                             next_y = lead(y)) |> ungroup()
steps <- br |> filter(kind == "step"); tots <- br |> filter(kind == "total"); conn <- br |> filter(!is.na(next_y))
span <- br |> group_by(period) |> summarise(lo = min(c(start[kind == "step"], end)), hi = max(c(start[kind == "step"], end)), .groups = "drop") |>
  mutate(pad = (hi - lo) * 0.18)
lab_df <- steps |> left_join(span, by = "period") |>
  mutate(x = ifelse(dir == "Adds to margin", pmax(start, end) + pad * 0.12, pmin(start, end) - pad * 0.12), hj = ifelse(dir == "Adds to margin", 0, 1), txt = bp(value_pp))
tot_df <- tots |> left_join(span, by = "period") |> mutate(x = end + (hi - lo) * 0.075, txt = sprintf("%.2f%%", end))
ylabs <- br |> distinct(y, label)
B3 <- 9.6
p <- ggplot() +
  geom_blank(data = span, aes(x = lo - pad * 3.8, y = 1)) + geom_blank(data = span, aes(x = hi + pad * 4.4, y = 1)) +
  geom_segment(data = conn, aes(x = end, xend = end, y = y - 0.3, yend = next_y + 0.3), colour = LIGHT, linewidth = 0.35) +
  geom_rect(data = steps, aes(xmin = pmin(start, end), xmax = pmax(start, end), ymin = y - 0.3, ymax = y + 0.3, fill = dir)) +
  geom_point(data = tots, aes(x = end, y = y, shape = "Margin"), colour = HOF, size = 2.7) +
  geom_text(data = lab_df, aes(x = x, y = y, label = txt, hjust = hj), family = "Figtree", size = B3 * 0.3, colour = TXT) +
  geom_text(data = tot_df, aes(x = x, y = y, label = txt), hjust = 0, family = "Figtree", fontface = "bold", size = B3 * 0.33, colour = TXT) +
  scale_fill_manual(values = c("Adds to margin" = BABU, "Cuts margin" = RAUSCH)) +
  scale_shape_manual(values = c(Margin = 16)) +
  guides(fill = guide_legend(order = 1), shape = guide_legend(order = 2)) +
  scale_y_continuous(breaks = ylabs$y, labels = ylabs$label, expand = expansion(add = 0.5)) +
  scale_x_continuous(labels = function(x) paste0(x, "%"), breaks = scales::breaks_pretty(n = 3), expand = expansion(mult = 0)) +
  facet_wrap(~period, nrow = 1, scales = "free_x") + coord_cartesian(clip = "off") +
  labs(title = "Graph 3: Adjusted EBITDA margin bridges, Street consensus to our model",
       subtitle = "S&M, hosting & AI compute and lower revenue drive the gap",
       caption = "Source: LSEG consensus (11 Sep 2026); Airbnb filings; team model. Each panel has its own scale.") +
  theme_tp(B3, grid = "x") + theme(axis.text.y = element_text(colour = TXT, size = B3 * 0.9, hjust = 0), panel.spacing = unit(2.4, "lines"))
save_tp(p, "graph3_margin_bridges", w = 7.6, h = 4.2)

message("done: ", OUT)
