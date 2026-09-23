# 47_pitch_charts / charts.R — candidate charts for thesis 3 (costs) in the two-pager.
# Run from the repo root after prepare_data.py:  Rscript analysis/src/margin_build/47_pitch_charts/charts.R
# Writes deck/figures/thesis3_candidates/*.png (6.5 x 3.6 in, 300 dpi). Font: Figtree (SIL OFL, bundled in fonts/),
# the closest open face to Airbnb Cereal. Colours: Airbnb brand palette (Rausch, Babu, Arches, Hof, Foggy).

suppressPackageStartupMessages({
  library(ggplot2); library(dplyr); library(tidyr); library(readr); library(scales)
  library(ggtext); library(ragg); library(systemfonts); library(forcats); library(stringr)
})

args <- commandArgs(trailingOnly = FALSE)
here <- dirname(normalizePath(sub("--file=", "", args[grep("--file=", args)])))
ROOT <- normalizePath(file.path(here, "../../../.."))
DATA <- file.path(ROOT, "data/processed/margin_build/47_pitch_charts")
OUT  <- file.path(ROOT, "deck/figures/thesis3_candidates"); dir.create(OUT, recursive = TRUE, showWarnings = FALSE)
F <- file.path(here, "fonts")
register_font("Figtree", plain = file.path(F, "Figtree-Regular.ttf"), bold = file.path(F, "Figtree-Bold.ttf"))
register_font("Figtree SemiBold", plain = file.path(F, "Figtree-SemiBold.ttf"), bold = file.path(F, "Figtree-ExtraBold.ttf"))
rd <- function(f) suppressMessages(read_csv(file.path(DATA, f), show_col_types = FALSE))

RAUSCH <- "#FF5A5F"; BABU <- "#00A699"; ARCHES <- "#FC642D"; HOF <- "#484848"; FOGGY <- "#767676"
LIGHT <- "#D8D8D8"; GRID <- "#EDEDED"; INK_SOFT <- "#9A9A9A"
SRC <- "Source: LSEG consensus (11 Sep 2026), Airbnb filings, team model (branch krish/cost-leg)."
sw  <- function(col, glyph = "&#9632;") sprintf("<span style='color:%s'>%s</span>", col, glyph)
pct1 <- function(x) sprintf("%.1f%%", x)
bp <- function(x) paste0(ifelse(x > 0, "+", ifelse(x < 0, "−", "")), abs(round(x * 100)), "bp")

