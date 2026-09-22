# 07_scenarios_montecarlo.R - football field, sensitivity heatmap, Monte Carlo on the FY27 valuation, tornado
source("R/00_setup.R"); d <- readRDS(file.path(DATA, "abnb_tidy.rds")); val <- d$val; grid <- d$grid; model_a <- d$model_a

# ---- 1. Football field from the model's valuation summary ---------------------------------------------------------------------
ff <- val |> filter(!is.na(price), !str_detect(lens, "Football|Reverse|undiscounted|5 Sep")) |>
  mutate(lens = fct_rev(factor(lens, levels = unique(lens))), scenario = factor(scenario, levels = c("Bear","Base","Bull")))
p <- ggplot(ff, aes(price, lens)) +
  geom_vline(xintercept = SPOT, colour = PAL[["red"]], linetype = 2) +
  geom_line(aes(group = lens), colour = INK["axis"], linewidth = 1.5) + geom_point(aes(colour = scenario), size = 3) +
  scale_colour_manual(values = c(Bear = PAL[["orange"]], Base = PAL[["blue"]], Bull = PAL[["aqua"]])) + scale_x_continuous(labels = label_dollar()) +
  labs(title = "Football field: value per share by lens and scenario (driver model, 7 Sep 2026)", subtitle = sprintf("Dashed red = spot $%.2f on %s", SPOT, format(SPOT_DATE, "%d %b %Y")), x = "$ per share", y = NULL)
save_fig(p, "20_football_field", 10, 5)

# ---- 2. Back out net cash and share count from the scenario grid (price = (EBITDA x multiple + net cash) / shares) ------------
gg <- grid |> arrange(fy27_revenue_growth_pct, fy27_margin_pct, exit_ev_ebitda_x) |> group_by(fy27_revenue_growth_pct, fy27_margin_pct) |>
  mutate(ev_ebitda = fy27_adj_ebitda_musd * exit_ev_ebitda_x, shares = (ev_ebitda - lag(ev_ebitda)) / (price - lag(price))) |> ungroup()
SHARES <- median(gg$shares, na.rm = TRUE); NETCASH <- median(gg$price * SHARES - gg$ev_ebitda)
REV26_BASE <- model_a |> filter(scenario == "Base", year == 2026) |> pull(revenue)
message(sprintf("Implied from grid: diluted shares %.1fM, net cash $%.0fM; FY26 base revenue $%.0fM", SHARES, NETCASH, REV26_BASE))

# ---- 3. Sensitivity heatmap: FY27 growth x margin, at three exit multiples ----------------------------------------------------------
mults <- sort(unique(grid$exit_ev_ebitda_x)); pick <- mults[sapply(c(13.5, 16.5, 18.5), function(m) which.min(abs(mults - m)))]
hm <- grid |> filter(exit_ev_ebitda_x %in% pick) |> mutate(multiple = factor(sprintf("%sx EV/EBITDA", exit_ev_ebitda_x), levels = sprintf("%sx EV/EBITDA", pick)))
p <- ggplot(hm, aes(factor(fy27_revenue_growth_pct), factor(fy27_margin_pct), fill = upside_vs_spot_pct)) +
  geom_tile(colour = INK["surface"], linewidth = 0.8) + geom_text(aes(label = round(price)), size = 2.6, colour = INK["primary"]) +
  facet_wrap(~multiple) +
  scale_fill_gradient2(low = PAL[["red"]], mid = INK[["neutral"]], high = PAL[["blue"]], midpoint = 0, name = "upside vs spot (%)") +
  labs(title = "FY27E price per share: revenue growth x EBITDA margin x exit multiple", subtitle = sprintf("Cell label = $ per share; colour = upside vs $%.0f spot", SPOT), x = "FY27 revenue growth (%)", y = "FY27 adj. EBITDA margin (%)") +
  theme(panel.grid = element_blank(), legend.position = "right")
