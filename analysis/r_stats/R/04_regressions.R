# 04_regressions.R - operating leverage, scale economies, marketing efficiency, seasonality tests
source("R/00_setup.R"); d <- readRDS(file.path(DATA, "abnb_tidy.rds")); q <- d$q
qm <- q |> filter(year >= 2022)   # drop the 2021 reopening quarters; n = 18

hac <- function(m) coeftest(m, vcov. = NeweyWest(m, lag = 2, prewhite = FALSE))

# ---- 1. Operating leverage: log(cash cost line) ~ log(revenue) + quarter dummies --------------------------
lines <- c(cor_cash = "Cost of revenue", ops_cash = "Ops & support", pd_cash = "Product dev.", sm_cash = "Sales & marketing",
           ga_cash = "G&A", cash_cost = "Total cash cost", sbc = "SBC")
elas <- map_dfr(names(lines), function(v) {
  m <- lm(reformulate(c("log(revenue)", "factor(qtr)"), response = sprintf("log(%s)", v)), data = qm)
  ct <- hac(m)
  tibble(line = lines[[v]], elasticity = ct["log(revenue)", "Estimate"], se_hac = ct["log(revenue)", "Std. Error"],
         t = ct["log(revenue)", "t value"], p = ct["log(revenue)", "Pr(>|t|)"], r2 = summary(m)$r.squared,
         dw = unname(dwtest(m)$statistic), bp_p = bptest(m)$p.value, n = nobs(m))
})
save_tbl(elas, "05_cost_elasticities", "Elasticity of each cash cost line to revenue (1Q22 to 2Q26, quarter dummies, Newey-West SE). Below 1 = operating leverage")
p <- ggplot(elas |> mutate(line = fct_reorder(line, elasticity)), aes(elasticity, line)) +
  geom_vline(xintercept = 1, colour = INK["axis"], linetype = 2) +
  geom_errorbar(aes(xmin = elasticity - 1.96 * se_hac, xmax = elasticity + 1.96 * se_hac), width = 0.2, orientation = "y", colour = INK["muted"]) +
  geom_point(colour = PAL[["blue"]], size = 3) +
  labs(title = "Cost elasticity to revenue: below 1 means the line grows slower than revenue", subtitle = "Point = OLS elasticity, bar = 95% CI with Newey-West SE; dashed line = proportional growth", x = "elasticity", y = NULL)
save_fig(p, "10_cost_elasticities", 9, 4.5)

# ---- 2. Scale economies: EBITDA margin ~ log(revenue) with quarter dummies -------------------------------------------
m_scale <- lm(ebitda_margin ~ log(revenue) + factor(qtr), data = qm)
m_scale_t <- lm(ebitda_margin ~ log(revenue) + factor(qtr) + t, data = qm)
scale_tbl <- bind_rows(tidy(hac(m_scale)) |> mutate(model = "margin ~ log(rev) + qtr"),
                       tidy(hac(m_scale_t)) |> mutate(model = "margin ~ log(rev) + qtr + trend")) |>
  select(model, term, estimate, std.error, statistic, p.value)
save_tbl(scale_tbl, "06_margin_scale_regression", "Adjusted EBITDA margin on scale (Newey-West SE)")
diag_tbl <- tibble(model = c("margin ~ log(rev) + qtr", "margin ~ log(rev) + qtr + trend"),
                   r2_adj = c(summary(m_scale)$adj.r.squared, summary(m_scale_t)$adj.r.squared),
                   durbin_watson = c(dwtest(m_scale)$statistic, dwtest(m_scale_t)$statistic),
                   breusch_pagan_p = c(bptest(m_scale)$p.value, bptest(m_scale_t)$p.value),
                   shapiro_p = c(shapiro.test(resid(m_scale))$p.value, shapiro.test(resid(m_scale_t))$p.value),
                   max_vif = c(max(vif(m_scale)[, 3]^2), max(vif(m_scale_t)[, 3]^2)))
