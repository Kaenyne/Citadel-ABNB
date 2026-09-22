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
