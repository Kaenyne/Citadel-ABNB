# 02_descriptives.R - summary statistics, KPI small multiples, seasonality, correlations
source("R/00_setup.R"); d <- readRDS(file.path(DATA, "abnb_tidy.rds")); q <- d$q

# ---- Table: summary statistics of the core KPIs ---------------------------------------------
kpi_lab <- c(nights = "Nights & experiences (M)", gbv = "GBV ($M)", adr = "ADR ($)", revenue = "Revenue ($M)",
             take_rate = "Take rate", ebitda_margin = "Adj. EBITDA margin", fcf_margin = "FCF margin",
             sbc_pct = "SBC % revenue", cost_per_night = "Cash cost per night ($)")
summ <- q |> select(all_of(names(kpi_lab))) |>
  pivot_longer(everything(), names_to = "var") |>
  group_by(var) |>
  summarise(n = n(), mean = mean(value), sd = sd(value), min = min(value), median = median(value), max = max(value),
            first = first(value), last = last(value), .groups = "drop") |>
  mutate(cagr_4y = if_else(var %in% c("nights","gbv","adr","revenue"), (last / first)^(1 / 5.25) - 1, NA_real_),
         metric = kpi_lab[var]) |>
  select(metric, n, mean, sd, min, median, max, first, last, cagr_4y) |>
  arrange(match(metric, kpi_lab))
save_tbl(summ, "01_summary_stats", "Quarterly KPIs, 1Q21 to 2Q26 (first = 1Q21, last = 2Q26, CAGR over 5.25 years)")

# ---- Figure: KPI small multiples -------------------------------------------------------------
sm <- q |> select(date, all_of(names(kpi_lab)[1:6])) |>
  pivot_longer(-date, names_to = "var") |>
  mutate(var = factor(kpi_lab[var], levels = kpi_lab[1:6]))
p <- ggplot(sm, aes(date, value)) +
  geom_line(colour = PAL[["blue"]], linewidth = 0.8) +
  geom_point(data = sm |> group_by(var) |> slice_tail(n = 1), colour = PAL[["blue"]], size = 2) +
  facet_wrap(~var, scales = "free_y", ncol = 3) +
  scale_y_continuous(labels = label_comma(accuracy = 0.01)) +
  labs(title = "Airbnb quarterly KPIs, 1Q21 to 2Q26", subtitle = "Source: model/ABNB_historicals.xlsx (shareholder letters, 10-Q/10-K)",
       x = NULL, y = NULL)
save_fig(p, "01_kpi_small_multiples", 10, 5.5)

# ---- Figure: seasonality (quarter-of-year lines by year) --------------------------------------
seas <- q |> select(year, qtr, nights, revenue, take_rate, ebitda_margin) |>
  pivot_longer(-c(year, qtr), names_to = "var") |>
  mutate(var = factor(kpi_lab[var], levels = kpi_lab), year = factor(year))
p <- ggplot(seas, aes(qtr, value, colour = year, group = year)) +
  geom_line(linewidth = 0.7) + geom_point(size = 1.6) +
  facet_wrap(~var, scales = "free_y") +
  scale_colour_manual(values = unname(SEQ_BLUE[c(2, 3, 4, 5, 6, 7)])) +
  scale_x_continuous(breaks = 1:4, labels = paste0("Q", 1:4)) +
  labs(title = "Seasonality: each year traced across its four quarters", subtitle = "Q3 is the check-in peak for revenue; Q1 is the booking peak for nights",
       x = NULL, y = NULL)
save_fig(p, "02_seasonality", 10, 5.5)

# ---- Table: seasonal shares (quarter share of full-year revenue and nights) ------------------
seas_tbl <- q |> filter(year %in% 2022:2025) |> group_by(year) |>
  mutate(rev_share = revenue / sum(revenue), nights_share = nights / sum(nights)) |> ungroup() |>
  group_by(quarter = paste0("Q", qtr)) |>
  summarise(revenue_share_mean = mean(rev_share), revenue_share_sd = sd(rev_share),
            nights_share_mean = mean(nights_share), nights_share_sd = sd(nights_share),
            take_rate_mean = mean(take_rate), ebitda_margin_mean = mean(ebitda_margin))
