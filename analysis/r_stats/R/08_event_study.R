# 08_event_study.R - cumulative returns around prints, print-day vs ordinary-day volatility
source("R/00_setup.R"); d <- readRDS(file.path(DATA, "abnb_tidy.rds")); px <- d$px; react <- d$react
PRE <- 10; POST <- 20
ev <- map_dfr(seq_len(nrow(react)), function(i) {
  i0 <- which(px$date >= react$reaction_date[i])[1]; if (is.na(i0) || i0 - PRE < 2 || i0 + POST > nrow(px)) return(NULL)
  idx <- (i0 - PRE):(i0 + POST)
  tibble(quarter = react$quarter[i], k = -PRE:POST, ret = px$ret[idx]) |> mutate(car = cumsum(if_else(k < 0, 0, ret)) * 100, pre = cumsum(ret) * 100)
})
car_tbl <- ev |> filter(k %in% c(0, 1, 5, 10, 20)) |> group_by(k) |>
  summarise(n = n(), mean_car = mean(car), median_car = median(car), sd = sd(car), share_positive = mean(car > 0),
            t_p = t.test(car)$p.value, wilcoxon_p = wilcox.test(car)$p.value)
save_tbl(car_tbl, "23_event_study_car", "Cumulative raw log return (%) from the print-reaction session (k = 0) forward")
mean_path <- ev |> group_by(k) |> summarise(car = mean(car))
p <- ggplot() + geom_hline(yintercept = 0, colour = INK["axis"]) + geom_vline(xintercept = 0, colour = INK["muted"], linetype = 2) +
  geom_line(data = ev, aes(k, car, group = quarter), colour = SEQ_BLUE[2], linewidth = 0.4) +
  geom_line(data = mean_path, aes(k, car), colour = PAL[["orange"]], linewidth = 1.2) +
  geom_text(data = ev |> filter(k == POST), aes(k, car, label = quarter), size = 2.3, hjust = -0.1, colour = INK["muted"]) +
  scale_x_continuous(expand = expansion(mult = c(0.02, 0.12))) +
  labs(title = "Cumulative return from the reaction session for each print (orange = mean)", subtitle = sprintf("%d prints; day 0 = first session after the release", n_distinct(ev$quarter)), x = "sessions after the print", y = "cumulative return (%)")
save_fig(p, "24_event_study_paths", 10, 5.5)

# ---- Volatility: print sessions vs ordinary sessions -----------------------------------------------------------------------------------
rx_dates <- as.Date(sapply(react$reaction_date, function(x) px$date[which(px$date >= x)[1]]), origin = "1970-01-01")
pxv <- px |> filter(!is.na(ret)) |> mutate(print_day = date %in% rx_dates, abs_ret = abs(ret) * 100)
vol_tbl <- pxv |> group_by(print_day = if_else(print_day, "Print session", "Ordinary session")) |>
  summarise(n = n(), mean_abs_return = mean(abs_ret), median_abs_return = median(abs_ret), sd_return = sd(ret) * 100, share_abs_gt_5pct = mean(abs_ret > 5))
vt <- list(levene_p = leveneTest(ret ~ factor(print_day), data = pxv)$`Pr(>F)`[1], mann_whitney_p = wilcox.test(abs_ret ~ print_day, data = pxv)$p.value,
           variance_ratio = var(pxv$ret[pxv$print_day]) / var(pxv$ret[!pxv$print_day]))
save_tbl(bind_rows(vol_tbl, tibble(print_day = sprintf("Tests: variance ratio %.1fx, Levene p = %.2g, Mann-Whitney p = %.2g", vt$variance_ratio, vt$levene_p, vt$mann_whitney_p))), "24_print_day_volatility", "Daily return dispersion on print sessions vs all other sessions")
p <- ggplot(pxv, aes(ret * 100, fill = print_day)) + geom_density(alpha = 0.6, colour = NA) +
  scale_fill_manual(values = c(`FALSE` = PAL[["blue"]], `TRUE` = PAL[["orange"]]), labels = c("Ordinary session", "Print session")) +
  coord_cartesian(xlim = c(-20, 20)) +
  labs(title = "Daily return distribution: print sessions vs ordinary sessions", subtitle = sprintf("Print-session variance is %.0fx the ordinary variance (Levene p = %.2g)", vt$variance_ratio, vt$levene_p), x = "daily log return (%)", y = "density")
save_fig(p, "25_return_distribution", 9, 5)

rv <- px |> filter(!is.na(ret)) |> mutate(rv21 = rollapply(ret, 21, sd, fill = NA, align = "right") * sqrt(252) * 100)
p <- ggplot(rv, aes(date, rv21)) + geom_line(colour = PAL[["blue"]], linewidth = 0.7) +
  geom_vline(xintercept = react$reaction_date, colour = PAL[["orange"]], alpha = 0.5, linewidth = 0.3) +
  labs(title = "21-session realised volatility, annualised (orange ticks = print sessions)", x = NULL, y = "vol (%)")
save_fig(p, "26_realised_volatility", 10, 4.5)

p <- ggplot(px, aes(date, close)) + geom_line(colour = PAL[["blue"]], linewidth = 0.7) +
  geom_point(data = px |> filter(date %in% pxv$date[pxv$print_day]), colour = PAL[["orange"]], size = 1.8) +
  scale_y_continuous(labels = label_dollar()) +
  labs(title = "ABNB close since IPO, print sessions marked", x = NULL, y = NULL)
save_fig(p, "27_price_history", 10, 4.5)
message("08_event_study done")