theme_abnb <- function(base = 9.5, grid = "y") {
  t <- theme_minimal(base_family = "Figtree", base_size = base) +
    theme(
      plot.title = element_text(family = "Figtree", face = "bold", size = base * 1.38, colour = HOF, margin = margin(b = 3)),
      plot.subtitle = element_textbox_simple(family = "Figtree", size = base * 0.98, colour = FOGGY, lineheight = 1.25, margin = margin(b = 12)),
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
  t
}
save_chart <- function(p, name, w = 6.5, h = 3.6) {
  ggsave(file.path(OUT, paste0(name, ".png")), p, device = agg_png, width = w, height = h, units = "in", dpi = 300, bg = "white")
  message("saved ", name)
}

# ------------------------------------------------------------------------------------------------------------------
# Bridges (46)
# ------------------------------------------------------------------------------------------------------------------
SHORT <- c("Street consensus" = "Street consensus",
           "Revenue below the Street, costs flexing at the historical rate" = "Lower revenue (costs flex down)",
           "Payments & other cost of revenue" = "Payments & other cost of revenue",
           "Hosting & AI compute" = "Hosting & AI compute",
           "Ops & support: AI support automation" = "AI support automation",
           "Ops & support: payroll, make-goods, insurance" = "Ops & support: payroll, other",
           "Product development" = "Product development",
           "Sales & marketing" = "Sales & marketing",
           "General & administrative" = "G&A",
           "Our model (official income statement)" = "Our model")
bridge_df <- function(per) {
  rd("d01_bridge.csv") |> filter(period %in% per) |>
    group_by(period) |> mutate(i = row_number(), n = n(), y = n - i + 1,
                               lab = unname(SHORT[item]),
                               dir = case_when(kind == "total" ~ "total", value_pp >= 0 ~ "add", TRUE ~ "cut"),
                               next_y = lead(y)) |> ungroup()
}
bridge_plot <- function(d, facet = FALSE, base = 9.5, pad_l = 1, pad_r = 1.6) {
  steps <- d |> filter(kind == "step"); tots <- d |> filter(kind == "total")
  conn <- d |> filter(!is.na(next_y))
  span <- d |> group_by(period) |> summarise(lo = min(c(start[kind == "step"], end)), hi = max(c(start[kind == "step"], end)), .groups = "drop") |>
    mutate(pad = (hi - lo) * 0.18)
  lab_df <- steps |> left_join(span, by = "period") |>
    mutate(x = ifelse(dir == "add", pmax(start, end) + pad * 0.12, pmin(start, end) - pad * 0.12), hj = ifelse(dir == "add", 0, 1), txt = bp(value_pp))
  tot_df <- tots |> left_join(span, by = "period") |> mutate(x = end + (hi - lo) * ifelse(facet, 0.075, 0.03), txt = sprintf("%.2f%%", end))
  ylabs <- d |> distinct(y, lab, kind)
  p <- ggplot() +
    geom_blank(data = span, aes(x = lo - pad * pad_l, y = 1)) + geom_blank(data = span, aes(x = hi + pad * pad_r, y = 1)) +
    geom_segment(data = conn, aes(x = end, xend = end, y = y - 0.3, yend = next_y + 0.3), colour = LIGHT, linewidth = 0.35) +
    geom_rect(data = steps, aes(xmin = pmin(start, end), xmax = pmax(start, end), ymin = y - 0.3, ymax = y + 0.3, fill = dir)) +
    geom_point(data = tots, aes(x = end, y = y), colour = HOF, size = 2.6) +
    geom_text(data = lab_df, aes(x = x, y = y, label = txt, hjust = hj), family = "Figtree", size = base * 0.3, colour = FOGGY) +
    geom_text(data = tot_df, aes(x = x, y = y, label = txt), hjust = 0, family = "Figtree", fontface = "bold", size = base * 0.33, colour = HOF) +
    scale_fill_manual(values = c(add = BABU, cut = RAUSCH)) +
    scale_y_continuous(breaks = ylabs$y, labels = ylabs$lab, expand = expansion(add = 0.5)) +
    scale_x_continuous(labels = function(x) paste0(x, "%"), breaks = scales::breaks_pretty(n = if (facet) 3 else 5), expand = expansion(mult = 0)) +
    theme_abnb(base, grid = "x") + theme(axis.text.y = element_text(colour = HOF, size = base * 0.86, hjust = 0))
  if (facet) p <- p + facet_wrap(~period, nrow = 1, scales = "free_x")
  p
}

p <- bridge_plot(bridge_df("FY27")) +
  labs(title = "Lower revenue takes the first 100bp. Marketing and hosting take the rest",
       subtitle = paste0("FY27 adjusted EBITDA margin, from Street consensus to our model. ", sw(BABU), " adds to margin  ", sw(RAUSCH), " cuts margin"),
       caption = paste("Revenue step: our revenue with the Street's costs falling at the historical rate (0.36% per 1% of revenue). Cost steps: our line build against the Street's plan spread at one growth rate (the Street publishes no line items).", SRC))
save_chart(p, "c01_bridge_fy27", h = 3.9)

p <- bridge_plot(bridge_df(c("3Q26", "4Q26", "FY27")), facet = TRUE, base = 8.6, pad_l = 3.8, pad_r = 4.2) +
  labs(title = "Every period lands below consensus, and for the same two reasons",
       subtitle = paste0("Adjusted EBITDA margin bridges, Street consensus to our model. ", sw(BABU), " adds  ", sw(RAUSCH), " cuts"),
       caption = paste("Each panel has its own scale. Method as in the FY27 bridge.", SRC)) +
  theme(panel.spacing = unit(1.6, "lines"))
save_chart(p, "c02_bridges_three_periods", w = 7.2, h = 3.9)

# ------------------------------------------------------------------------------------------------------------------
# S&M against revenue (02 panel)
# ------------------------------------------------------------------------------------------------------------------
a <- rd("d02_sm_vs_revenue_annual.csv") |> mutate(period = factor(period, levels = period))
p <- ggplot(a, aes(x = period)) +
  geom_segment(aes(xend = period, y = revenue_growth, yend = sm_growth), colour = LIGHT, linewidth = 1.6) +
  geom_point(aes(y = revenue_growth), colour = HOF, size = 3.2) +
  geom_point(aes(y = sm_growth), colour = RAUSCH, size = 3.2) +
  geom_text(aes(y = revenue_growth, label = pct1(revenue_growth)), nudge_x = -0.2, hjust = 1, family = "Figtree", size = 3, colour = HOF) +
  geom_text(aes(y = sm_growth, label = pct1(sm_growth)), nudge_x = 0.2, hjust = 0, family = "Figtree", fontface = "bold", size = 3, colour = HOF) +
  scale_y_continuous(labels = function(x) paste0(x, "%"), limits = c(0, 44), expand = expansion(mult = c(0, 0.02))) +
  labs(title = "When revenue growth slowed, marketing growth didn't",
       subtitle = paste0("Year-over-year growth. ", sw(HOF, "&#9679;"), " revenue  ", sw(RAUSCH, "&#9679;"), " sales & marketing (cash, ex stock comp)"),
       caption = paste("1H26 against 1H25.", SRC)) +
  theme_abnb()
save_chart(p, "c03_sm_vs_revenue_dumbbell")

q <- rd("d03_quarterly_growth.csv") |> filter(quarter %in% c(paste0(1:4, "Q23"), paste0(1:4, "Q24"), paste0(1:4, "Q25"), "1Q26", "2Q26")) |>
  mutate(x = row_number(), gap = sm_yoy > revenue_yoy)
streak <- q |> filter(x >= which(q$quarter == "2Q24"))
p <- ggplot(q, aes(x = x)) +
  geom_ribbon(data = streak, aes(ymin = revenue_yoy, ymax = sm_yoy), fill = RAUSCH, alpha = 0.12) +
  geom_line(aes(y = revenue_yoy), colour = HOF, linewidth = 0.9) +
  geom_line(aes(y = sm_yoy), colour = RAUSCH, linewidth = 0.9) +
  geom_point(data = q |> slice_tail(n = 1), aes(y = revenue_yoy), colour = HOF, size = 2.2) +
  geom_point(data = q |> slice_tail(n = 1), aes(y = sm_yoy), colour = RAUSCH, size = 2.2) +
  annotate("text", x = max(q$x) + 0.25, y = tail(q$sm_yoy, 1), label = "Sales & marketing", hjust = 0, family = "Figtree", size = 3, colour = HOF) +
  annotate("text", x = max(q$x) + 0.25, y = tail(q$revenue_yoy, 1), label = "Revenue", hjust = 0, family = "Figtree", size = 3, colour = HOF) +
  annotate("text", x = mean(streak$x), y = 37, label = "2Q24 to 2Q26: S&M above revenue growth every quarter", family = "Figtree", size = 2.9, colour = FOGGY) +
  scale_x_continuous(breaks = q$x, labels = str_replace(q$quarter, "Q", "Q "), expand = expansion(add = c(0.3, 3.4))) +
  scale_y_continuous(labels = function(x) paste0(x, "%"), limits = c(0, 38)) +
  labs(title = "Marketing has outgrown revenue for nine straight quarters",
       subtitle = paste0("Year-over-year growth by quarter. ", sw(RAUSCH, "&#9644;"), " sales & marketing (cash)  ", sw(HOF, "&#9644;"), " revenue"),
       caption = SRC) +
  theme_abnb() + theme(axis.text.x = element_text(size = 7.4))
save_chart(p, "c04_sm_vs_revenue_quarterly")

sh <- rd("d04_line_shares.csv") |>
  mutate(group = case_when(line == "Sales & marketing" ~ "Sales & marketing", line == "Cost of revenue" ~ "Cost of revenue", TRUE ~ "Ops, product & G&A")) |>
  group_by(period, group) |> summarise(pct = sum(pct), .groups = "drop") |>
  mutate(x = match(period, c("FY22", "FY23", "FY24", "FY25", "FY26E", "FY27E")))
ends <- sh |> filter(period %in% c("FY22", "FY27E"))
cols <- c("Sales & marketing" = RAUSCH, "Ops, product & G&A" = BABU, "Cost of revenue" = FOGGY)
p <- ggplot(sh, aes(x = x, y = pct, colour = group)) +
  annotate("rect", xmin = 4.5, xmax = 6.5, ymin = -Inf, ymax = Inf, fill = "#F7F7F7") +
  annotate("text", x = 5.5, y = 32.6, label = "Our model", family = "Figtree", size = 2.9, colour = FOGGY) +
  geom_line(linewidth = 1) + geom_point(size = 2) +
  geom_text(data = ends |> filter(period == "FY27E"), aes(label = paste0(group, "  ", pct1(pct))), hjust = 0, nudge_x = 0.15, family = "Figtree", size = 3, colour = HOF) +
  geom_text(data = ends |> filter(period == "FY22"), aes(label = pct1(pct)), hjust = 1, nudge_x = -0.15, family = "Figtree", size = 3, colour = FOGGY) +
  scale_colour_manual(values = cols) +
  scale_x_continuous(breaks = 1:6, labels = c("FY22", "FY23", "FY24", "FY25", "FY26E", "FY27E"), expand = expansion(add = c(0.6, 2.4))) +
  scale_y_continuous(labels = function(x) paste0(x, "%"), limits = c(14, 33)) +
  labs(title = "Efficiency in support and overhead is being spent on marketing",
       subtitle = "Cost lines as a share of revenue (cash, ex stock comp). FY26-27 on our revenue, AI savings included",
       caption = SRC) +
  theme_abnb()
save_chart(p, "c05_cost_mix_shift")

# ------------------------------------------------------------------------------------------------------------------
# What consensus needs (41, 45)
# ------------------------------------------------------------------------------------------------------------------
cg <- rd("d05_cost_growth.csv")
bars <- cg |> filter(kind %in% c("actual", "street"), period != "FY28E") |> mutate(period = factor(period, levels = unique(period)),
                                                               fill = case_when(kind == "actual" ~ "actual", period == "FY27E" ~ "hi", TRUE ~ "street"))
ours <- cg |> filter(kind == "ours"); beq <- cg |> filter(kind == "breakeven")
p <- ggplot(bars, aes(x = period, y = growth)) +
  geom_col(aes(fill = fill), width = 0.62) +
  geom_text(aes(label = pct1(growth)), vjust = -0.5, family = "Figtree", size = 3, colour = HOF) +
  geom_vline(xintercept = 5.5, colour = LIGHT, linewidth = 0.4) +
  annotate("text", x = 3, y = 29, label = "Actual", family = "Figtree", size = 3, colour = FOGGY) +
  annotate("text", x = 6.5, y = 29, label = "Consensus (LSEG)", family = "Figtree", size = 3, colour = FOGGY) +
  annotate("segment", x = 7.42, xend = 7.42, y = beq$growth, yend = ours$growth, colour = LIGHT, linewidth = 0.4) +
  annotate("point", x = 7.42, y = ours$growth, colour = RAUSCH, size = 2.4) +
  annotate("point", x = 7.42, y = beq$growth, colour = HOF, shape = 21, fill = "white", size = 2.4, stroke = 0.9) +
  annotate("text", x = 7.6, y = ours$growth, label = paste0("Ours ", pct1(ours$growth)), hjust = 0, family = "Figtree", size = 2.7, colour = HOF) +
  annotate("text", x = 7.6, y = beq$growth, label = paste0("Needed to hold\nconsensus margin\non our revenue ", pct1(beq$growth)), hjust = 0, vjust = 1, family = "Figtree", size = 2.5, colour = FOGGY, lineheight = 0.95) +
  scale_fill_manual(values = c(actual = "#BDBDBD", street = "#E3E3E3", hi = HOF)) +
  scale_y_continuous(labels = function(x) paste0(x, "%"), limits = c(0, 30), expand = expansion(mult = c(0, 0.02))) +
  scale_x_discrete(expand = expansion(add = c(0.6, 2.3))) +
  labs(title = "Consensus needs Airbnb's slowest cost growth since the IPO",
       subtitle = "Growth in costs (revenue minus adjusted EBITDA). Consensus has FY27 costs up 10% after 15% in FY26 (FY28: 8.7%)",
       caption = SRC) +
  theme_abnb()
save_chart(p, "c06_cost_growth_history")

cv <- rd("d06_breakeven_curves.csv") |> pivot_longer(-cost_growth, names_to = "rev", values_to = "margin")
grid <- rd("d11_fy27_grid.csv") |> filter(revenue_path == "official v2")
pts <- tibble(
  lab = c("Consensus", "Our line build", "Generous AI case", "Needed"),
  x = c(10.04, grid$fy27_cost_growth_vs_street_fy26_pct[startsWith(grid$cost_case, "A.")], grid$fy27_cost_growth_vs_street_fy26_pct[startsWith(grid$cost_case, "C.")], 7.297),
  y = c(36.45, grid$fy27_margin_pct[startsWith(grid$cost_case, "A.")], grid$fy27_margin_pct[startsWith(grid$cost_case, "C.")], 36.45),
  col = c(HOF, RAUSCH, BABU, HOF), hj = c(-0.15, 1.15, 1.15, 1.15), vj = c(-0.9, 1.9, 1.9, -0.9))
p <- ggplot(cv, aes(x = cost_growth, y = margin)) +
  geom_hline(yintercept = 36.45, colour = LIGHT, linewidth = 0.4) +
  geom_line(aes(colour = rev), linewidth = 1) +
  geom_point(data = pts, aes(x = x, y = y), colour = pts$col, size = 2.8) +
  geom_text(data = pts, aes(x = x, y = y, label = lab, hjust = hj, vjust = vj), family = "Figtree", size = 2.9, colour = HOF) +
  annotate("text", x = 15.9, y = 35.3, label = "At consensus revenue", hjust = 1, family = "Figtree", size = 2.9, colour = FOGGY) +
  annotate("text", x = 15.9, y = 30.6, label = "At our revenue", hjust = 1, family = "Figtree", size = 2.9, colour = HOF) +
  scale_colour_manual(values = c(margin_street_rev = "#BDBDBD", margin_our_rev = RAUSCH)) +
  scale_x_continuous(labels = function(x) paste0(x, "%"), breaks = seq(4, 16, 2)) +
  scale_y_continuous(labels = function(x) paste0(x, "%"), breaks = seq(30, 42, 2)) +
  coord_cartesian(xlim = c(4, 16), ylim = c(29.5, 41)) +
  labs(title = "On our revenue, holding the Street's margin needs 7% cost growth",
       subtitle = "FY27 adjusted EBITDA margin against FY27 cost growth (on consensus FY26 costs). Consensus is 36.4% at 10.0% growth",
       caption = paste("Generous AI case: support cost per booking −10% across the whole line, product +5%, G&A +3%, lower compute.", SRC)) +
  theme_abnb(grid = "y")
save_chart(p, "c07_breakeven_curve")

sc <- grid |> mutate(short = c("Our line build", "Marketing slows to consensus pace", "Generous AI case", "Generous AI and marketing slows",
                                "Consensus cost plan, flexing with revenue", "Consensus cost plan, fixed"),
                     above = fy27_margin_pct >= 36.45) |> arrange(fy27_margin_pct) |> mutate(y = row_number())
p <- ggplot(sc, aes(y = y)) +
  geom_vline(xintercept = 36.45, colour = HOF, linewidth = 0.5) +
  annotate("text", x = 36.5, y = nrow(sc) + 0.62, label = "Consensus 36.4%", hjust = 0, family = "Figtree", size = 2.9, colour = HOF) +
  geom_segment(aes(x = 36.45, xend = fy27_margin_pct, yend = y), colour = LIGHT, linewidth = 0.9) +
  geom_point(aes(x = fy27_margin_pct, colour = above), size = 3.2) +
  geom_text(aes(x = fy27_margin_pct, label = sprintf("%.1f%%", fy27_margin_pct), hjust = ifelse(above, -0.35, 1.35)), family = "Figtree", size = 2.9, colour = HOF) +
  scale_colour_manual(values = c(`TRUE` = BABU, `FALSE` = RAUSCH)) +
  scale_y_continuous(breaks = sc$y, labels = sc$short, expand = expansion(add = c(0.6, 1.1))) +
  scale_x_continuous(labels = function(x) paste0(x, "%"), limits = c(33, 37.6)) +
  labs(title = "On our revenue, only the most generous cost case reaches consensus",
       subtitle = "FY27 adjusted EBITDA margin on our revenue ($15.4bn, 2.5% below consensus) under each cost case",
       caption = SRC) +
  theme_abnb(grid = "x") + theme(axis.text.y = element_text(colour = HOF))
save_chart(p, "c08_cost_cases")

# ------------------------------------------------------------------------------------------------------------------
# Costs vs consensus at prints (41) and AI in the filings (45)
# ------------------------------------------------------------------------------------------------------------------
cs <- rd("d07_cost_surprise.csv") |> mutate(x = row_number(), above = cost_surprise_pct > 0,
                                            lab = ifelse(str_ends(print_quarter, "Q1"), paste0("1Q", substr(print_quarter, 3, 4)), ""))
p <- ggplot(cs, aes(x = x, y = cost_surprise_pct, fill = above)) +
  annotate("rect", xmin = max(cs$x) - 3.5, xmax = max(cs$x) + 0.5, ymin = -Inf, ymax = Inf, fill = "#F7F7F7") +
  geom_hline(yintercept = 0, colour = FOGGY, linewidth = 0.35) +
  geom_col(width = 0.68) +
  annotate("text", x = max(cs$x) - 1.5, y = -9.5, label = "Above consensus\nin 3 of the last 4", family = "Figtree", size = 2.8, colour = HOF, lineheight = 0.95) +
  scale_fill_manual(values = c(`TRUE` = RAUSCH, `FALSE` = BABU)) +
  scale_x_continuous(breaks = cs$x[cs$lab != ""], labels = cs$lab[cs$lab != ""], expand = expansion(add = 0.6)) +
  scale_y_continuous(labels = function(x) paste0(x, "%")) +
  labs(title = "The cost beats have stopped",
       subtitle = paste0("Actual costs against consensus at each print, % of consensus. ", sw(BABU), " below  ", sw(RAUSCH), " above"),
       caption = paste("Costs = revenue minus adjusted EBITDA. Descriptive; n = 4 recent prints. Consensus: LSEG mean the day before each print.", SRC)) +
  theme_abnb()
save_chart(p, "c09_cost_surprise_history")

ai <- rd("d08_ai_vs_spend.csv") |> mutate(item = fct_reorder(item, usd_m))
p <- ggplot(ai, aes(y = item, x = usd_m, fill = group)) +
  geom_vline(xintercept = 0, colour = FOGGY, linewidth = 0.35) +
  geom_col(width = 0.6) +
  geom_text(aes(label = ifelse(usd_m > 0, paste0("+$", usd_m, "M"), paste0("−$", abs(usd_m), "M")), hjust = ifelse(usd_m > 0, -0.15, 1.15)),
            family = "Figtree", size = 3, colour = HOF) +
  scale_fill_manual(values = c(ai = BABU, other = "#BDBDBD", sm = RAUSCH)) +
  scale_x_continuous(labels = function(x) paste0("$", x, "M"), limits = c(-70, 430)) +
  labs(title = "AI's savings so far are small next to the spending growth",
       subtitle = "Change in 1H26 against 1H25, $M, as described in Airbnb's 2Q26 10-Q",
       caption = "Source: Airbnb 2Q26 10-Q (MD&A). The support saving is “due to lower agent contact volume resulting from increased use of AI”. Payroll lines include stock comp.") +
  theme_abnb(grid = "x") + theme(axis.text.y = element_text(colour = HOF))
save_chart(p, "c10_ai_vs_spending", h = 3.2)

ef <- rd("d02_sm_vs_revenue_annual.csv") |> mutate(period = factor(period, levels = period), hi = period %in% c("FY24", "FY25", "1H26"))
p <- ggplot(ef, aes(x = period, y = incr_rev_per_incr_sm, fill = hi)) +
  geom_col(width = 0.58) +
  geom_text(aes(label = sprintf("$%.1f", incr_rev_per_incr_sm)), vjust = -0.5, family = "Figtree", size = 3.1, colour = HOF) +
  scale_fill_manual(values = c(`TRUE` = RAUSCH, `FALSE` = "#BDBDBD")) +
  scale_y_continuous(labels = function(x) paste0("$", x), limits = c(0, 8.6), expand = expansion(mult = c(0, 0.02))) +
  labs(title = "Each extra marketing dollar comes with less extra revenue",
       subtitle = "Incremental revenue per incremental dollar of sales & marketing (cash), year over year",
       caption = paste("A ratio of increments, not a measured return on marketing. 1H26 against 1H25.", SRC)) +
  theme_abnb()
save_chart(p, "c11_marketing_efficiency", h = 3.3)

# ------------------------------------------------------------------------------------------------------------------
# What it means for the stock (42) and the margin path (12, 13)
# ------------------------------------------------------------------------------------------------------------------
rx <- rd("d10_reaction.csv"); fit <- rd("d10_r1_fit.csv") |> filter(window == "W1")
rx <- rx |> mutate(qlab = paste0(substr(print_quarter, 6, 6), "Q", substr(print_quarter, 3, 4)),
                   show = print_quarter %in% c("2023Q1", "2024Q2", "2024Q3", "2026Q2", "2025Q4", "2024Q4"))
p <- ggplot(rx, aes(x = ntm_ebitda_rev_pct, y = excess_5d_pct)) +
  geom_hline(yintercept = 0, colour = LIGHT, linewidth = 0.35) + geom_vline(xintercept = 0, colour = LIGHT, linewidth = 0.35) +
  geom_abline(intercept = fit$intercept, slope = fit$coef, colour = RAUSCH, linewidth = 0.9) +
  geom_point(colour = HOF, size = 2.4) +
  geom_text(data = rx |> filter(show), aes(label = qlab), nudge_y = 2.6, family = "Figtree", size = 2.7, colour = FOGGY) +
  annotate("text", x = -5.9, y = 16, label = sprintf("Slope %.1f: each 1%% cut to forward\nEBITDA came with a ~%.0f%% fall", fit$coef, fit$coef), hjust = 0, family = "Figtree", size = 2.8, colour = HOF, lineheight = 0.95) +
  scale_x_continuous(labels = function(x) paste0(x, "%")) + scale_y_continuous(labels = function(x) paste0(x, "%")) +
  labs(title = "The stock trades on forward EBITDA, at about twice the revision",
       subtitle = "Five-day return against the Nasdaq-100 after each print since 1Q23 (y) against the change in next-12-month EBITDA consensus (x)",
       caption = paste("n = 14; an association, not a measured price response. Consensus: LSEG, day before and five trading days after each print.", SRC)) +
  theme_abnb(grid = "y")
save_chart(p, "c12_stock_vs_ebitda_revisions")

mh <- rd("d12_margin_history.csv")
rep <- mh |> filter(series == "Reported"); last <- rep |> slice_tail(n = 1)
fc <- bind_rows(mh |> filter(series != "Reported"), last |> mutate(series = "Street"), last |> mutate(series = "Ours"))
xmap <- c(FY22 = 1, FY23 = 2, FY24 = 3, FY25 = 4, FY26E = 5, FY27E = 6)
rep$x <- xmap[rep$period]; fc$x <- xmap[fc$period]
endlab <- fc |> filter(period == "FY27E")
p <- ggplot() +
  annotate("rect", xmin = 4.5, xmax = 6.6, ymin = -Inf, ymax = Inf, fill = "#F7F7F7") +
  annotate("segment", x = 4.8, xend = 5.2, y = 35.5, yend = 35.5, colour = FOGGY, linewidth = 0.6) +
  annotate("text", x = 5.24, y = 35.5, label = "FY26 floor 35.5%", hjust = 0, family = "Figtree", size = 2.6, colour = FOGGY) +
  geom_line(data = rep, aes(x = x, y = margin), colour = HOF, linewidth = 1) +
  geom_line(data = fc, aes(x = x, y = margin, colour = series), linewidth = 1) +
  geom_point(data = rep, aes(x = x, y = margin), colour = HOF, size = 2.2) +
  geom_point(data = fc |> filter(period != "FY25"), aes(x = x, y = margin, colour = series), size = 2.4) +
  geom_text(data = rep, aes(x = x, y = margin, label = pct1(margin), vjust = ifelse(period %in% c("FY22", "FY25"), 2.1, -1.1)), family = "Figtree", size = 2.9, colour = HOF) +
  geom_text(data = endlab, aes(x = x + 0.12, y = margin, label = paste0(ifelse(series == "Ours", "Ours ", "Consensus "), pct1(margin))), hjust = 0, family = "Figtree", size = 3, colour = HOF) +
  scale_colour_manual(values = c(Street = "#A9A9A9", Ours = RAUSCH)) +
  scale_x_continuous(breaks = 1:6, labels = names(xmap), expand = expansion(add = c(0.4, 1.5))) +
  scale_y_continuous(labels = function(x) paste0(x, "%"), limits = c(33, 37.6)) +
  labs(title = "Consensus has margins turning up in FY27. Ours keep falling",
       subtitle = paste0("Adjusted EBITDA margin. ", sw(HOF, "&#9644;"), " reported  ", sw("#A9A9A9", "&#9644;"), " consensus  ", sw(RAUSCH, "&#9644;"), " our model"),
       caption = SRC) +
  theme_abnb()
save_chart(p, "c13_margin_path")

q3 <- rd("d13_q3_margins.csv")
xm <- c("3Q22" = 1, "3Q23" = 2, "3Q24" = 3, "3Q25" = 4, "3Q26E" = 5)
rq <- q3 |> filter(series == "Reported") |> mutate(x = xm[period])
lq <- rq |> slice_tail(n = 1)
fq <- bind_rows(q3 |> filter(series != "Reported") |> mutate(x = 5), lq |> mutate(series = "Street"), lq |> mutate(series = "Ours"))
p <- ggplot() +
  annotate("rect", xmin = 4.5, xmax = 5.6, ymin = -Inf, ymax = Inf, fill = "#F7F7F7") +
  geom_line(data = rq, aes(x = x, y = margin), colour = HOF, linewidth = 1) +
  geom_line(data = fq, aes(x = x, y = margin, colour = series), linewidth = 1) +
  geom_point(data = rq, aes(x = x, y = margin), colour = HOF, size = 2.4) +
  geom_point(data = fq |> filter(x == 5), aes(x = x, y = margin, colour = series), size = 2.6) +
  geom_text(data = rq, aes(x = x, y = margin, label = pct1(margin), vjust = ifelse(period == "3Q22", 2.1, -1.1)), family = "Figtree", size = 2.9, colour = HOF) +
  geom_text(data = fq |> filter(x == 5), aes(x = 5.12, y = margin, label = paste0(ifelse(series == "Ours", "Ours ", "Consensus "), pct1(margin))), hjust = 0, family = "Figtree", size = 2.9, colour = HOF) +
  scale_colour_manual(values = c(Street = "#A9A9A9", Ours = RAUSCH)) +
  scale_x_continuous(breaks = 1:5, labels = names(xm), expand = expansion(add = c(0.4, 1.45))) +
  scale_y_continuous(labels = function(x) paste0(x, "%"), limits = c(48, 55)) +
  labs(title = "The peak-quarter margin has fallen three years running",
       subtitle = paste0("Third-quarter adjusted EBITDA margin. ", sw(HOF, "&#9644;"), " reported  ", sw("#A9A9A9", "&#9644;"), " consensus  ", sw(RAUSCH, "&#9644;"), " our model"),
       caption = SRC) +
  theme_abnb()
save_chart(p, "c14_q3_margin_trend", h = 3.3)

message("done: ", OUT)
