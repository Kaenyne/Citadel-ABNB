# 03_growth_decomposition.R - what revenue growth and margin change are made of
source("R/00_setup.R"); d <- readRDS(file.path(DATA, "abnb_tidy.rds")); q <- d$q

# ---- Revenue growth = nights + ADR ex-FX + FX + take rate (log points, from the workbook) --------
dec <- q |> filter(!is.na(c_nights)) |>
  select(date, period, c_nights, c_adr_exfx, c_fx, c_take, rev_yoy) |>
  pivot_longer(c(c_nights, c_adr_exfx, c_fx, c_take), names_to = "driver", values_to = "pts") |>
  mutate(driver = factor(driver, levels = c("c_nights","c_adr_exfx","c_fx","c_take"),
                         labels = c("Nights","ADR ex-FX","FX","Take rate / timing")))
p <- ggplot(dec, aes(date, pts / 100, fill = driver)) +
  geom_col(width = 60, colour = INK["surface"], linewidth = 0.4) +
  geom_point(aes(date, rev_yoy), colour = INK["primary"], size = 1.8, inherit.aes = FALSE, data = distinct(dec, date, rev_yoy)) +
  geom_hline(yintercept = 0, colour = INK["axis"]) +
  scale_fill_manual(values = unname(PAL[1:4])) + scale_y_continuous(labels = label_percent()) +
  labs(title = "Revenue growth decomposition (points of y/y growth)", subtitle = "Bars: contribution by driver (log decomposition). Dots: reported revenue y/y", x = NULL, y = NULL)
save_fig(p, "06_revenue_growth_decomposition")

dec_tbl <- q |> filter(!is.na(c_nights)) |> group_by(year) |>
  summarise(quarters = n(), nights = mean(c_nights), adr_exfx = mean(c_adr_exfx), fx = mean(c_fx),
            take_rate = mean(c_take), reported_yoy_pct = 100 * mean(rev_yoy))
save_tbl(dec_tbl, "04_growth_decomposition_by_year", "Average contribution to revenue y/y growth, points, by year")

# ---- Margin change = cost-line contributions (from section I of the workbook) -----------------------
mb <- q |> filter(!is.na(d_margin_pts)) |>
  select(date, d_margin_pts, d_cor_pts, d_ops_pts, d_pd_pts, d_sm_pts, d_ga_pts, d_da_pts) |>
  pivot_longer(-c(date, d_margin_pts), names_to = "line", values_to = "pts") |>
  mutate(line = factor(line, levels = c("d_cor_pts","d_ops_pts","d_pd_pts","d_sm_pts","d_ga_pts","d_da_pts"),
                       labels = c("Cost of revenue","Ops & support","Product dev.","Sales & marketing","G&A","D&A / add-backs")))
p <- ggplot(mb, aes(date, pts, fill = line)) +
  geom_col(width = 60, colour = INK["surface"], linewidth = 0.4) +
  geom_point(aes(date, d_margin_pts), colour = INK["primary"], size = 1.8, inherit.aes = FALSE, data = distinct(mb, date, d_margin_pts)) +
  geom_hline(yintercept = 0, colour = INK["axis"]) +
  scale_fill_manual(values = unname(PAL[1:6])) +
  coord_cartesian(ylim = c(-12, 12)) +
  labs(title = "What moved the Adjusted EBITDA margin (y/y change, points)", subtitle = "Bars: contribution by cost line (lower cost ratio = positive). Dots: total margin change",
       caption = "Axis clipped at +/-12 pts: 1Q24 and 1Q25 carry offsetting G&A and add-back swings of about 45 pts (one-off accruals that net out).", x = NULL, y = "pts")
save_fig(p, "07_margin_bridge")

# ---- Unit-cost vs revenue-per-night effects ----------------------------------------------------------
ue <- q |> filter(!is.na(unit_cost_effect_pts)) |> select(date, unit_cost_effect_pts, rpn_effect_pts) |>
  pivot_longer(-date, names_to = "effect") |>
  mutate(effect = factor(effect, levels = c("unit_cost_effect_pts","rpn_effect_pts"), labels = c("Unit cost per night", "Revenue per night")))
p <- ggplot(ue, aes(date, value, colour = effect)) + geom_hline(yintercept = 0, colour = INK["axis"]) +
  geom_line(linewidth = 0.9) + geom_point(size = 1.8) +
  scale_colour_manual(values = unname(PAL[1:2])) +
  labs(title = "Margin change split: cost per night vs revenue per night (points)", subtitle = "Since 2024 unit-cost growth (S&M) has eaten most of the revenue-per-night gain", x = NULL, y = "pts")
save_fig(p, "08_unit_cost_vs_revenue_per_night")

# ---- Cost ratios over time -----------------------------------------------------------------------------
cr <- q |> select(date, cor_pct, ops_pct, pd_pct, sm_pct, ga_pct) |> pivot_longer(-date, names_to = "line") |>
  mutate(line = factor(line, levels = c("cor_pct","ops_pct","pd_pct","sm_pct","ga_pct"),
                       labels = c("Cost of revenue","Ops & support","Product dev.","Sales & marketing","G&A")))
p <- ggplot(cr, aes(date, value, colour = line)) + geom_line(linewidth = 0.9) +
  scale_colour_manual(values = unname(PAL[1:5])) + scale_y_continuous(labels = label_percent()) +
  labs(title = "Cash cost lines as a share of revenue", subtitle = "Sales & marketing is the only line not falling as a share of revenue", x = NULL, y = NULL)
save_fig(p, "09_cost_ratios")
message("03_growth_decomposition done")
