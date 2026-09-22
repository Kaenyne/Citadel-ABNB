# 05_time_series.R - STL, ETS/ARIMA forecasts vs the driver model, rolling-origin backtest, structural breaks
source("R/00_setup.R"); d <- readRDS(file.path(DATA, "abnb_tidy.rds")); q <- d$q; model_q <- d$model_q
H <- 6; fq <- c("3Q26","4Q26","1Q27","2Q27","3Q27","4Q27")
GUIDE_3Q26 <- c(low = 4690, high = 4770); STREET_3Q26 <- 4740   # 2Q26 letter and Card_5Nov sheet

ts_of <- function(v) ts(q[[v]], start = c(2021, 1), frequency = 4)
fc_set <- function(v) {
  y <- log(ts_of(v))
  f_ets <- forecast(ets(y), h = H); f_ar <- forecast(auto.arima(y, stepwise = FALSE, approximation = FALSE, max.d = 1, max.D = 1), h = H)
  f_sn <- forecast(snaive(y, h = H)); f_rwd <- forecast(rwf(y, drift = TRUE, h = H))
  tibble(quarter = fq, h = 1:H,
         ets = exp(as.numeric(f_ets$mean)), ets_lo80 = exp(as.numeric(f_ets$lower[, 1])), ets_hi80 = exp(as.numeric(f_ets$upper[, 1])),
         arima = exp(as.numeric(f_ar$mean)), arima_lo80 = exp(as.numeric(f_ar$lower[, 1])), arima_hi80 = exp(as.numeric(f_ar$upper[, 1])),
         seasonal_naive = exp(as.numeric(f_sn$mean))) |>
    list(fc = _, ets_model = f_ets$method, arima_model = f_ar$method)
}
fc_rev <- fc_set("revenue"); fc_nights <- fc_set("nights")

mq <- model_q |> select(quarter, scenario, revenue, nights) |>
  pivot_wider(names_from = scenario, values_from = c(revenue, nights))
rev_tbl <- fc_rev$fc |> left_join(mq |> select(quarter, starts_with("revenue_")), by = "quarter") |>
  mutate(guide_low = if_else(quarter == "3Q26", GUIDE_3Q26[["low"]], NA_real_), guide_high = if_else(quarter == "3Q26", GUIDE_3Q26[["high"]], NA_real_),
         street = if_else(quarter == "3Q26", STREET_3Q26, NA_real_))
save_tbl(rev_tbl, "11_revenue_forecasts_vs_model", sprintf("Revenue ($M): statistical forecasts (%s; %s) vs the driver model's scenarios, 3Q26 guide and Street", fc_rev$ets_model, fc_rev$arima_model))
nights_tbl <- fc_nights$fc |> left_join(mq |> select(quarter, starts_with("nights_")), by = "quarter")
save_tbl(nights_tbl, "12_nights_forecasts_vs_model", sprintf("Nights (M): statistical forecasts (%s; %s) vs the driver model", fc_nights$ets_model, fc_nights$arima_model))

