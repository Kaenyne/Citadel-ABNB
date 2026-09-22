# 00_setup.R - packages, paths, palette, theme, helpers
# Working directory must be the r_stats project folder (RStudio does this via the .Rproj).
suppressPackageStartupMessages({
  library(tidyverse); library(readxl); library(broom); library(sandwich); library(lmtest)
  library(car); library(forecast); library(strucchange); library(tseries); library(gt)
  library(patchwork); library(scales); library(zoo)
})
options(dplyr.summarise.inform = FALSE, warn = 1)

PROJ <- normalizePath(getwd())
REPO <- normalizePath(file.path(PROJ, "..", ".."))
MODEL_DIR <- file.path(REPO, "model")
PROC_DIR  <- file.path(REPO, "data", "processed")
DATA <- file.path(PROJ, "data"); FIG <- file.path(PROJ, "figures"); TBL <- file.path(PROJ, "tables")
for (d in c(DATA, FIG, TBL)) dir.create(d, showWarnings = FALSE, recursive = TRUE)

SPOT <- 181.94           # close 4 Sep 2026, the model's reference price (Inputs sheet)
SPOT_DATE <- as.Date("2026-09-04")

# Palette (validated categorical order; sequential blue; diverging blue-red)
PAL <- c(blue = "#2a78d6", orange = "#eb6834", aqua = "#1baf7a", yellow = "#eda100",
         magenta = "#e87ba4", green = "#008300", violet = "#4a3aa7", red = "#e34948")
INK <- c(primary = "#0b0b0b", secondary = "#52514e", muted = "#898781", grid = "#e1e0d9",
         axis = "#c3c2b7", surface = "#fcfcfb", neutral = "#f0efec")
SEQ_BLUE <- c("#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b")

theme_abnb <- function(base_size = 11) {
  theme_minimal(base_size = base_size) +
    theme(panel.grid.minor = element_blank(), panel.grid.major.x = element_blank(),
          panel.grid.major.y = element_line(colour = INK["grid"], linewidth = 0.3),
          axis.line.x = element_line(colour = INK["axis"], linewidth = 0.3),
          axis.ticks = element_blank(), axis.text = element_text(colour = INK["muted"]),
          axis.title = element_text(colour = INK["secondary"], size = rel(0.9)),
          plot.title = element_text(face = "bold", colour = INK["primary"]),
          plot.subtitle = element_text(colour = INK["secondary"]),
          plot.caption = element_text(colour = INK["muted"], hjust = 0),
          plot.background = element_rect(fill = INK["surface"], colour = NA),
          legend.position = "top", legend.title = element_blank(),
          strip.text = element_text(colour = INK["primary"], face = "bold", hjust = 0),
          plot.title.position = "plot", plot.caption.position = "plot")
}
theme_set(theme_abnb())

save_fig <- function(p, name, w = 9, h = 5) {
  ggsave(file.path(FIG, paste0(name, ".png")), p, width = w, height = h, dpi = 150, bg = INK[["surface"]])
  invisible(p)
}
save_tbl <- function(df, name, title = NULL, digits = 3) {
  write_csv(df, file.path(TBL, paste0(name, ".csv")))
  g <- gt(df) |> fmt_number(columns = where(is.numeric), decimals = digits, drop_trailing_zeros = TRUE) |>
    tab_options(table.font.size = px(12))
  if (!is.null(title)) g <- g |> tab_header(title = title)
  gtsave(g, file.path(TBL, paste0(name, ".html")))
  invisible(df)
}
qtr_to_yq <- function(x) as.yearqtr(paste0("20", substr(x, 3, 4), " Q", substr(x, 1, 1)))
yq_to_label <- function(yq) paste0(cycle(yq), "Q", substr(format(yq, "%Y"), 3, 4))
