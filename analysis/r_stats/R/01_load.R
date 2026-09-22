# 01_load.R - read the two workbooks and the model's CSV outputs into tidy frames
source("R/00_setup.R")

# ---- Historicals sheet (rows = line items, columns = quarters) -> long + wide ---------------
raw <- read_excel(file.path(MODEL_DIR, "ABNB_historicals.xlsx"), sheet = "Historicals", skip = 3,
                  col_names = TRUE, .name_repair = "minimal")
names(raw)[1:2] <- c("line", "unit")
qcols <- grep("^[1-4]Q\\d{2}$", names(raw), value = TRUE)
fycols <- grep("^FY\\d{4}$|^LTM", names(raw), value = TRUE)

hist_long <- raw |>
  select(line, unit, all_of(c(qcols, fycols))) |>
  filter(!is.na(line)) |>
  mutate(section = if_else(str_detect(line, "^[A-K]\\. "), str_sub(line, 1, 1), NA_character_)) |>
  fill(section, .direction = "down") |>
  filter(!str_detect(line, "^[A-K]\\. ")) |>
  mutate(line = str_trim(line)) |>
  pivot_longer(all_of(c(qcols, fycols)), names_to = "period", values_to = "value") |>
  mutate(value = suppressWarnings(as.numeric(value))) |>
  filter(!is.na(value))

# Map (section, label) -> tidy variable name
var_map <- tribble(
  ~section, ~line, ~var,
  "A","Nights & Seats Booked","nights", "A","Gross Booking Value","gbv", "A","ADR (GBV / nights)","adr",
  "A","Revenue","revenue", "A","Take rate (revenue / GBV)","take_rate", "A","Revenue per night","rev_per_night",
  "B","Nights y/y","nights_yoy", "B","GBV y/y","gbv_yoy", "B","ADR y/y (reported)","adr_yoy",
  "B","Revenue y/y (reported)","rev_yoy", "B","Take rate y/y change","take_rate_chg_pts", "B","Revenue per night y/y","rpn_yoy",
  "C","Revenue y/y ex-FX (letter)","rev_yoy_exfx", "C","FX effect on revenue growth (reported minus ex-FX)","fx_rev_pp",
  "C","ADR y/y ex-FX (letter)","adr_yoy_exfx", "C","FX effect on ADR growth (reported minus ex-FX)","fx_adr_pp",
  "D","from nights","c_nights", "D","from ADR (reported, incl. FX)","c_adr", "D","of which FX (letter)","c_fx",
  "D","of which ADR ex-FX (residual)","c_adr_exfx", "D","from take rate (booking-to-stay timing and fee mix)","c_take",
  "E","Nights y/y: North America","nights_yoy_na", "E","Nights y/y: EMEA","nights_yoy_emea",
  "E","Nights y/y: Latin America","nights_yoy_latam", "E","Nights y/y: Asia Pacific","nights_yoy_apac",
  "E","ADR y/y: North America","adr_yoy_na", "E","ADR y/y: EMEA","adr_yoy_emea",
  "E","Cross-border share of nights","cross_border_share", "E","Urban share of nights","urban_share",
  "E","Long-term stays (28+ nights) share","lt_share", "E","App share of nights","app_share", "E","Active listings","active_listings",
  "F","Cost of revenue","cor_gaap", "F","Operations and support","ops_gaap", "F","Product development","pd_gaap",
  "F","Sales and marketing","sm_gaap", "F","General and administrative","ga_gaap", "F","Operating income (reported)","op_income",
  "F","Interest income","interest_income", "F","Income tax provision (benefit)","tax", "F","Net income (loss)","net_income",
  "F","Diluted weighted-average shares","shares", "F","GAAP diluted EPS (net income / diluted shares)","eps_gaap",
  "G","SBC total","sbc", "G","Cost of revenue, cash","cor_cash", "G","Operations and support, cash","ops_cash",
  "G","Product development, cash","pd_cash", "G","Sales and marketing, cash","sm_cash", "G","G&A, cash","ga_cash",
  "G","S&M: brand and performance marketing","bpm_cash", "G","S&M: field operations and policy","fop_cash",
  "G","Total cash cost","cash_cost", "G","Depreciation and amortisation","da", "G","Adjusted EBITDA (reported)","adj_ebitda",
  "G","Free cash flow (letter)","fcf",
  "H","Adjusted EBITDA margin","ebitda_margin", "H","GAAP operating margin","op_margin", "H","Net margin","net_margin",
  "H","FCF margin","fcf_margin", "H","SBC % revenue","sbc_pct", "H","Cost of revenue (cash)","cor_pct",
  "H","Operations and support (cash)","ops_pct", "H","Product development (cash)","pd_pct", "H","Sales and marketing (cash)","sm_pct",
  "H","G&A (cash)","ga_pct", "H","Brand and performance marketing","bpm_pct", "H","Cost of revenue (cash) per $100 of GBV","cor_per_100gbv",
  "I","Change in Adjusted EBITDA margin y/y","d_margin_pts", "I","Cost of revenue (lower ratio = positive)","d_cor_pts",
  "I","Operations and support (lower ratio = positive)","d_ops_pts", "I","Product development (lower ratio = positive)","d_pd_pts",
  "I","Sales and marketing (lower ratio = positive)","d_sm_pts", "I","G&A (lower ratio = positive)","d_ga_pts", "I","D&A and add-backs","d_da_pts",
  "J","Cash cost per night, total","cost_per_night", "J","Cost of revenue per night","cor_per_night",
  "J","Operations and support per night","ops_per_night", "J","Product development per night","pd_per_night",
  "J","Sales and marketing per night","sm_per_night", "J","G&A per night","ga_per_night",
  "J","Total unit-cost effect (all lines)","unit_cost_effect_pts", "J","Total revenue-per-night effect (all lines)","rpn_effect_pts",
  "K","Cash from operations","cfo", "K","Capex","capex", "K","Share repurchases","buybacks",
  "K","RSU tax withholding (net share settlement)","rsu_withholding", "K","Unearned fees (quarter end)","unearned_fees",
  "K","Funds held for clients (quarter end)","funds_held"
)
missing <- anti_join(var_map, distinct(hist_long, section, line), by = c("section","line"))
if (nrow(missing)) warning("Unmatched labels: ", paste(missing$line, collapse = "; "))