plot_fc <- function(fc, v, mq_prefix, title, ylab, guide = NULL) {
  hist_df <- q |> select(date, value = all_of(v)) |> mutate(series = "Actual")
  fdates <- as.Date(as.yearqtr(qtr_to_yq(fc$fc$quarter)), frac = 1)
  fdf <- fc$fc |> mutate(date = fdates)
  lines_df <- bind_rows(fdf |> transmute(date, value = ets, series = "ETS"), fdf |> transmute(date, value = arima, series = "ARIMA"))
  mdf <- model_q |> select(quarter, scenario, value = all_of(v)) |> mutate(date = as.Date(as.yearqtr(qtr_to_yq(quarter)), frac = 1))
  p <- ggplot() +
    geom_ribbon(data = fdf, aes(date, ymin = ets_lo80, ymax = ets_hi80), fill = SEQ_BLUE[1], alpha = 0.8) +
    geom_line(data = hist_df, aes(date, value, colour = series), linewidth = 0.9) +
    geom_line(data = lines_df, aes(date, value, colour = series), linewidth = 0.9, linetype = "42") +
    geom_point(data = mdf, aes(date, value, shape = scenario), colour = PAL[["orange"]], size = 2.4) +
    scale_colour_manual(values = c(Actual = INK[["primary"]], ETS = PAL[["blue"]], ARIMA = PAL[["aqua"]])) +
    scale_shape_manual(values = c(Bear = 6, Base = 16, Bull = 2)) +
    scale_y_continuous(labels = label_comma()) +
    labs(title = title, subtitle = "Dashed: ETS and ARIMA on the log series, shaded: ETS 80% interval. Orange: driver model bear / base / bull", x = NULL, y = ylab)
  if (!is.null(guide)) p <- p + annotate("segment", x = fdates[1] - 20, xend = fdates[1] + 20, y = guide[1], yend = guide[1], colour = PAL[["red"]]) +
    annotate("segment", x = fdates[1] - 20, xend = fdates[1] + 20, y = guide[2], yend = guide[2], colour = PAL[["red"]]) +
    annotate("text", x = fdates[1] + 25, y = mean(guide), label = "3Q26 guide", hjust = 0, size = 3, colour = PAL[["red"]])
  p
}
save_fig(plot_fc(fc_rev, "revenue", "revenue", "Quarterly revenue: time-series forecasts vs the driver model", "$M", GUIDE_3Q26), "13_revenue_forecast_vs_model", 10, 5.5)
save_fig(plot_fc(fc_nights, "nights", "nights", "Nights & experiences booked: time-series forecasts vs the driver model", "M"), "14_nights_forecast_vs_model", 10, 5.5)

# ---- STL decomposition of log revenue ----------------------------------------------------------------------------------------
s <- stl(log(ts_of("revenue")), s.window = "periodic")
stl_df <- bind_rows(tibble(date = q$date, component = "log revenue", value = as.numeric(log(ts_of("revenue")))),
                    tibble(date = q$date, component = "trend", value = as.numeric(s$time.series[, "trend"])),
                    tibble(date = q$date, component = "seasonal", value = as.numeric(s$time.series[, "seasonal"])),
                    tibble(date = q$date, component = "remainder", value = as.numeric(s$time.series[, "remainder"]))) |>
  mutate(component = factor(component, levels = c("log revenue","trend","seasonal","remainder")))
p <- ggplot(stl_df, aes(date, value)) + geom_line(colour = PAL[["blue"]], linewidth = 0.8) +
  facet_wrap(~component, ncol = 1, scales = "free_y") +
  labs(title = "STL decomposition of log quarterly revenue", subtitle = "Seasonal amplitude is about +/-0.2 log points; the trend is decelerating smoothly", x = NULL, y = NULL)
save_fig(p, "15_stl_revenue", 9, 7)
seas_idx <- tibble(quarter = paste0("Q", 1:4), seasonal_factor = exp(as.numeric(s$time.series[1:4, "seasonal"])))
save_tbl(seas_idx, "13_stl_seasonal_factors", "Multiplicative seasonal factors for revenue (STL)")

# ---- Rolling-origin backtest: which simple method forecasts next quarter best? ----------------------------------------------------
bt <- map_dfr(12:20, function(o) {          # origins 4Q23 .. 4Q25, forecast 1 and 2 quarters ahead
  y <- log(ts_of("revenue")); ytr <- window(y, end = time(y)[o]); act <- exp(as.numeric(y))[o + 1:2]
  hh <- sum(!is.na(act))
  f <- list(ETS = exp(as.numeric(forecast(ets(ytr), h = 2)$mean)), ARIMA = exp(as.numeric(forecast(auto.arima(ytr, max.d = 1, max.D = 1), h = 2)$mean)),
            `Seasonal naive` = exp(as.numeric(snaive(ytr, h = 2)$mean)),
            `Last y/y growth` = exp(as.numeric(ytr)[length(ytr) - 3:2] + (as.numeric(ytr)[length(ytr)] - as.numeric(ytr)[length(ytr) - 4])))
  map_dfr(names(f), ~ tibble(origin = q$period[o], method = .x, h = 1:2, forecast = f[[.x]], actual = act)) |> filter(!is.na(actual))
})
bt_tbl <- bt |> mutate(ape = abs(forecast / actual - 1)) |> group_by(method, h) |>
  summarise(n = n(), MAPE = mean(ape), median_APE = median(ape), bias = mean(forecast / actual - 1), .groups = "drop") |> arrange(h, MAPE)
