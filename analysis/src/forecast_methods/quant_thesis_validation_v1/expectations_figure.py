"""Scientific scenario figure; consumes completed deterministic bridge, no fitting."""
from pathlib import Path
import argparse
import csv
import json
import hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[4]
PKG=ROOT/'data/processed/forecast_methods/quant_thesis_validation_v1'

def main(out):
    if out.exists(): raise FileExistsError(out)
    src=PKG/'expectations_v2/stress_surface.csv'
    with src.open(newline='') as f: data=list(csv.DictReader(f))
    out.mkdir(parents=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(10,6.4))
    fig.subplots_adjust(left=.12,right=.97,top=.79,bottom=.26)
    fig.text(.12,.94,'The Q4 comparison changes sign with small input changes',fontsize=16,weight='bold',color='#152d44')
    fig.text(.12,.88,'Own guide versus a hypothetical Street guide, both using the same cushion',fontsize=11,color='#45566a')
    for lp,color,label in [('-0.10','#bc7444','Conversion -0.10pp'),('0','#193e5d','Retained conversion'),('0.10','#3e918e','Conversion +0.10pp')]:
        selected=sorted([r for r in data if float(r['lambda_change_pp'])==float(lp)],key=lambda r:float(r['g1_change_pct']))
        ax.plot([float(r['g1_change_pct']) for r in selected],[float(r['hypothetical_guide_gap_to_lseg_musd']) for r in selected],color=color,lw=2.4,label=label)
    ax.axhline(0,color='#4d5964',lw=1)
    ax.axvline(0,color='#bcc4cb',lw=1,ls=':')
    ax.scatter([-.8776312295],[0],color='#193e5d',s=35,zorder=3)
    ax.annotate('Equal revenue at Q3 GBV -0.88%',(-.8776312295,0),xytext=(-4.6,65),arrowprops={'arrowstyle':'-','color':'#193e5d'},fontsize=10,color='#193e5d')
    ax.set_xlabel('Change from L4 forecast Q3 GBV of $26.009bn (%)',labelpad=10)
    ax.set_ylabel('Hypothetical guide gap (USDm)',labelpad=10)
    ax.set_xlim(-5,5)
    ax.set_xticks([-5,-3,-1,0,1,3,5])
    ax.grid(axis='y',alpha=.16)
    ax.legend(loc='lower right',frameon=False,fontsize=10)
    fig.text(.12,.12,'Reference: Q4 revenue $3,179.344m; conversion 12.04037%; cushion 1.79049%.',fontsize=10,color='#45566a')
    fig.text(.12,.08,'LSEG-family revenue consensus $3,161.021m, captured 13 Sep 2026 15:20 UTC. No observed guide consensus.',fontsize=9,color='#45566a')
    fig.text(.12,.04,'One conditional Q4 reference. Deterministic stresses, not prediction intervals or probabilities. Source: expectations_v2.',fontsize=9,color='#45566a')
    fig.savefig(out/'expectations_break_even.png',dpi=180)
    fig.savefig(out/'expectations_break_even.svg')
    plt.close(fig)
    (out/'receipt.json').write_text(json.dumps({'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'n_reference':1,'plotted_curves':3,'meaning':'deterministic conditional stresses'},indent=2)+'\n')
    print(out)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=PKG/'figures_v1')
    main(p.parse_args().out)
