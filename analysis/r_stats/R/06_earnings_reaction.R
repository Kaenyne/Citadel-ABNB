# 06_earnings_reaction.R - what the stock does on print day, and what explains it
source("R/00_setup.R"); d <- readRDS(file.path(DATA, "abnb_tidy.rds"))
e <- d$earn |> mutate(across(c(rev_surprise, nights_surprise, gbv_surprise, ebitda_surprise, guide_vs_street, abnb_1d, qqq_1d, excess_1d, abnb_5d,
                               excess_5d, abnb_20d, excess_20d, gap_at_open, open_to_close_1d), ~ .x * 100),
                      rev_beat = rev_surprise > 0.5, guide_above = guide_vs_street > 0, up_day = excess_1d > 0)

# ---- 1. Reaction summary ---------------------------------------------------------------------------------------------------------
summ <- e |> summarise(prints = n(), mean_excess_1d = mean(excess_1d), median_excess_1d = median(excess_1d), sd_excess_1d = sd(excess_1d),
                       share_up_1d = mean(up_day), mean_abs_move_1d = mean(abs(abnb_1d)), median_abs_move_1d = median(abs(abnb_1d)),
                       share_abs_gt_7pct = mean(abs(abnb_1d) > 7), mean_excess_20d = mean(excess_20d, na.rm = TRUE),
                       share_overnight = sum(abs(gap_at_open)) / sum(abs(abnb_1d)),
                       wilcoxon_p_excess_1d = wilcox.test(excess_1d)$p.value, sign_test_p = binom.test(sum(up_day), n())$p.value,
                       t_test_p = t.test(excess_1d)$p.value)
save_tbl(summ |> pivot_longer(everything(), names_to = "statistic"), "16_reaction_summary", "Print-day reaction, 23 prints (percent; excess = vs QQQ)")

# ---- 2. Contingency tables and exact tests --------------------------------------------------------------------------------------
ct <- function(x, y, xlab, ylab) {
  dd <- e |> filter(!is.na(.data[[x]]), !is.na(.data[[y]])); tab <- table(dd[[x]], dd[[y]]); ft <- fisher.test(tab)
  tibble(row_variable = xlab, col_variable = ylab, n = nrow(dd),
         both_true = tab["TRUE","TRUE"], row_true_col_false = tab["TRUE","FALSE"], row_false_col_true = tab["FALSE","TRUE"], both_false = tab["FALSE","FALSE"],
         odds_ratio = unname(ft$estimate), fisher_p = ft$p.value,
         mean_excess_if_true = mean(dd$excess_1d[dd[[x]]]), mean_excess_if_false = mean(dd$excess_1d[!dd[[x]]]),
         wilcoxon_rank_sum_p = wilcox.test(dd$excess_1d[dd[[x]]], dd$excess_1d[!dd[[x]]])$p.value)
}
ct_tbl <- bind_rows(ct("rev_beat", "up_day", "Revenue beat (> +0.5%)", "Excess day-1 return > 0"),
                    ct("guide_above", "up_day", "Next-Q guide midpoint above Street", "Excess day-1 return > 0"))
save_tbl(ct_tbl, "17_beat_miss_contingency", "Does a beat, or a guide above Street, predict an up day? (Fisher exact and Wilcoxon rank-sum)")

# ---- 3. Univariate reaction regressions with HC3 and bootstrap CIs ---------------------------------------------------------------
set.seed(42)
feats <- c(rev_surprise = "Revenue surprise (%)", nights_surprise = "Nights surprise (%)", gbv_surprise = "GBV surprise (%)",
           ebitda_surprise = "EBITDA surprise (%)", eps_surprise = "EPS surprise (fraction)", guide_vs_street = "Next-Q guide vs Street (%)")
uni <- map_dfr(names(feats), function(f) map_dfr(c("excess_1d", "excess_5d", "excess_20d"), function(y) {
  dd <- e |> filter(!is.na(.data[[f]]), !is.na(.data[[y]])); if (nrow(dd) < 6) return(NULL)
  m <- lm(reformulate(f, y), dd); ct <- coeftest(m, vcov. = vcovHC(m, type = "HC3"))
  boot <- replicate(2000, { i <- sample(nrow(dd), replace = TRUE); coef(lm(reformulate(f, y), dd[i, ]))[2] })
  tibble(feature = feats[[f]], horizon = y, n = nrow(dd), slope = ct[2, 1], se_hc3 = ct[2, 2], p_hc3 = ct[2, 4],
         boot_lo95 = unname(quantile(boot, 0.025)), boot_hi95 = unname(quantile(boot, 0.975)), r2 = summary(m)$r.squared,
         spearman = cor(dd[[f]], dd[[y]], method = "spearman"), spearman_p = suppressWarnings(cor.test(dd[[f]], dd[[y]], method = "spearman")$p.value))
}))
save_tbl(uni, "18_reaction_univariate", "Excess return (pct) on each surprise feature: OLS slope with HC3 SE, bootstrap 95% CI, Spearman rho")

