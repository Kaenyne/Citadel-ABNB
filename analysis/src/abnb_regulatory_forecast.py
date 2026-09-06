"""Probability-weighted regulatory impact profile for ABNB (built 2026-09-05 with the forecast skill).

Inputs: the regulatory research package (research/regulatory/, 32 factors, catalyst calendar, illustrative
sensitivities), exposure anchors from the Inside Airbnb supply panel (city share of GBV from est_revenue_l365d),
Eurostat platform-nights country shares, and a same-day web recency pass (see the note and research log).

Each event carries: horizon probabilities (outcome by end-2027 and by end-2030), a conditional net revenue loss
distribution (triangular: low / mode / high, as % of global revenue run-rate, net of recapture on Airbnb), and a
correlation group. Losses are incremental to today's run-rate: NYC's 2023 loss and Spain's 2025 removals are
already in reported numbers and are not deducted again. A latent "European housing-politics" factor correlates
the EU events (Gaussian copula); US events share a weaker factor. Monte Carlo over 200,000 draws.

Outputs (data/processed/):
  abnb_regulatory_events.csv        the event table with probabilities, loss ranges, expected loss, sources
  abnb_regulatory_profile.csv       percentiles of total incremental loss by horizon (revenue %, EBITDA $M, $/share)
  abnb_regulatory_contributions.csv expected loss and P(any loss) per event and horizon; share of total variance
Figure: analysis/figures/abnb_regulatory_profile.png
Run: py -3.13 analysis/src/abnb_regulatory_forecast.py
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[2]
PROC = ROOT / "data/processed"
FIG = ROOT / "analysis/figures"
RNG = np.random.default_rng(20260905)
N = 200_000
# valuation translation (driver model, PR #13): FY27E base revenue $15,959M, 70% contribution margin on lost revenue
# (regulatory package assumption), 22x EV/EBITDA, 567M diluted shares
REV_BASE, CONTRIB, EV_EBITDA, SHARES = 15959.0, 0.70, 22.0, 567.0

# ------------------------------------------------------------------------------------------------ the event table
# p27 / p30: probability the loss-bearing outcome is in force by end-2027 / end-2030 (monotone).
# loss: (low, mode, high) net incremental annual revenue loss, % of global revenue, once in force.
# scale30: multiplier on the loss draw at the 2030 horizon (phase-outs ramp; 1.0 = same).
# group: correlation group. cash: one-off cash item ($M) drawn with the same event, not in run-rate loss.
EVENTS = [
    dict(id="EU-AHA", factor="REG-25", event="EU Affordable Housing Act adopted with a framework letting cities cap or restrict commercial multi-property STRs in housing-stress areas, and at least three large member states enforce under it",
         p27=0.12, p30=0.45, loss=(0.4, 1.2, 3.0), scale30=1.0, group="EU", cash=0,
         gates="proposal presented 9 Sep 2026 (0.90) x adopted by end-2027 (0.40) x enabling caps (0.70) x enforcement by 3+ states by 2027 (0.45) -> 0.11; by 2030: 0.90 x 0.75 x 0.70 x 0.95",
         base_rate="EU ordinary legislative procedure median about 18 months from proposal to adoption; STR data regulation took 17 months (Nov 2022 to Apr 2024); housing is a shared competence so the act is framed as enabling, not a ban",
         anchor="Skift 4 Sep 2026: 'not designed as a complete ban'; excludes primary residences (The Local, 5 Sep 2026)"),
    dict(id="EU-TAIL", factor="REG-25", event="Tail: the act is adopted with binding quantitative caps and enforced quickly across France, Spain, Italy, Portugal and the Netherlands (adds to EU-AHA)",
         p27=0.02, p30=0.08, loss=(2.0, 3.5, 6.0), scale30=1.0, group="EU", cash=0,
         gates="conditional on EU-AHA branch; requires Council appetite for caps against member-state competence objections",
         base_rate="no EU precedent for a binding sector cap on private lettings; fat-tailed by construction", anchor="none"),
    dict(id="ES-FINE", factor="REG-02", event="Spain's EUR64m consumer fine is upheld on the merits and paid (one-off cash; excluded from run-rate loss)",
         p27=0.55, p30=0.70, loss=(0.0, 0.0, 0.0), scale30=1.0, group="EU", cash=76,
         gates="Madrid High Court denied the stay (23 Mar 2026); EUR70m surety bond posted May 2026; merits appeal pending; possible CJEU reference on platform liability (Airbnb Ireland C-390/18 precedent favours platforms)",
         base_rate="platform-liability fines in the EU are more often reduced or annulled than paid in full at first instance; Spain's consumer authority has a mixed record on appeal", anchor="Airbnb 10-Q: loss 'neither probable nor estimable'"),
    dict(id="ES-REMOVE", factor="REG-02/03/18/21", event="A further Spanish mass removal order or platform-verified registry takes at least 25,000 more Airbnb ads offline (beyond the July 2025 cohort) with enforcement in force",
         p27=0.35, p30=0.55, loss=(0.10, 0.20, 0.45), scale30=1.2, group="EU", cash=0,
         gates="needs replacement legislation after the Supreme Court annulled RD1312/2024's single registry (May 2026); EU data-sharing regulation applies since May 2026 and lowers the cost of a redesigned registry",
         base_rate="Spain has run three enforcement waves in 24 months (removal order May 2025, fine Dec 2025, registry Jul 2025); INE tourist dwellings -10.7% y/y May 2026", anchor="Spain about 6% of global revenue (20% of EU platform nights x ~30% EU share of revenue)"),
    dict(id="ES-REGIONS", factor="REG-13/16/21", event="Regional implementations (Canary Islands Law 6/2025, Balearics enforcement, Malaga moratorium, Andalusia) remove or freeze a measurable share of Spanish supply",
         p27=0.45, p30=0.65, loss=(0.05, 0.15, 0.35), scale30=1.3, group="EU", cash=0,
         gates="Canary law enacted Dec 2025 with phased municipal implementation; Malaga moratorium to Aug 2028", base_rate="Ibiza supply almost halved in 2025 (Exceltur via Reuters); Canaries -4.6% y/y", anchor="none"),
    dict(id="BCN-2028", factor="REG-22", event="Barcelona lets at least 70% of its 10,101 tourist-apartment licences lapse in Nov 2028 and enforces removal",
         p27=0.0, p30=0.45, loss=(0.15, 0.22, 0.35), scale30=1.0, group="EU", cash=0,
         gates="Constitutional Court upheld the Catalan decree (Mar 2025); 2027 Barcelona municipal election (May 2027) could change the council; Catalan decree allows 5-year renewals at municipal discretion",
         base_rate="announced phase-outs of legal STR stock at city scale: NYC enforced as planned; Amsterdam/Paris tightened as planned; Portugal national reversed. Roughly half of announced European STR phase-outs survive in substantially original form 4+ years later", anchor="phase-2 matched cohort: 5,146 licence ids, $23.9m net loss = 0.20% of FY25 revenue"),
    dict(id="BCN-PARTIAL", factor="REG-22", event="Barcelona phase-out proceeds only partially (30% to 70% of licences) or with a grandfathering period past 2029",
         p27=0.0, p30=0.55, loss=(0.05, 0.10, 0.18), scale30=1.0, group="EU", cash=0, gates="drawn only where BCN-2028 did not occur: 0.55 x (1 - 0.45) = 0.30 effective; the remaining 25% is blocked or delayed past 2030", base_rate="as above", anchor="as above"),
    dict(id="MAUI", factor="REG-23", event="Maui Bill 9 phase-out proceeds on schedule (West Maui Jan 2029) with fewer than half of the Minatoya units exempted by hotel rezoning",
         p27=0.0, p30=0.40, loss=(0.04, 0.07, 0.12), scale30=1.0, group="US", cash=0,
         gates="lawsuits filed Dec 2025 (Kaanapali Royal owners), no injunction as of mid-2026; Planning Commission recommended against hotel rezoning (Feb 2026) so rezoning needs a 2/3 council supermajority; 2031 phase for the rest of the county falls outside the 2030 horizon",
         base_rate="US county-level STR phase-outs challenged in court: most survive but with delays (Honolulu 2022 ordinance partly enjoined then upheld)", anchor="phase-2 matched cohort: 3,862 units, $18.0m = 0.15% post-2031; West Maui portion about 35%"),
    dict(id="PARIS-PRO", factor="REG-26/08", event="Paris enacts a quota or ban on non-primary-residence (professional) tourist furnished rentals under the Nov 2024 Le Meur law powers, in force by the horizon",
         p27=0.30, p30=0.55, loss=(0.10, 0.20, 0.35), scale30=1.2, group="EU", cash=0,
         gates="Le Meur law (Nov 2024) gives municipalities quota powers; Constitutional Council validated co-ownership bans (19 Mar 2026); Council of State upheld Paris' commercial-space authorisation rule (15 Jul 2026); Paris municipal election March 2026 outcome decides appetite",
         base_rate="Paris has tightened every 2 years since 2017 (registration 2017, 120-day enforcement 2019, 90 days 2025); each step was implemented", anchor="Paris about 1.0% of global GBV (supply panel); multi-listing hosts 36% of Paris listings"),
    dict(id="PARIS-COPRO", factor="REG-08", event="Co-ownership bans and the 90-night cap keep eroding Paris occasional-host supply (attrition already legal, in force)",
         p27=0.90, p30=0.95, loss=(0.01, 0.03, 0.06), scale30=1.5, group="EU", cash=0, gates="law in force", base_rate="Inside Airbnb Paris listings -4% to -14% y/y in 2025 to 2026 while reviews flat", anchor="supply panel"),
    dict(id="GR-FREEZE", factor="REG-04/05/20", event="Greece extends the Athens and Thessaloniki registration freezes into 2027 and adds at least one more area; transfer rule erodes incumbent supply",
         p27=0.70, p30=0.80, loss=(0.02, 0.05, 0.12), scale30=1.8, group="EU", cash=0,
         gates="joint ministerial decision needed before 31 Dec 2026; none published as of mid-Aug 2026; law permits extension", base_rate="the 2025 freeze was extended once already (to 2026) and expanded (Thessaloniki, Jul 2026)", anchor="Greece 5.5% of EU platform nights, growing 15%"),
    dict(id="IE-REG", factor="REG-24", event="Ireland's register launches (Dec 2026) and planning-compliance enforcement removes more than 20% of Irish listings within 12 months",
         p27=0.35, p30=0.55, loss=(0.04, 0.07, 0.15), scale30=1.0, group="EU", cash=0,
         gates="launch 1 Dec 2026 (0.80, already delayed once from May 2026) x enforcement removes >20% (0.45)", base_rate="registration schemes with planning declarations (Scotland 2023) removed 10% to 20% of supply in year one", anchor="Ireland about 0.4% of global revenue"),
    dict(id="UK-ENG", factor="REG-27", event="England's registration scheme goes live and councils use it to remove or cap supply in at least two large tourist areas (London, Cornwall, Lake District type)",
         p27=0.20, p30=0.45, loss=(0.03, 0.08, 0.20), scale30=1.3, group="EU", cash=0,
         gates="scheme not live as of Jul 2026 after three slipped dates (2024, Apr 2026, 'later 2026'); C5 planning use class needed for caps", base_rate="UK government digital-registration launches slip a median of 12+ months", anchor="London about 0.8% of global GBV"),
    dict(id="IT-NAT", factor="REG-14", event="Italy adds national or art-city restrictions beyond CIN and the 3-property business threshold (night caps or zone bans in Rome, Venice, Milan), or Florence's transition ends with removals in May 2028",
         p27=0.30, p30=0.60, loss=(0.05, 0.12, 0.30), scale30=1.4, group="EU", cash=0,
         gates="Florence expansion enacted Jun 2026; transition ends May 2028; national 2026 budget law raised the business threshold", base_rate="Italy has added one national STR measure per year since 2023 (cedolare 26%, CIN, business threshold)", anchor="Italy 14.6% of EU platform nights; Rome 0.6% of global GBV"),
    dict(id="PT-RETIGHT", factor="REG-06/07/28", event="Portugal re-tightens nationally or Lisbon containment converts to removals of existing AL",
         p27=0.20, p30=0.35, loss=(0.04, 0.08, 0.18), scale30=1.2, group="EU", cash=0,
         gates="national policy reversed toward liberalisation (Oct 2024); referendum blocked by Constitutional Court; Lisbon containment in force Dec 2025", base_rate="one reversal already; Portugal platform nights +4.9% y/y Q1 2026 (slowest large market)", anchor="Portugal 5.2% of EU platform nights"),
    dict(id="NL-AMS", factor="REG-09", event="Amsterdam extends the 15-night cap citywide or the Netherlands adopts a national cap",
         p27=0.30, p30=0.50, loss=(0.01, 0.03, 0.06), scale30=1.2, group="EU", cash=0, gates="eight districts since Apr 2026; council evaluation due 2027", base_rate="Amsterdam tightened in 2019 (30 nights), 2021 (permits), 2026 (15 nights)", anchor="Netherlands 1.3% of EU platform nights"),
    dict(id="US-CITY", factor="REG-01 analogue", event="At least one more top-10 US Airbnb market (Los Angeles, Chicago, San Diego, Boston, Washington DC, Honolulu) enacts NYC-style platform-verified registration that removes more than 30% of its listings",
         p27=0.30, p30=0.55, loss=(0.08, 0.18, 0.40), scale30=1.3, group="US", cash=0,
         gates="Chicago suit (Jun 2026) seeks injunction; Houston platform enforcement Apr 2026; California SB 346 (Jan 2026) mandates platform data sharing; DC legislation announced", base_rate="since 2019, one large US city per ~2 years has adopted platform-verified registration (NYC 2023, Houston 2026); Clark County NV rules partly enjoined", anchor="LA 0.8%, Chicago 0.2%, San Diego 0.4% of global GBV"),
    dict(id="NYC-LOOSEN", factor="REG-01", event="NYC materially loosens Local Law 18 for owner-occupied one- and two-family homes (Int 879-2026 or successor enacted), a revenue gain",
         p27=0.20, p30=0.35, loss=(-0.25, -0.12, -0.05), scale30=1.0, group="US", cash=0,
         gates="Int 879 introduced 30 Apr 2026, six sponsors, no committee hearing as of 31 Aug 2026; 51-member council; mayoral position unknown", base_rate="NYC has not loosened LL18 in three years despite 2024 lobbying; registered hosts 3,500+ (Sep 2026)", anchor="NYC 0.35% of GBV today vs about 1% of revenue before LL18"),
    dict(id="CHI-SUIT", factor="US litigation", event="Chicago's suit against Airbnb ends in a judgment or settlement with an injunction changing platform practice or a fine above $10m",
         p27=0.40, p30=0.60, loss=(0.01, 0.03, 0.08), scale30=1.0, group="US", cash=20,
         gates="filed 23 Jun 2026 in Cook County; motion practice through 2027", base_rate="city-versus-platform enforcement suits mostly settle with compliance terms within 2 years (SF 2017, Boston 2019, NYC data-sharing 2020)", anchor="Chicago 0.2% of GBV"),
    dict(id="COMPLIANCE", factor="REG-17 and all", event="Recurring compliance, legal and mitigation spending rises (EU data-sharing, registries, Spain rural commitment $50m over 3 years); modelled as an EBITDA cost equal to this % of revenue",
         p27=0.90, p30=0.95, loss=(0.05, 0.12, 0.25), scale30=1.2, group="EU", cash=0,
         gates="EU data-sharing regulation applies since 20 May 2026", base_rate="Airbnb's 10-K legal and regulatory expense is not broken out; $50m Spain commitment is the one disclosed mitigation cost", anchor="none"),
]
GROUP_RHO = {"EU": 0.45, "US": 0.25}


def draw(N):
    ev = pd.DataFrame(EVENTS)
    z_eu, z_us = RNG.standard_normal(N), RNG.standard_normal(N)
    out = {}
    for h, pcol in (("2027", "p27"), ("2030", "p30")):
        loss_total = np.zeros(N); cash_total = np.zeros(N); per_event = {}
        for _, e in ev.iterrows():
            rho = GROUP_RHO[e.group]; zc = z_eu if e.group == "EU" else z_us
            u = _norm_cdf(np.sqrt(rho) * zc + np.sqrt(1 - rho) * RNG.standard_normal(N))  # correlated uniform
            occurs = u < e[pcol]
            lo, mo, hi = e.loss
            size = (RNG.triangular(lo, mo, hi, N) if hi > lo else np.zeros(N)) * (e.scale30 if h == "2030" else 1.0)
            # mutually exclusive Barcelona branches: partial only where full did not occur
            if e.id == "BCN-PARTIAL":
                occurs = occurs & ~per_event["BCN-2028"][0]
            contrib = np.where(occurs, size, 0.0)
            per_event[e.id] = (occurs, contrib)
            loss_total += contrib
            if e.cash:
                cash_total += np.where(occurs, e.cash, 0.0)
        out[h] = dict(loss=loss_total, cash=cash_total, per_event=per_event)
    return ev, out


def _norm_cdf(x):
    from scipy.stats import norm
    return norm.cdf(x)


def summarise(ev, out):
    pct = [5, 10, 25, 50, 75, 90, 95, 99]
    rows, contribs = [], []
    for h, d in out.items():
        loss = d["loss"]
        # split run-rate revenue loss from the compliance cost line (which is an EBITDA cost, not lost revenue)
        comp = d["per_event"]["COMPLIANCE"][1]
        rev_loss = loss - comp
        ebitda = rev_loss / 100 * REV_BASE * CONTRIB + comp / 100 * REV_BASE
        per_share = ebitda * EV_EBITDA / SHARES
        for p in pct:
            rows.append(dict(horizon=h, percentile=p, revenue_loss_pct=np.percentile(rev_loss, p), compliance_cost_pct_rev=np.percentile(comp, p),
                             total_ebitda_hit_musd=np.percentile(ebitda, p), value_per_share_usd=np.percentile(per_share, p), one_off_cash_musd=np.percentile(d["cash"], p)))
        rows.append(dict(horizon=h, percentile="mean", revenue_loss_pct=rev_loss.mean(), compliance_cost_pct_rev=comp.mean(), total_ebitda_hit_musd=ebitda.mean(), value_per_share_usd=per_share.mean(), one_off_cash_musd=d["cash"].mean()))
        rows.append(dict(horizon=h, percentile="P(revenue loss > 0.5%)", revenue_loss_pct=(rev_loss > 0.5).mean(), compliance_cost_pct_rev=None, total_ebitda_hit_musd=None, value_per_share_usd=None, one_off_cash_musd=None))
        rows.append(dict(horizon=h, percentile="P(revenue loss > 1%)", revenue_loss_pct=(rev_loss > 1.0).mean(), compliance_cost_pct_rev=None, total_ebitda_hit_musd=None, value_per_share_usd=None, one_off_cash_musd=None))
        rows.append(dict(horizon=h, percentile="P(revenue loss > 2%)", revenue_loss_pct=(rev_loss > 2.0).mean(), compliance_cost_pct_rev=None, total_ebitda_hit_musd=None, value_per_share_usd=None, one_off_cash_musd=None))
        var_total = np.var(loss)
        for eid, (occ, c) in d["per_event"].items():
            contribs.append(dict(horizon=h, id=eid, p_in_force=occ.mean(), expected_loss_pct=c.mean(), loss_if_occurs_pct=c[occ].mean() if occ.any() else 0.0,
                                 variance_share=np.cov(c, loss)[0, 1] / var_total if var_total else 0.0))
    return pd.DataFrame(rows), pd.DataFrame(contribs)


def figure(out, contribs):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for h, col in (("2027", "#4C72B0"), ("2030", "#DD8452")):
        rl = out[h]["loss"] - out[h]["per_event"]["COMPLIANCE"][1]
        axes[0].hist(np.clip(rl, -0.3, 10), bins=160, range=(-0.3, 10), density=True, alpha=0.55, color=col, label=f"end-{h} run-rate (mean {rl.mean():.2f}%, median {np.median(rl):.2f}%)")
    axes[0].set_xlabel("incremental net revenue loss, % of global revenue"); axes[0].set_ylabel("density"); axes[0].legend(frameon=False, fontsize=8); axes[0].grid(alpha=0.3)
    axes[0].set_title("Probability-weighted regulatory loss, beyond today's run-rate", loc="left", fontweight="bold", fontsize=10)
    c = contribs[(contribs.horizon == "2030") & (contribs.id != "COMPLIANCE")].sort_values("expected_loss_pct")
    axes[1].barh(c.id, c.expected_loss_pct, color="#4C72B0")
    for y, (p, e) in enumerate(zip(c.p_in_force, c.expected_loss_pct)):
        axes[1].text(max(e, 0) + 0.005, y, f"P={p:.0%}", va="center", fontsize=7)
    axes[1].set_xlabel("expected loss by end-2030, % of revenue (probability x conditional loss)"); axes[1].grid(alpha=0.3, axis="x")
    axes[1].set_title("Where the expected loss comes from", loc="left", fontweight="bold", fontsize=10)
    fig.text(0.01, 0.005, "Sources: research/regulatory factor register and catalyst calendar; Inside Airbnb and Eurostat exposure anchors; web recency pass 5 Sep 2026; Citadel-ABNB forecast (200k Monte Carlo draws)", fontsize=7, color="grey")
    fig.tight_layout(); fig.savefig(FIG / "abnb_regulatory_profile.png", dpi=150); plt.close(fig)


def main():
    ev, out = draw(N)
    prof, contribs = summarise(ev, out)
    ev2 = ev.copy()
    ev2["loss_low"], ev2["loss_mode"], ev2["loss_high"] = zip(*ev2.loss); ev2 = ev2.drop(columns=["loss"])
    for h in ("2027", "2030"):
        m = contribs[contribs.horizon == h].set_index("id")
        ev2[f"expected_loss_pct_{h}"] = ev2.id.map(m.expected_loss_pct); ev2[f"p_in_force_{h}"] = ev2.id.map(m.p_in_force)
    ev2.round(4).to_csv(PROC / "abnb_regulatory_events.csv", index=False)
    prof.round(4).to_csv(PROC / "abnb_regulatory_profile.csv", index=False)
    contribs.round(4).to_csv(PROC / "abnb_regulatory_contributions.csv", index=False)
    figure(out, contribs)
    pd.set_option("display.width", 250); pd.set_option("display.max_columns", 20); pd.set_option("display.max_colwidth", 60)
    print(prof.round(3).to_string(index=False))
    print(contribs.round(4).sort_values(["horizon", "expected_loss_pct"], ascending=[True, False]).to_string(index=False))


if __name__ == "__main__":
    sys.exit(main())