q <- hist_long |>
  inner_join(var_map, by = c("section","line")) |>
  filter(period %in% qcols) |>
  select(period, var, value) |>
  pivot_wider(names_from = var, values_from = value) |>
  mutate(yq = qtr_to_yq(period), year = as.integer(format(yq, "%Y")), qtr = cycle(yq),
         date = as.Date(yq, frac = 1)) |>
  arrange(yq) |>
  mutate(t = row_number())
fy <- hist_long |> inner_join(var_map, by = c("section","line")) |> filter(period %in% fycols) |>
  select(period, var, value) |> pivot_wider(names_from = var, values_from = value)

# ---- Earnings sheet: 23 prints, consensus, guidance, reaction -----------------------------
earn <- read_excel(file.path(MODEL_DIR, "ABNB_historicals.xlsx"), sheet = "Earnings", skip = 3, n_max = 23,
                   .name_repair = "minimal")
earn <- earn[, names(earn) != ""]
names(earn) <- names(earn) |> str_to_lower() |> str_replace_all("[^a-z0-9]+", "_") |> str_remove("_$")
earn <- earn |>
  mutate(across(c(print_date, reaction_date), as.Date),
         across(c(rev_guide_low, rev_guide_high, rev_actual, vs_guide_mid, vs_guide_top, rev_consensus, rev_surprise,
                  nights_cons_m, nights_actual, nights_surprise, gbv_cons_b, gbv_actual, gbv_surprise, adr_cons, adr_actual,
                  adr_surprise, ebitda_cons, ebitda_actual, ebitda_surprise, margin_actual, eps_cons, eps_actual, eps_surprise,
                  next_q_rev_consensus, next_q_guide_mid, guide_vs_street, abnb_1d, qqq_1d, excess_1d, abnb_5d, excess_5d,
                  abnb_20d, excess_20d, gap_at_open, open_to_close_1d, open_entry_5d, open_entry_20d),
                ~ suppressWarnings(as.numeric(.x)))) |>
  mutate(yq = qtr_to_yq(print))

# ---- Driver model: History sheet (cross-check) and Street sheet ---------------------------
drv_hist <- read_excel(file.path(MODEL_DIR, "ABNB_driver_model.xlsx"), sheet = "History", skip = 3,
                       .name_repair = "minimal") |>
  filter(str_detect(Quarter, "^[1-4]Q\\d{2}$")) |>
  mutate(across(-Quarter, ~ suppressWarnings(as.numeric(.x))))
street <- read_excel(file.path(MODEL_DIR, "ABNB_driver_model.xlsx"), sheet = "Street", skip = 3, .name_repair = "minimal")
names(street) <- c("line","street","n_range","our_base","delta","delta_pct","vendor")[seq_len(ncol(street))]
street <- street |> filter(!is.na(line), !is.na(street)) |> mutate(street = suppressWarnings(as.numeric(street)))

# ---- Model outputs (overnight workstream 13) and price data --------------------------------
model_q <- read_csv(file.path(PROC_DIR, "overnight", "13_model_quarterly.csv"), show_col_types = FALSE)
model_a <- read_csv(file.path(PROC_DIR, "overnight", "13_model_annual.csv"), show_col_types = FALSE)
grid    <- read_csv(file.path(PROC_DIR, "overnight", "13_scenario_grid.csv"), show_col_types = FALSE)
val     <- read_csv(file.path(PROC_DIR, "overnight", "13_valuation_summary.csv"), show_col_types = FALSE)
px      <- read_csv(file.path(PROC_DIR, "abnb_daily_close.csv"), show_col_types = FALSE) |>
  rename(date = Date, close = Close) |> arrange(date) |> mutate(ret = c(NA, diff(log(close))))
react   <- read_csv(file.path(PROC_DIR, "abnb_earnings_reactions.csv"), show_col_types = FALSE) |>
  mutate(reaction_date = as.Date(reaction_date))

# ---- Save tidy copies for RStudio use --------------------------------------------------------
write_csv(q, file.path(DATA, "abnb_quarterly.csv"))
write_csv(earn, file.path(DATA, "abnb_earnings_prints.csv"))
write_csv(hist_long, file.path(DATA, "abnb_historicals_long.csv"))
saveRDS(list(q = q, fy = fy, earn = earn, drv_hist = drv_hist, street = street, model_q = model_q,
             model_a = model_a, grid = grid, val = val, px = px, react = react, hist_long = hist_long),
        file.path(DATA, "abnb_tidy.rds"))
message("Loaded: ", nrow(q), " quarters (", q$period[1], " to ", q$period[nrow(q)], "), ",
        nrow(earn), " earnings prints, ", nrow(px), " daily closes")