save_tbl(diag_tbl, "07_regression_diagnostics", "Residual diagnostics")
p <- ggplot(qm, aes(revenue, ebitda_margin)) +
  geom_smooth(method = "lm", formula = y ~ log(x), colour = PAL[["blue"]], fill = SEQ_BLUE[1], linewidth = 0.8) +
  geom_point(aes(colour = factor(qtr)), size = 2.5) +
  geom_text(aes(label = period), size = 2.6, colour = INK["muted"], vjust = -0.9) +
  scale_colour_manual(values = unname(PAL[1:4]), labels = paste0("Q", 1:4)) +
  scale_x_continuous(labels = label_dollar(suffix = "M")) + scale_y_continuous(labels = label_percent()) +
  labs(title = "Margin vs scale, coloured by quarter: the seasonal pattern dominates the size effect", x = "quarterly revenue", y = "Adj. EBITDA margin")
save_fig(p, "11_margin_vs_scale")

# ---- 3. Seasonality tests: one-way ANOVA and Kruskal-Wallis by quarter --------------------------------------------------
seas_tests <- map_dfr(c(nights = "nights", revenue = "revenue", take_rate = "take_rate", ebitda_margin = "ebitda_margin", sm_pct = "sm_pct"),
  function(v) {
    dfv <- qm |> mutate(y = .data[[v]], y_detr = resid(lm(log(abs(y) + 1e-9) ~ t)))
    a <- anova(lm(y_detr ~ factor(qtr), data = dfv)); k <- kruskal.test(y_detr ~ factor(qtr), data = dfv)
    tibble(variable = v, anova_F = a$`F value`[1], anova_p = a$`Pr(>F)`[1], kruskal_chi2 = unname(k$statistic), kruskal_p = k$p.value)
  })
save_tbl(seas_tests, "08_seasonality_tests", "Is the quarter-of-year effect significant? (on log-detrended series)")

# ---- 4. Marketing efficiency: does S&M spend lead nights growth? (cross-correlation) -------------------------------------
xc <- qm |> filter(!is.na(nights_yoy)) |> mutate(sm_yoy = sm_cash / lag(sm_cash, 4) - 1)
xc <- q |> mutate(sm_yoy = sm_cash / lag(sm_cash, 4) - 1) |> filter(!is.na(nights_yoy), !is.na(sm_yoy))
cc <- ccf(xc$sm_yoy, xc$nights_yoy, lag.max = 4, plot = FALSE)
cc_tbl <- tibble(lag_quarters = as.vector(cc$lag), correlation = as.vector(cc$acf)) |>
  mutate(reading = case_when(lag_quarters < 0 ~ "S&M growth leads nights growth", lag_quarters > 0 ~ "nights growth leads S&M growth", TRUE ~ "contemporaneous"))
save_tbl(cc_tbl, "09_sm_vs_nights_ccf", sprintf("Cross-correlation of S&M y/y and nights y/y (n = %d); |r| above %.2f is the 95%% band", nrow(xc), 1.96 / sqrt(nrow(xc))))
p <- ggplot(cc_tbl, aes(lag_quarters, correlation)) +
  geom_hline(yintercept = c(-1, 1) * 1.96 / sqrt(nrow(xc)), linetype = 2, colour = INK["muted"]) + geom_hline(yintercept = 0, colour = INK["axis"]) +
  geom_col(width = 0.5, fill = PAL[["blue"]]) +
  labs(title = "Does marketing spend lead bookings growth?", subtitle = "Negative lags: S&M growth this quarter vs nights growth k quarters later. Dashed: 95% band", x = "lag (quarters)", y = "correlation")
save_fig(p, "12_sm_nights_crosscorrelation", 8, 4.5)

# ---- 5. Take-rate model: what explains the quarterly take rate? -----------------------------------------------------------
m_tr <- lm(take_rate ~ factor(qtr) + t + fx_rev_pp, data = qm)
save_tbl(tidy(hac(m_tr)) |> select(term, estimate, std.error, statistic, p.value), "10_take_rate_regression",
         sprintf("Take rate on quarter dummies, trend and FX-on-revenue (n = %d, Newey-West SE, adj. R2 = %.2f)", nobs(m_tr), summary(m_tr)$adj.r.squared))
message("04_regressions done")