# ---- 4. Multivariate and logistic ------------------------------------------------------------------------------------------------
dd <- e |> filter(!is.na(rev_surprise), !is.na(guide_vs_street))
m_multi <- lm(excess_1d ~ rev_surprise + guide_vs_street, dd)
m_multi2 <- lm(excess_1d ~ rev_surprise + guide_vs_street + nights_surprise, dd |> filter(!is.na(nights_surprise)))
m_logit <- glm(up_day ~ rev_surprise + guide_vs_street, dd, family = binomial)
multi_tbl <- bind_rows(tidy(coeftest(m_multi, vcov. = vcovHC(m_multi, type = "HC3"))) |> mutate(model = sprintf("OLS: excess_1d ~ rev + guide (n=%d, R2=%.2f)", nobs(m_multi), summary(m_multi)$r.squared)),
                       tidy(coeftest(m_multi2, vcov. = vcovHC(m_multi2, type = "HC3"))) |> mutate(model = sprintf("OLS: + nights (n=%d, R2=%.2f)", nobs(m_multi2), summary(m_multi2)$r.squared)),
                       tidy(m_logit) |> mutate(model = sprintf("Logit: P(up day) (n=%d, McFadden R2=%.2f)", nobs(m_logit), 1 - m_logit$deviance / m_logit$null.deviance))) |>
  select(model, term, estimate, std.error, statistic, p.value)
save_tbl(multi_tbl, "19_reaction_multivariate", "Day-1 excess return on revenue surprise and guide-vs-Street together")

# ---- 5. Figures ---------------------------------------------------------------------------------------------------------------------
sc <- e |> select(print, excess_1d, rev_surprise, nights_surprise, guide_vs_street, ebitda_surprise) |>
  pivot_longer(-c(print, excess_1d), names_to = "feature") |> filter(!is.na(value)) |>
  mutate(feature = factor(feats[feature], levels = feats))
p <- ggplot(sc, aes(value, excess_1d)) + geom_hline(yintercept = 0, colour = INK["axis"]) + geom_vline(xintercept = 0, colour = INK["axis"]) +
  geom_smooth(method = "lm", formula = y ~ x, colour = PAL[["blue"]], fill = SEQ_BLUE[1], linewidth = 0.8) +
  geom_point(colour = PAL[["blue"]], size = 2.2) + geom_text(aes(label = print), size = 2.4, colour = INK["muted"], vjust = -0.8) +
  facet_wrap(~feature, scales = "free_x") +
  labs(title = "Day-1 excess return vs each surprise feature", subtitle = "Guide-vs-Street and revenue surprise carry the most signal; nights surprise almost none", x = "feature (%)", y = "excess return, day 1 (%)")
save_fig(p, "17_reaction_scatter", 10, 6)

pr <- e |> mutate(print = factor(print, levels = print), verdict = case_when(is.na(guide_vs_street) ~ "No guide vs Street", guide_above ~ "Guide above Street", TRUE ~ "Guide below Street"))
p <- ggplot(pr, aes(print, excess_1d, fill = verdict)) + geom_hline(yintercept = 0, colour = INK["axis"]) +
  geom_col(width = 0.7) + scale_fill_manual(values = c(`Guide above Street` = PAL[["blue"]], `Guide below Street` = PAL[["orange"]], `No guide vs Street` = INK[["axis"]])) +
  labs(title = "Excess return on the session after each print, by whether the next-quarter guide beat Street", x = NULL, y = "excess return, day 1 (%)") +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))
save_fig(p, "18_reaction_by_print", 10, 5)

p <- ggplot(e |> filter(!is.na(excess_20d)), aes(excess_1d, excess_20d)) + geom_hline(yintercept = 0, colour = INK["axis"]) + geom_vline(xintercept = 0, colour = INK["axis"]) +
  geom_abline(slope = 1, intercept = 0, linetype = 2, colour = INK["muted"]) +
  geom_smooth(method = "lm", formula = y ~ x, colour = PAL[["blue"]], fill = SEQ_BLUE[1], linewidth = 0.8) +
  geom_point(colour = PAL[["blue"]], size = 2.2) + geom_text(aes(label = print), size = 2.4, colour = INK["muted"], vjust = -0.8) +
  labs(title = "Does the day-1 move persist or reverse over 20 sessions?", subtitle = "Dashed: full persistence. Points below the line for positive moves = fade", x = "excess return, day 1 (%)", y = "excess return, 20 sessions (%)")
save_fig(p, "19_reaction_drift", 8, 6)
message("06_earnings_reaction done")
