"""Decision figures, sourced directly from reviewed immutable result tables."""
from pathlib import Path
import argparse
import hashlib
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).resolve().parents[5]
DATA = ROOT / "data/processed/forecast_methods/gbv_decision_0915_v1"
NAVY, TEAL, ORANGE, GRAY, RED = "#203B55", "#178D9B", "#D88643", "#758494", "#B54732"
COLORS = {"joint": ORANGE, "fixed": TEAL, "guide_growth": NAVY, "revenue_growth": GRAY, "DoltHub": GRAY}
LABELS = {"joint": "Joint cohort", "fixed": "Fixed lag", "guide_growth": "Guide growth", "revenue_growth": "Revenue growth", "DoltHub": "Street proxy"}
plt.rcParams.update({"font.family": "DejaVu Sans", "text.parse_math": False, "font.size": 11, "axes.titleweight": "bold", "axes.labelcolor": NAVY,
                     "text.color": NAVY, "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
                     "axes.edgecolor": "#D5DDE3", "xtick.color": NAVY, "ytick.color": NAVY, "figure.facecolor": "#F7F9FB"})


def heading(fig, title, subtitle, foot):
    fig.text(.055, .95, title, fontsize=22, weight="bold", va="top")
    fig.text(.055, .889, subtitle, fontsize=11, va="top")
    fig.text(.055, .035, foot, fontsize=9, color="#536779", va="bottom")


def barplot(ax, names, values, title, colors=None, limit=None):
    bars = ax.bar(np.arange(len(names)), values, color=colors or [COLORS[n] for n in names], width=.6)
    ax.set_xticks(np.arange(len(names)), [LABELS.get(n, n) for n in names], fontsize=10)
    ax.set_title(title, fontsize=13, pad=22)
    ax.set_ylim(0, limit or max(values) * 1.27)
    ax.set_ylabel("RMSE (USD millions)")
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#E7EBEF")
    for b, value in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, value + ax.get_ylim()[1] * .025, f"{value:.1f}", ha="center", fontsize=12, weight="bold")