save_tbl(seas_tbl, "02_seasonal_shares", "Quarter share of the full year, FY22 to FY25")

# ---- Figure: year-over-year growth --------------------------------------------------------------
g <- q |> filter(!is.na(rev_yoy)) |> select(date, nights_yoy, adr_yoy, rev_yoy, gbv_yoy) |>
  pivot_longer(-date, names_to = "var") |>
  mutate(var = factor(var, levels = c("rev_yoy","gbv_yoy","nights_yoy","adr_yoy"),
                      labels = c("Revenue", "GBV", "Nights", "ADR")))
p <- ggplot(g, aes(date, value, colour = var)) +
  geom_hline(yintercept = 0, colour = INK["axis"]) +
  geom_line(linewidth = 0.9) +
  scale_colour_manual(values = unname(PAL[1:4])) +
  scale_y_continuous(labels = label_percent()) +
  labs(title = "Year-over-year growth is converging on the low teens", x = NULL, y = "y/y")
save_fig(p, "03_yoy_growth")

# ---- Figure + table: correlation matrix of growth and margin change ------------------------------
cm_vars <- c(nights_yoy = "Nights y/y", adr_yoy = "ADR y/y", take_rate_chg_pts = "Take-rate chg (pts)",
             rev_yoy = "Revenue y/y", d_margin_pts = "Margin chg (pts)", fx_rev_pp = "FX on revenue (pp)",
             sbc_pct = "SBC % rev", sm_pct = "S&M % rev")
cm_df <- q |> select(all_of(names(cm_vars))) |> drop_na()
cm <- cor(cm_df, method = "spearman")
cm_long <- as.data.frame(as.table(cm)) |> rename(x = Var1, y = Var2, rho = Freq) |>
  mutate(x = factor(cm_vars[as.character(x)], levels = cm_vars), y = factor(cm_vars[as.character(y)], levels = rev(cm_vars)))
p <- ggplot(cm_long, aes(x, y, fill = rho)) + geom_tile(colour = INK["surface"], linewidth = 1) +
  geom_text(aes(label = sprintf("%.2f", rho)), size = 3, colour = INK["primary"]) +
  scale_fill_gradient2(low = PAL[["red"]], mid = INK[["neutral"]], high = PAL[["blue"]], limits = c(-1, 1)) +
  labs(title = sprintf("Spearman correlations across %d quarters (1Q22 to 2Q26)", nrow(cm_df)), x = NULL, y = NULL) +
  theme(axis.text.x = element_text(angle = 30, hjust = 1), panel.grid = element_blank(), legend.position = "right")
save_fig(p, "04_correlation_matrix", 8, 6.5)
save_tbl(as.data.frame(cm) |> rownames_to_column("variable"), "03_spearman_correlations", "Spearman rank correlations")

# ---- Figure: regional nights growth (letters, where disclosed) ---------------------------------
reg <- q |> select(date, nights_yoy_na, nights_yoy_emea, nights_yoy_latam, nights_yoy_apac) |>
  pivot_longer(-date, names_to = "region") |> filter(!is.na(value)) |>
  mutate(region = factor(region, levels = c("nights_yoy_na","nights_yoy_emea","nights_yoy_latam","nights_yoy_apac"),
                         labels = c("North America","EMEA","Latin America","Asia Pacific")))
p <- ggplot(reg, aes(date, value, colour = region)) + geom_line(linewidth = 0.9) + geom_point(size = 1.8) +
  scale_colour_manual(values = unname(PAL[1:4])) + scale_y_continuous(labels = label_percent()) +
  labs(title = "Nights growth by region, as disclosed in shareholder letters", subtitle = "Gaps are quarters where the letter gave a band or nothing", x = NULL, y = "y/y")
save_fig(p, "05_regional_nights_growth")
message("02_descriptives done")