save_fig(p, "21_sensitivity_heatmap", 11, 5)

# ---- 4. Monte Carlo on the three valuation drivers -------------------------------------------------------------------------------------
sc27 <- model_a |> filter(year == 2027) |> select(scenario, revenue_yoy_pct, adj_ebitda_margin_pct)
rng <- list(growth = setNames(sc27$revenue_yoy_pct, sc27$scenario), margin = setNames(sc27$adj_ebitda_margin_pct, sc27$scenario), multiple = c(Bear = 13.5, Base = 16.5, Bull = 18.5))   # Inputs sheet, WS12 exit EV / FY27E adj. EBITDA (the 5 Sep set was 18 / 22 / 25.5x)
rpert <- function(u, lo, mode, hi) { a <- 1 + 4 * (mode - lo) / (hi - lo); b <- 1 + 4 * (hi - mode) / (hi - lo); lo + (hi - lo) * qbeta(u, a, b) }
set.seed(2026); N <- 20000; RHO <- 0.5
Z <- MASS::mvrnorm(N, mu = rep(0, 3), Sigma = matrix(c(1, RHO, RHO, RHO, 1, RHO, RHO, RHO, 1), 3)); U <- pnorm(Z)
sim <- tibble(growth = rpert(U[, 1], rng$growth[["Bear"]], rng$growth[["Base"]], rng$growth[["Bull"]]),
              margin = rpert(U[, 2], rng$margin[["Bear"]], rng$margin[["Base"]], rng$margin[["Bull"]]),
              multiple = rpert(U[, 3], rng$multiple[["Bear"]], rng$multiple[["Base"]], rng$multiple[["Bull"]])) |>
  mutate(revenue27 = REV26_BASE * (1 + growth / 100), ebitda27 = revenue27 * margin / 100,
         price = (ebitda27 * multiple + NETCASH) / SHARES, upside = price / SPOT - 1)
mc_tbl <- sim |> summarise(mean_price = mean(price), median_price = median(price), p5 = quantile(price, 0.05), p25 = quantile(price, 0.25),
                           p75 = quantile(price, 0.75), p95 = quantile(price, 0.95), prob_above_spot = mean(price > SPOT),
                           prob_upside_over_20pct = mean(upside > 0.2), prob_downside_over_20pct = mean(upside < -0.2), expected_upside = mean(upside)) |>
  pivot_longer(everything(), names_to = "statistic")
save_tbl(mc_tbl, "20_monte_carlo_summary", sprintf("Monte Carlo (n = %s) on FY27 growth, margin and exit EV/EBITDA multiple (13.5 / 16.5 / 18.5x); PERT around bear/base/bull, Gaussian copula rho = %.1f", format(N, big.mark = ","), RHO))
p <- ggplot(sim, aes(price)) + geom_histogram(bins = 80, fill = PAL[["blue"]], colour = INK["surface"], linewidth = 0.2) +
  geom_vline(xintercept = SPOT, colour = PAL[["red"]], linetype = 2) + geom_vline(xintercept = median(sim$price), colour = INK["primary"]) +
  annotate("text", x = SPOT, y = Inf, label = sprintf("spot $%.0f", SPOT), vjust = 1.5, hjust = 1.1, size = 3, colour = PAL[["red"]]) +
  annotate("text", x = median(sim$price), y = Inf, label = sprintf("median $%.0f", median(sim$price)), vjust = 3.5, hjust = 1.1, size = 3) +
  scale_x_continuous(labels = label_dollar()) +
  labs(title = "Monte Carlo distribution of FY27E value per share (EV/EBITDA lens)", subtitle = sprintf("P(price > spot) = %.0f%%; P(upside > 20%%) = %.0f%%; P(downside > 20%%) = %.0f%%", 100 * mean(sim$price > SPOT), 100 * mean(sim$upside > 0.2), 100 * mean(sim$upside < -0.2)), x = "$ per share", y = "simulations")