def box(ax, x, y, w, h, title, body, color=TEAL):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=.015", facecolor="white", edgecolor=color, linewidth=1.5))
    ax.text(x + .025, y + h - .04, title, va="top", fontsize=13, weight="bold", color=color)
    ax.text(x + .025, y + h - .1, body, va="top", fontsize=11, linespacing=1.5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError("Choose a new output folder")
    inputs = {"scores": DATA / "horizon_v1/results_v2/scores_common.csv", "points": DATA / "horizon_v1/results_v2/predictions.csv",
              "eligibility": DATA / "horizon_v1/eligibility_audit_v1/comparisons.csv",
              "street": DATA / "street_v1/common_v1/common_model_metrics.csv", "flights": DATA / "calendar_flights_v1/results_v1/scores.csv"}
    tables = {key: pd.read_csv(path) for key, path in inputs.items()}
    scores, points, street = tables["scores"], tables["points"], tables["street"]
    live = points[points.is_live].copy()
    figures = []

    fig = plt.figure(figsize=(13.3, 8.1))
    heading(fig, "What the joint cohort model actually does", "It estimates an aggregate booking-to-revenue bridge. It does not observe individual reservation histories.",
            "Weights shown are the current fitted predictor weights, not observed booking shares or conversion probabilities.\nSeasonal multipliers combine monetization, timing, cancellations, mix and specification error; RNPL is not separately identified.")
    ax = fig.add_axes([.055, .14, .89, .67]); ax.set_xlim(-.02, 1.02); ax.set_ylim(0, 1); ax.axis("off")
    box(ax, .01, .69, .26, .25, "Inputs we observe", "Quarterly net GBV\nQuarterly reported revenue\nPast issued guidance", TEAL)
    box(ax, .355, .69, .27, .25, "Hidden booking allocation", "Which booking quarter\nproduced each dollar of fees?\nEstimated jointly, not measured", ORANGE)
    box(ax, .715, .69, .27, .25, "Forecast we need", "Known + forecast GBV\n→ expected revenue\n÷ (1 + cushion) = guide", NAVY)
    for a, b in [(.285, .34), (.638, .70)]:
        ax.annotate("", (b, .81), (a, .81), arrowprops={"arrowstyle": "->", "color": NAVY, "lw": 2})
    ax.text(.01, .57, "Same question, two forecasting rules", fontsize=16, weight="bold")
    box(ax, .01, .17, .455, .33, "Fixed lag", "Revenue = seasonal multiplier ×\n[2/3 prior-quarter GBV + 1/3 two-quarters-ago GBV]\n\nSame-quarter predictor weight is fixed at zero.", TEAL)
    box(ax, .515, .17, .47, .33, "Joint cohort candidate", "Revenue = seasonal multiplier × weighted GBV\nSame quarter 35.90% | one prior 47.29%\nTwo prior 16.81% | older tail 0.00%\n\nWeights are fitted together using historical totals.", ORANGE)
    ax.text(.01, .035, "“Joint” means one consistent allocation supports both views: where this quarter’s revenue came from,\nand where a booking quarter’s allocated fees go. Many allocations can fit the same total revenue.", fontsize=12, linespacing=1.5)
    figures.append(("01_model_explained", fig))

    fig, axs = plt.subplots(2, 2, figsize=(13.3, 9.5))
    fig.subplots_adjust(left=.08, right=.96, top=.79, bottom=.16, wspace=.25, hspace=.73)
    heading(fig, "Accuracy depends on the target and the sample", "Raw midpoint RMSE; lower is better. Reconstructed historical forecasts, not live performance.",
            "Top/left panels: W2 common rows, targets from 2024 onward. Each horizon has its own eligible sample.\nBottom right: fixed lag versus guide growth at p+4. Its nine-row win fails when earlier eligible quarters are restored.\nAll six model–horizon promotion claims fail the broader candidate-eligibility audit; failure is not proof of uselessness.")
    for ax, h in zip(axs.flat[:3], [2, 3, 4]):
        d = scores[(scores.window == "W2") & (scores.object == "guide") & (scores.horizon_quarters == h)].set_index("model")
        names = ["joint", "fixed", "guide_growth"]
        barplot(ax, names, [d.loc[n, "rmse_musd"] for n in names], f"Guide announcement {h-1} ahead  |  n={int(d.loc['joint', 'n'])}", limit=175)
    ax = axs.flat[3]
    common = scores[(scores.window == "W1") & (scores.object == "guide") & (scores.horizon_quarters == 4)].set_index("model")
    standalone = tables["eligibility"].query("horizon_quarters == 4 and window == 'W1' and candidate == 'fixed' and reference == 'guide_growth'").iloc[0]
    vals = [common.loc["fixed", "rmse_musd"], common.loc["guide_growth", "rmse_musd"], standalone.candidate_rmse_musd, standalone.reference_rmse_musd]
    barplot(ax, ["Fixed\nn=9", "Guide growth\nn=9", "Fixed\nn=12", "Guide growth\nn=12"], vals,
            "The favorable p+4 result is sample-sensitive", [TEAL, NAVY, TEAL, NAVY], 195)
    ax.axvline(1.5, color="#C7D1D9", linestyle="--")
    figures.append(("02_guide_accuracy_and_coverage", fig))

    fig, axs = plt.subplots(1, 2, figsize=(13.3, 8.1))
    fig.subplots_adjust(left=.075, right=.96, top=.77, bottom=.28, wspace=.26)
    heading(fig, "A revenue advantage does not yet establish a guidance trade", "Same calendar origin, same ten W2 quarters, same target within each panel. Street = the held DoltHub series.",
            "W1 joint revenue RMSE is also lower: $57.4m versus $89.9m (n=11). The favorable finding is retained.\nHistorical Street snapshots have inherited provenance; the 14 used vintages remain uncertified at row level.\nThe Street guide proxy is revenue consensus divided by our cushion. It is not an observed expectation of management’s guide.")
    for ax, comp, names, title in [(axs[0], "revenue_same_object", ["joint", "fixed", "DoltHub"], "Eventual revenue forecast: joint is strongest"),
                                   (axs[1], "guide_common_cushion_proxy", ["joint", "fixed", "guide_growth", "DoltHub"], "Issued guide forecast: simple guide growth is strongest")]:
        d = street[(street.window == "W2") & (street.comparison == comp)].set_index("model")
        barplot(ax, names, [d.loc[n, "rmse_musd"] for n in names], title, limit=115)
    fig.text(.075, .165, "Live Q4 illustration: joint guide $3.185bn versus revenue consensus $3.200bn looks negative.\nAgainst the same-cushion implied guide ($3.142bn), it is +$43.6m. Those comparisons answer different questions.", fontsize=12, weight="bold", linespacing=1.6)
    figures.append(("03_street_and_guide_are_different_tests", fig))

    fig, axs = plt.subplots(1, 2, figsize=(13.3, 8.1))
    fig.subplots_adjust(left=.08, right=.96, top=.77, bottom=.29, wspace=.3)
    heading(fig, "Three future guides: a short trade can still rely on forecast inputs", "As of 15 September 2026; latest company actuals published 6 August. Q3 guidance is already issued.",
            "Points are conditional research forecasts, not promoted calls. Lines between quarters do not remove seasonality.\nKnown-GBV share measures exposure of the model’s predicted dollars to published GBV; it is not actual revenue already booked.\nThere are no calibrated next-event prediction intervals, and no quarterly Street series here for Q1/Q2 2027.")
    ax = axs[0]
    for name in ["joint", "fixed", "guide_growth"]:
        d = live[live.model == name].sort_values("target")
        ax.plot(range(3), d.guide_mid_musd / 1000, "o-", color=COLORS[name], lw=2, label=LABELS[name])
    ax.set_xticks(range(3), ["Q4 2026", "Q1 2027", "Q2 2027"])
    ax.set_ylim(2.8, 4.4); ax.grid(axis="y", color="#E7EBEF")
    ax.set_ylabel("Conditional guide midpoint (USD billions)")
    ax.set_title("The relevant forward strip", fontsize=14, pad=18)
    ax.legend(loc="upper left", frameon=False, fontsize=10)
    ax = axs[1]
    values, labels = [], []
    for target in ["2026Q4", "2027Q1", "2027Q2"]:
        for model in ["joint", "fixed"]:
            row = live[(live.target == target) & (live.model == model)].iloc[0]
            values.append(100 * row.known_gbv_dollar_share)
            labels.append(f"{target} {LABELS[model]}")
    y = np.arange(6)
    ax.barh(y, values, color=TEAL, label="Published GBV")
    ax.barh(y, 100 - np.array(values), left=values, color="#DCE3E9", label="Projected GBV")
    ax.set_yticks(y, labels, fontsize=10); ax.invert_yaxis(); ax.set_xlim(0, 105)
    ax.set_xlabel("Share of predicted revenue dollars (%)")
    ax.set_title("How much is anchored in reported GBV?", fontsize=14, pad=18)
    for i, v in enumerate(values):
        ax.text(max(v, 1) + 1, i, f"{v:.1f}% known", va="center", fontsize=10)
    ax.set_ylim(6.2, -.7); ax.legend(loc="lower center", ncol=2, frameon=False, fontsize=9)
    fig.text(.08, .16, "Booking carry is economically real. Our reported aggregate data do not measure its full size.\nIn the live fitted rules, Q1/Q2 estimates depend entirely on projected GBV inputs.", fontsize=12, weight="bold", linespacing=1.6)
    figures.append(("04_forward_strip_and_known_inputs", fig))

    fig, axs = plt.subplots(1, 2, figsize=(13.3, 8.1))
    fig.subplots_adjust(left=.08, right=.96, top=.77, bottom=.29, wspace=.28)
    heading(fig, "The most useful repair is better future-GBV information", "An unavailable perfect-input diagnostic identifies room to improve; the tested flight repair does not deliver it.",
            "Left: same W2 common samples within each horizon (n=10,10,9). Oracle uses actual future GBV and is impossible at trade time.\nRight: the preregistered calendar-flight test uses nine identical W1/W2 rows and one fitted slope; only two current-quarter features.\nError components covary; the oracle improvement is conditional potential, not an achievable guarantee or a causal decomposition.")
    ax = axs[0]
    for name, label, color in [("fixed", "Fixed lag: forecast GBV", TEAL), ("fixed_oracle", "Fixed lag: perfect future GBV", GRAY)]:
        d = scores[(scores.window == "W2") & (scores.object == "guide") & (scores.model == name)].sort_values("horizon_quarters")
        ax.plot([1, 2, 3], d.rmse_musd, "o-", label=label, color=color, lw=2.5)
        for x, v in zip([1, 2, 3], d.rmse_musd): ax.text(x, v + 4, f"{v:.1f}", ha="center", fontsize=11)
    ax.set_ylim(0, 155); ax.set_xticks([1, 2, 3], ["Next guide", "Two ahead", "Three ahead"])
    ax.set_ylabel("Guide RMSE (USD millions)"); ax.grid(axis="y", color="#E7EBEF")
    ax.set_title("Perfect GBV inputs reduce fixed-model error", fontsize=13, pad=20)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    d = tables["flights"].query("window == 'W2'").set_index("model")
    names = ["joint_noflight", "joint_flight", "fixed_noflight", "fixed_flight"]
    barplot(axs[1], ["Joint", "Joint +\nflights", "Fixed", "Fixed +\nflights"], [d.loc[n, "rmse_musd"] for n in names],
            "The specific flight remedy fails its gate", [ORANGE, "#E9B38C", TEAL, "#8BC3C9"], 110)
    fig.text(.08, .16, "Prioritize booking/stay timing, cancellation outcomes and correctly dated quarterly signals.\nMore fitted cohort weights cannot manufacture the missing information.", fontsize=12, weight="bold", linespacing=1.6)
    figures.append(("05_gap_diagnostic_and_failed_remedy", fig))

    args.out.mkdir(parents=True)
    with PdfPages(args.out / "GBV_decision_visuals.pdf") as pdf:
        for name, fig in figures:
            fig.savefig(args.out / f"{name}.png", dpi=160)
            pdf.savefig(fig)
            plt.close(fig)
    sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()
    manifest = dict(code_sha256=sha(__file__), inputs={k: dict(path=str(p.relative_to(ROOT)), sha256=sha(p)) for k, p in inputs.items()},
                    figures=[name for name, _ in figures], source_status="reviewed reconstructed research; no promotion",
                    outputs={p.name: sha(p) for p in args.out.iterdir()})
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(dict(out=str(args.out), figures=len(figures)), indent=2))


if __name__ == "__main__":
    main()