save_tbl(bt_tbl, "14_forecast_backtest", "Rolling-origin backtest of revenue (origins 4Q23 to 4Q25)")

# ---- Structural breaks (mean shift) in the y/y series --------------------------------------------------------------------------
brk <- map_dfr(c(take_rate_chg_pts = "Take-rate change (pts)", d_margin_pts = "Margin change (pts)", nights_yoy = "Nights y/y", adr_yoy = "ADR y/y", rev_yoy = "Revenue y/y"),
  function(lbl) {
    v <- names(which(c(take_rate_chg_pts = "Take-rate change (pts)", d_margin_pts = "Margin change (pts)", nights_yoy = "Nights y/y", adr_yoy = "ADR y/y", rev_yoy = "Revenue y/y") == lbl))
    dd <- q |> filter(!is.na(.data[[v]])); y <- dd[[v]]
    fs <- Fstats(y ~ 1, from = 0.2); st <- sctest(fs, type = "supF")
    bp <- breakpoints(y ~ 1, h = 4); nb <- length(bp$breakpoints[!is.na(bp$breakpoints)])
    tibble(series = lbl, n = length(y), supF = unname(st$statistic), p_supF = st$p.value,
           break_after = if (nb > 0) dd$period[bp$breakpoints[1]] else NA_character_,
           mean_before = if (nb > 0) mean(y[seq_len(bp$breakpoints[1])]) else mean(y),
           mean_after = if (nb > 0) mean(y[-seq_len(bp$breakpoints[1])]) else NA_real_,
           adf_p = suppressWarnings(adf.test(y)$p.value), kpss_p = suppressWarnings(kpss.test(y)$p.value))
  })
save_tbl(brk, "15_structural_breaks", "supF test for a mean shift (Andrews), BIC-chosen break date, ADF and KPSS p-values")

# Figure: nights y/y and revenue y/y with the segment means
seg_plot <- function(v, lbl) {
  dd <- q |> filter(!is.na(.data[[v]])); y <- dd[[v]]; bp <- breakpoints(y ~ 1, h = 4)
  dd$segment <- if (length(bp$breakpoints[!is.na(bp$breakpoints)])) breakfactor(bp) else factor(1)
  dd |> group_by(segment) |> mutate(seg_mean = mean(.data[[v]])) |> ungroup() |> mutate(series = lbl, value = .data[[v]]) |> select(date, series, value, seg_mean)
}
sp <- bind_rows(seg_plot("nights_yoy", "Nights y/y"), seg_plot("rev_yoy", "Revenue y/y"), seg_plot("adr_yoy", "ADR y/y"))
p <- ggplot(sp, aes(date, value)) + geom_hline(yintercept = 0, colour = INK["axis"]) +
  geom_step(aes(y = seg_mean), colour = PAL[["orange"]], linewidth = 0.9) + geom_line(colour = PAL[["blue"]], linewidth = 0.8) + geom_point(colour = PAL[["blue"]], size = 1.5) +
  facet_wrap(~series, ncol = 1, scales = "free_y") + scale_y_continuous(labels = label_percent()) +
  labs(title = "Growth regimes: BIC-chosen mean shifts (orange) in the y/y series", x = NULL, y = NULL)
save_fig(p, "16_growth_regimes", 9, 7)
message("05_time_series done")
