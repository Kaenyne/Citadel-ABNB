# run_all.R - rebuild every table and figure, then knit the report.
# From RStudio: open ABNB_stats.Rproj, then source("run_all.R").
# From a terminal:  cd analysis/r_stats && Rscript run_all.R
if (!interactive()) { a <- commandArgs(FALSE); f <- sub("^--file=", "", a[grep("^--file=", a)]); if (length(f)) setwd(dirname(normalizePath(f))) }
t0 <- Sys.time()
for (s in c("01_load", "02_descriptives", "03_growth_decomposition", "04_regressions", "05_time_series",
            "06_earnings_reaction", "07_scenarios_montecarlo", "08_event_study")) {
  message("==> ", s); source(file.path("R", paste0(s, ".R")), local = new.env())
}
pandoc <- Sys.getenv("RSTUDIO_PANDOC")
if (!nzchar(pandoc)) for (cand in c("/Applications/RStudio.app/Contents/Resources/app/quarto/bin/tools/aarch64",
                                    "/Applications/RStudio.app/Contents/Resources/app/quarto/bin/tools/x86_64")) if (file.exists(file.path(cand, "pandoc"))) { Sys.setenv(RSTUDIO_PANDOC = cand); break }
if (rmarkdown::pandoc_available()) { rmarkdown::render("ABNB_stats_report.Rmd", quiet = TRUE); message("Report: ABNB_stats_report.html") } else message("pandoc not found: open ABNB_stats_report.Rmd in RStudio and press Knit")
message(sprintf("Done in %.0f s. %d figures, %d tables.", as.numeric(difftime(Sys.time(), t0, units = "secs")),
                length(list.files("figures", "png$")), length(list.files("tables", "csv$"))))
