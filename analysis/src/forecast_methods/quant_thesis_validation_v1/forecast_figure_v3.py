"""Plot matched, preregistered historical losses without reranking samples."""
from pathlib import Path
import argparse,csv,json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[4]
PKG=ROOT/'data/processed/forecast_methods/quant_thesis_validation_v1'
def main(source,out):
    if out.exists():raise FileExistsError(out)
    with source.open(newline='') as f:rows=list(csv.DictReader(f))
    rows=[r for r in rows if r['scope']=='all_three' and r['basis']=='interval']
    if len(rows)!=6:raise ValueError('Require three matched methods in both windows')
    out.mkdir(parents=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(10,6.4));fig.subplots_adjust(left=.1,right=.97,top=.77,bottom=.27)
    fig.text(.1,.94,'The early-origin forecast fails the two-benchmark hurdle',fontsize=16,weight='bold',color='#17344d')
    fig.text(.1,.88,'Guide-midpoint error at fixed dates before the target quarter and next GBV print',fontsize=11,color='#4d6272')
    for idx,(method,label,color) in enumerate([
            ('candidate_k0_gbv','Kernel + forecast GBV','#193e5d'),
            ('B1_guide_growth','Guide-growth baseline','#3e918e'),
            ('B2_revenue_naive_cushion','Revenue-growth + cushion','#a8b4bc')]):
        values=[float(next(r['rmse'] for r in rows if r['method']==method and r['window']==w)) for w in ['W1','W2']]
        bars=ax.bar([0+(idx-1)*.23,1+(idx-1)*.23],values,width=.21,label=label,color=color)
        for bar,value in zip(bars,values):ax.text(bar.get_x()+bar.get_width()/2,value+2,f'{value:.1f}',ha='center',fontsize=11)
    counts=[next(r['n'] for r in rows if r['window']==w) for w in ['W1','W2']]
    ax.set_xticks([0,1],[f'W1: 2023Q1-2026Q2\nMatched n={counts[0]}',f'W2: 2024Q1-2026Q2\nMatched n={counts[1]} (nested)'])
    ax.set_ylabel('Guide-midpoint RMSE (USDm)');ax.set_ylim(0,140);ax.grid(axis='y',alpha=.12)
    fig.legend(*ax.get_legend_handles_labels(),loc='upper left',bbox_to_anchor=(.09,.835),ncol=3,frameon=False,fontsize=9.5)
    fig.text(.1,.10,'Origin: quarter start minus 18 calendar days, rolled to prior/same US equity session close.',fontsize=9,color='#4d6272')
    fig.text(.1,.065,'Historical frozen-panel reconstruction; not archived forecasts. W1 kernel abstains in 2023Q1 and 2023Q3.',fontsize=9,color='#4d6272')
    fig.text(.1,.03,'Primary loss: distance to midpoint +/-$0.5m project convention. Raw-error verdict agrees. No confidence claim.',fontsize=9,color='#4d6272')
    fig.savefig(out/'preannouncement_forecast_test.png',dpi=180);fig.savefig(out/'preannouncement_forecast_test.svg');plt.close(fig)
    (out/'receipt.json').write_text(json.dumps({'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'matched_n':counts,'primary_loss':'interval-fair USDm RMSE','status':'failed frozen hurdle'},indent=2)+'\n')
    print(out)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=PKG/'prospective_v1/results_v1/evaluation/scores.csv');p.add_argument('--out',type=Path,default=PKG/'figures_forecast_v3')
    a=p.parse_args();main(a.source,a.out)

