"""Presentation PNG/SVGs. No dependence on the output directory name."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

BG="#F7F8FA"; INK="#152C3E"; MUTED="#627485"; BLUE="#336DA5"; TEAL="#168D86"; RED="#C86449"; GOLD="#B88729"
COLORS=[BLUE,TEAL,RED,GOLD]


def setup():
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":12,"axes.titlesize":15,"axes.labelsize":12,
                         "axes.spines.top":False,"axes.spines.right":False,"axes.spines.left":False,
                         "axes.spines.bottom":False,"axes.edgecolor":"#DDE3E8","axes.labelcolor":INK,
                         "text.color":INK,"xtick.color":MUTED,"ytick.color":MUTED,
                         "figure.facecolor":BG,"axes.facecolor":BG,"grid.color":"#DDE3E8","grid.alpha":.75,
                         "svg.hashsalt":"conversion_validation_v1"})


def title(fig,headline,subtitle):
    fig.text(.06,.94,headline,fontsize=23,fontweight="bold",ha="left",va="top")
    fig.text(.06,.887,subtitle,fontsize=11.5,color=MUTED,ha="left",va="top")


def finish(fig,out,name,foot):
    fig.text(.06,.035,foot,fontsize=9.3,color=MUTED,ha="left",va="bottom")
    fig.savefig(out/(name+".png"),dpi=200,facecolor=BG)
    fig.savefig(out/(name+".svg"),facecolor=BG,metadata={"Date":None})
    plt.close(fig)


def render(out,params,profiles,fitted,uncertainty,paths,scores,paired,loyo,passes):
    setup()
    primary=params[(params["sample"]=="all22")&(params.model=="free_w")&(params.loss=="usd")].iloc[0]
    f=fitted[fitted.model=="free_w"]
    fig=plt.figure(figsize=(16,9));gs=fig.add_gridspec(1,2,left=.07,right=.95,top=.78,bottom=.16,width_ratios=[1.5,1],wspace=.24)
    ax=fig.add_subplot(gs[0]);ar=fig.add_subplot(gs[1])
    title(fig,"One shared weight. Four seasonal conversion rates.",
          "FULL-SAMPLE CALIBRATION  |  22 quarters: 2021 Q1–2026 Q2  |  USD-level least squares, no intercept")
    for season,color in zip(range(1,5),COLORS):
        g=f[f.season==season];x=g.weighted_gbv_musd/1000;y=g.actual_musd/1000
        ax.scatter(x,y,s=74,color=color,edgecolor=BG,linewidth=1.3,label=f"Q{season}  ·  n={len(g)}",zorder=3)
        xs=np.array([x.min()*.93,x.max()*1.045]);lam=primary[f"lambda_Q{season}_pct"]/100
        ax.plot(xs,lam*xs,color=color,lw=2,alpha=.85)
    ax.set(xlabel="Weighted prior-quarter GBV (USD billions)",ylabel="Revenue (USD billions)")
    ax.grid(axis="y");ax.legend(frameon=False,loc="upper left",ncol=2,fontsize=10)
    names=[f"Q{s}" for s in range(1,5)];values=[primary[f"lambda_Q{s}_pct"] for s in range(1,5)]
    ar.barh(names,values,color=COLORS,height=.52,zorder=2)
    for i,s in enumerate(range(1,5)):
        u=uncertainty[uncertainty.parameter==f"lambda_Q{s}_pct"].iloc[0]
        ar.plot([u.lower,u.upper],[i,i],color=INK,lw=1.8,zorder=3)
        ar.scatter([u.lower,u.upper],[i,i],marker="|",color=INK,s=65,zorder=3)
        ar.text(values[i]+.3,i+.22,f"{values[i]:.2f}%",fontsize=13,fontweight="bold")
    ar.set_xlim(0,20.5);ar.invert_yaxis();ar.set_xlabel("Seasonal revenue / weighted GBV (%)");ar.grid(axis="x")
    ar.set_title(f"Shared first-lag coefficient w = {primary.w:.3f}",loc="left",pad=25)
    ar.text(0,-.25,"",transform=ar.transAxes)
    finish(fig,out,"01_seasonal_conversion",
           "Descriptive fitted relationships; no forecasting claim. Thin ranges: 95% year-block resampling sensitivity (6 year blocks).\nw is a reduced-form lag coefficient, not a booking probability or actual revenue contribution share. Source: frozen Airbnb KPI panel/calendar.")

    fig=plt.figure(figsize=(16,9));gs=fig.add_gridspec(1,2,left=.07,right=.95,top=.78,bottom=.18,width_ratios=[1.4,1],wspace=.24)
    ax=fig.add_subplot(gs[0]);ay=fig.add_subplot(gs[1])
    title(fig,"The fitted lag moves when the estimation period changes.",
          "IDENTIFICATION SENSITIVITY  |  All 22 quarters remain the primary descriptive fit  |  Each profile re-fits all four seasonal rates")
    samples=[("all22","2021 Q1+ · n=22",BLUE),("exclude2021","2022 Q1+ · n=18",TEAL),("2023plus","2023 Q1+ · n=14",RED)]
    for sample,label,color in samples:
        g=profiles[(profiles["sample"]==sample)&(profiles.loss=="usd")]
        fitrow=params[(params["sample"]==sample)&(params.model=="free_w")&(params.loss=="usd")].iloc[0]
        ax.plot(g.w,100*(g.rmse_loss/g.rmse_loss.min()-1),color=color,lw=2.8,label=f"{label}; w={fitrow.w:.3f}")
        ax.scatter([fitrow.w],[0],s=70,color=color,zorder=4)
    ax.axvline(2/3,color=INK,lw=1.5,ls=(0,(4,4)),label="Fixed benchmark · w=2/3")
    ax.axhline(5,color=MUTED,lw=1,ls=":");ax.set(xlabel="Shared first-lag coefficient w",ylabel="RMSE above each sample's own minimum (%)",ylim=(-2,90),xlim=(0,1))
    ax.grid(axis="y");ax.legend(frameon=False,fontsize=10,loc="upper right")
    yl=loyo[loyo.model=="free_w"].sort_values("held_out_year")
    labels=[f"Drop {int(y)}" for y in yl.held_out_year]
    ay.scatter(yl.w,np.arange(len(yl)),s=95,color=BLUE,zorder=3)
    ay.axvline(primary.w,color=BLUE,lw=1.6,label="All-22 fit")
    ay.axvline(2/3,color=INK,lw=1.5,ls=(0,(4,4)))
    ay.set(yticks=np.arange(len(yl)),yticklabels=labels,xlim=(0,1),xlabel="Re-estimated w after excluding one year")
    ay.invert_yaxis();ay.grid(axis="x")
    for i,w in enumerate(yl.w):ay.text(w+.025,i,f"{w:.3f}",va="center",fontsize=11)
    u=uncertainty[uncertainty.parameter=="w"].iloc[0]
    ay.set_title(f"Year-block sensitivity: {u.lower:.2f}–{u.upper:.2f}",loc="left",pad=25)
    finish(fig,out,"02_weight_identification",
           "Profiles and leave-year-out fits are descriptive sensitivity, not chronological validation. Dotted 5% line is a flatness diagnostic, not a confidence interval.\nYear-block percentile range uses 1,000 draws over only six calendar years, including partial 2026; precise structural identification is unsupported.")

    fig=plt.figure(figsize=(16,9));gs=fig.add_gridspec(1,2,left=.19,right=.95,top=.775,bottom=.22,wspace=.2)
    title(fig,"Test the extra lag parameter on quarters it has not seen.",
          f"CHRONOLOGICAL GUIDE-DATE REFITS  |  Shared-weight promotion hurdle: {'PASS' if passes else 'FAIL'}  |  Existing fixed operational kernel retained")
    shown=[("free_w_usd","Free w · matched OLS",BLUE),("fixed_2_3_usd","Fixed 2/3 · matched OLS",TEAL),
           ("legacy_fixed_last3_ex2021","Existing last3 · fixed 2/3",GOLD),("harness_naive","Harness naive",MUTED),
           ("guide_cushion_postguide","Guide + cushion*",RED)]
    for j,window in enumerate(["W1","W2"]):
        ax=fig.add_subplot(gs[j]);table=scores[scores.window==window].set_index("model")
        vals=[table.loc[m,"rmse_musd"] for m,_,_ in shown]
        labels=[label for model,label,_ in shown]
        if len({int(table.loc[model,"n"]) for model,_,_ in shown}) != 1:
            raise AssertionError("presentation comparison requires matched forecast coverage")
        ax.barh(labels,vals,color=[x[2] for x in shown],height=.57)
        ax.tick_params(axis="y",labelsize=10)
        if j==1:ax.set_yticklabels([])
        for i,v in enumerate(vals):ax.text(v+2,i,f"${v:.1f}m",va="center",fontweight="bold",fontsize=12)
        ax.invert_yaxis();ax.grid(axis="x");ax.set_xlim(0,max(vals)*1.26);ax.set_xlabel("Revenue RMSE (USD millions)")
        n=int(table.iloc[0].n);ratio=table.loc["free_w_usd","ratio_to_fixed_ols"]
        u=paired[paired.window==window].iloc[0]
        ax.set_title(f"{window} · n={n}  |  Free/fixed RMSE: {ratio:.3f}×",loc="left",pad=22)
        ax.text(0,-.15,f"Paired year-block ratio range: {u.rmse_ratio_lower:.2f}–{u.rmse_ratio_upper:.2f}\n{int(u.n_year_blocks)} target-year blocks; interval is imprecise",transform=ax.transAxes,fontsize=10,color=MUTED,va="top")
    finish(fig,out,"03_chronological_validation",
           "W1: 2023 Q1–2026 Q2; W2: 2024 Q1–2026 Q2. At each origin, prior-quarter print is available; target revenue and GBV are excluded.\n*Guide + cushion uses management's already-issued target-quarter guide: an advantaged post-guide benchmark, not a guide-surprise forecast.")