save_fig(p, "22_monte_carlo_price", 9, 5)

# ---- 5. Tornado: one driver at a time to its bear / bull value ----------------------------------------------------------------------------
price_at <- function(g, m, x) (REV26_BASE * (1 + g / 100) * m / 100 * x + NETCASH) / SHARES
base_px <- price_at(rng$growth[["Base"]], rng$margin[["Base"]], rng$multiple[["Base"]])
torn <- tibble(driver = c("FY27 revenue growth", "FY27 EBITDA margin", "Exit EV/EBITDA multiple"),
               low = c(price_at(rng$growth[["Bear"]], rng$margin[["Base"]], rng$multiple[["Base"]]), price_at(rng$growth[["Base"]], rng$margin[["Bear"]], rng$multiple[["Base"]]), price_at(rng$growth[["Base"]], rng$margin[["Base"]], rng$multiple[["Bear"]])),
               high = c(price_at(rng$growth[["Bull"]], rng$margin[["Base"]], rng$multiple[["Base"]]), price_at(rng$growth[["Base"]], rng$margin[["Bull"]], rng$multiple[["Base"]]), price_at(rng$growth[["Base"]], rng$margin[["Base"]], rng$multiple[["Bull"]])),
               bear_value = c(rng$growth[["Bear"]], rng$margin[["Bear"]], rng$multiple[["Bear"]]), base_value = c(rng$growth[["Base"]], rng$margin[["Base"]], rng$multiple[["Base"]]), bull_value = c(rng$growth[["Bull"]], rng$margin[["Bull"]], rng$multiple[["Bull"]])) |>
  mutate(swing = high - low, driver = fct_reorder(driver, swing))
save_tbl(torn |> mutate(base_price = base_px), "21_tornado", "One-at-a-time sensitivity of the FY27E EV/EBITDA price")
p <- ggplot(torn) + geom_vline(xintercept = base_px, colour = INK["primary"]) + geom_vline(xintercept = SPOT, colour = PAL[["red"]], linetype = 2) +
  geom_segment(aes(x = low, xend = base_px, y = driver, yend = driver), colour = PAL[["orange"]], linewidth = 8) +
  geom_segment(aes(x = base_px, xend = high, y = driver, yend = driver), colour = PAL[["aqua"]], linewidth = 8) +
  geom_text(aes(x = low, y = driver, label = dollar(low, 1)), hjust = 1.2, size = 3) + geom_text(aes(x = high, y = driver, label = dollar(high, 1)), hjust = -0.2, size = 3) +
  scale_x_continuous(labels = label_dollar(), expand = expansion(mult = 0.15)) +
  labs(title = "Tornado: which driver moves the FY27E price most?", subtitle = sprintf("Orange = bear value of that driver, aqua = bull; others held at base ($%.0f). Dashed red = spot", base_px), x = "$ per share", y = NULL)
save_fig(p, "23_tornado", 9, 4)

# ---- 6. Model vs Street --------------------------------------------------------------------------------------------------------------------
mv <- model_a |> filter(scenario %in% c("Bear","Base","Bull"), year %in% 2026:2027) |> select(scenario, year, revenue, adj_ebitda, adj_ebitda_margin_pct) |>
  pivot_wider(names_from = scenario, values_from = c(revenue, adj_ebitda, adj_ebitda_margin_pct))
st <- d$street |> filter(str_detect(line, "^FY[0-9]{4} revenue [(][$]M[)]$")) |> mutate(year = as.integer(str_extract(line, "[0-9]{4}"))) |> select(year, street_revenue = street, vendor)
save_tbl(mv |> left_join(st, by = "year") |> mutate(base_vs_street_pct = 100 * (revenue_Base / street_revenue - 1)), "22_model_vs_street", "Driver model scenarios vs Street revenue consensus")
message("07_scenarios_montecarlo done")
