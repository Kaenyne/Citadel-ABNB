# 09_pitch_figures.R - memo-sized crops of the exhibits used in the two-page pitch
source("R/00_setup.R"); d <- readRDS(file.path(DATA, "abnb_tidy.rds")); q <- d$q

dec <- q |> filter(!is.na(c_nights), year >= 2024) |>
  select(period, yq, c_nights, c_adr_exfx, c_fx, c_take, rev_yoy) |>
  pivot_longer(c(c_nights, c_adr_exfx, c_fx, c_take), names_to = "driver", values_to = "pts") |>
  mutate(driver = factor(driver, levels = c("c_nights", "c_adr_exfx", "c_fx", "c_take"),
                         labels = c("Nights", "ADR ex-FX", "FX", "Take rate / timing")),
         period = factor(period, levels = unique(period)))
tot <- dec |> group_by(period) |> summarise(rev_yoy = first(rev_yoy), top = sum(pmax(pts, 0)) / 100)
dec <- dec |> mutate(lab = case_when(driver == "Nights" ~ sprintf("%.1f", pts), driver == "FX" & pts >= 2.5 ~ sprintf("+%.1f", pts), TRUE ~ ""))
p <- ggplot(dec, aes(period, pts / 100, fill = driver)) +
  geom_col(width = 0.72, colour = INK["surface"], linewidth = 0.5) +
  geom_text(aes(label = lab), position = position_stack(vjust = 0.5), size = 3, colour = "white") +
  geom_hline(yintercept = 0, colour = INK["axis"]) +
  geom_point(data = tot, aes(period, rev_yoy), inherit.aes = FALSE, colour = INK["primary"], size = 2.2) +
  geom_text(data = tot, aes(period, top, label = percent(rev_yoy, 0.1)), inherit.aes = FALSE, vjust = -0.6, size = 3, colour = INK["primary"]) +
  scale_fill_manual(values = unname(PAL[1:4])) +
  scale_y_continuous(labels = label_percent(), expand = expansion(mult = c(0.05, 0.12))) +
  labs(title = "Revenue growth by driver, 1Q24 to 2Q26 (points of y/y growth)",
       subtitle = "Nights have added a steady 8 to 11 points since 2024; the 2026 step-up is FX. Dots and labels: reported revenue y/y",
       x = NULL, y = NULL, caption = "Source: shareholder letters via model/ABNB_historicals.xlsx; log decomposition into nights, ADR ex-FX, FX and take rate") +
  theme(legend.position = "top")
save_fig(p, "P1_revenue_growth_decomposition_2024on", 8.5, 4.6)
message("09_pitch_figures done")

# ---- P2: day-1 excess return by print, coloured by whether the next-quarter guide beat Street ----------------
e <- d$earn |> mutate(excess_1d = 100 * excess_1d, guide_vs_street = 100 * guide_vs_street,
                      verdict = case_when(is.na(guide_vs_street) ~ "No guide vs Street on record",
                                          guide_vs_street > 0 ~ "Guide above Street", TRUE ~ "Guide below Street"),
                      verdict = factor(verdict, levels = c("Guide above Street", "Guide below Street", "No guide vs Street on record")),
                      print = factor(print, levels = print))
means <- e |> filter(verdict != "No guide vs Street on record") |> group_by(verdict) |> summarise(m = mean(excess_1d), n = n())
p <- ggplot(e, aes(print, excess_1d, fill = verdict)) +
  geom_hline(yintercept = 0, colour = INK["axis"]) +
  geom_col(width = 0.72) +
  geom_text(aes(label = sprintf("%+.0f", excess_1d), vjust = if_else(excess_1d >= 0, -0.4, 1.3)), size = 2.8, colour = INK["primary"]) +
  scale_fill_manual(values = c(`Guide above Street` = PAL[["blue"]], `Guide below Street` = PAL[["orange"]], `No guide vs Street on record` = INK[["axis"]])) +
  scale_y_continuous(labels = function(x) paste0(x, "%"), expand = expansion(mult = 0.15)) +
  labs(title = "The print trades on the guide: day-1 excess return vs QQQ, all 23 prints",
       subtitle = sprintf("Guide above Street: mean %+.1f%% (n = %d). Guide below Street: mean %+.1f%% (n = %d). Wilcoxon rank-sum p = 0.02",
                          means$m[means$verdict == "Guide above Street"], means$n[means$verdict == "Guide above Street"],
                          means$m[means$verdict == "Guide below Street"], means$n[means$verdict == "Guide below Street"]),
       x = NULL, y = NULL, caption = "Source: model/ABNB_historicals.xlsx, Earnings sheet. Guide = next-quarter revenue guide midpoint vs consensus at the print (none on record before 4Q21)") +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))
save_fig(p, "P2_reaction_by_print_guide_vs_street", 8.5, 4.6)
message("P2 done")
