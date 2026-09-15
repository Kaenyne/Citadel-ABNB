"""Build a two-page, source-bound GBV/guidance research memo. No research refits."""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[5]
DATA = ROOT / 'data/processed/forecast_methods/gbv_event_v1'
INPUTS = {
    'model': DATA / 'integration_v2/model.json',
    'events': DATA / 'events_v1/run_v3/event_panel.csv',
    'associations': DATA / 'events_v1/run_v3/associations.csv',
    'event_receipt': DATA / 'events_v1/run_v3/receipt.json',
    'forecast_audit': DATA / 'forecast_v1/results_v1/forecast_audit.json',
    'scores': DATA / 'forecast_v1/results_v1/score_summary.csv',
    'variance': DATA / 'forecast_v1/results_v1/variance_reconciliation.csv',
    'independent_review': DATA / 'sources_v1/review_v2/receipt.json',
    'source_note': ROOT / 'docs/revenue-forecast-strategy/05_backtests/GE_SOURCE_RESULTS_v2.md',
}
NAVY, TEAL, AMBER = map(HexColor, ['#162C42', '#087F82', '#C77B35'])
GRAY, GRID, PALE = map(HexColor, ['#536573', '#DAE2E8', '#F1F5F7'])
W, H, M = 612, 792, 38
WIDTH = W - 2*M


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


class Memo:
    def __init__(self, path):
        self.c = canvas.Canvas(str(path), pagesize=(W,H), invariant=1)
        self.c.setTitle('Airbnb | The guide, the gap, and the evidence')
        self.c.setAuthor('Citadel ABNB research | GBV event validation')
        self.bounds=[]

    def txt(self, x, top, text, size=9, color=NAVY, bold=False, align='left'):
        self.c.setFillColor(color)
        self.c.setFont('Arial-Bold' if bold else 'Arial', size)
        fn = self.c.drawRightString if align=='right' else self.c.drawCentredString if align=='center' else self.c.drawString
        fn(x,H-top-size,text)

    def para(self, x, top, width, text, size=9.2, color=NAVY, leading=None, maxheight=None):
        style=ParagraphStyle('p', fontName='Arial', fontSize=size, leading=leading or size*1.32,
                             textColor=color, spaceAfter=0)
        p=Paragraph(text,style)
        _,height=p.wrap(width, H)
        if maxheight is not None and height>maxheight+0.1:
            raise ValueError(f'Paragraph overflow at {top}: {height}>{maxheight}: {text[:70]}')
        if top+height>751:
            raise ValueError(f'Page overflow: {top+height}')
        p.drawOn(self.c,x,H-top-height)
        self.bounds.append(dict(page=self.c.getPageNumber(),top=top,bottom=top+height,text=text))
        return height

    def line(self,x1,t1,x2,t2,color=GRID,width=.6):
        self.c.setStrokeColor(color);self.c.setLineWidth(width)
        self.c.line(x1,H-t1,x2,H-t2)

    def rect(self,x,top,w,h,color):
        self.c.setFillColor(color);self.c.rect(x,H-top-h,w,h,fill=1,stroke=0)

    def header(self,n,label):
        self.txt(M,25,'ABNB  /  GUIDANCE RESEARCH',8,TEAL,True)
        self.txt(W-M,25,'15 SEP 2026  |  Q3 2026 - Q2 2027',8,GRAY,align='right')
        self.line(M,43,W-M,43)
        self.txt(M,757,label,7.4,GRAY)
        self.txt(W-M,757,f'{n} / 2',7.4,GRAY,align='right')

    def dot(self,x,top,r,color):
        self.c.setFillColor(color);self.c.circle(x,H-top,r,fill=1,stroke=0)


def build(out):
    if out.exists():
        raise FileExistsError(f'Choose a new output directory: {out}')
    out.mkdir(parents=True)
    pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold','C:/Windows/Fonts/arialbd.ttf'))
    model=json.loads(INPUTS['model'].read_text())
    audit=json.loads(INPUTS['forecast_audit'].read_text())
    events=rows(INPUTS['events']);associations=rows(INPUTS['associations'])
    review=json.loads(INPUTS['independent_review'].read_text())
    f=model['forecast']; q4=f[1]; chosen=model['selected_comparisons'][1]
    assert len(f)==4 and [x['quarter'] for x in f]==['2026Q3','2026Q4','2027Q1','2027Q2']
    assert len(events)==23 and audit['forecast_verdict']=='FAIL'
    primary=[r for r in associations if r['primary_family']=='True']
    assert len(primary)==12 and all(float(r['holm_12_primary_p'])==1 for r in primary)
    assert review['checks']==review['passed']==314
    c=q4['cushion_decimal']
    q4_boundary=(chosen['consensus_revenue_musd']/q4['lambda_decimal']-q4['lag2_gbv_musd']/3)*1.5
    lambda_boundary=chosen['break_even_conversion_given_our_gbv']*100
    pdf=out/'ABNB_GBV_two_pager.pdf'
    p=Memo(pdf)
    p.header(1,'Conditional operating model | independently checked arithmetic; method not promoted')
    p.txt(M,55,'The guide, the gap, and the evidence',22,NAVY,True)
    p.para(M,87,WIDTH,'Four-quarter GBV conversion gives an auditable guidance path. The current evidence supports scenario analysis; it does not establish a short or predict a share-price move.',10.4,GRAY,maxheight=32)
    p.rect(M,128,WIDTH,59,PALE)
    p.txt(M+12,138,'Q4 IMPLIED GUIDE',8,TEAL,True)
    p.txt(M+12,153,f"${q4['implied_guide_musd']:,.1f}m",19,NAVY,True)
    p.para(M+183,139,WIDTH-195,f"<b>+${chosen['implied_guide_gap_musd']:.0f}m / +{chosen['revenue_gap_pct']:.2f}%</b> versus a like-for-like Yahoo/LSEG implied-guide proxy. A lower guide than Street <i>revenue</i> is not itself a bearish surprise. [1, 2]",9.6,maxheight=43)

    p.txt(M,201,'01  |  Translate booked value into the first guide',11,NAVY,True)
    xs=[M,M+57,M+156,M+223,M+309,M+395,W-M]
    headers=['Target','Weighted GBV','Conversion','Revenue','Implied guide','Guide status']
    p.rect(M,221,WIDTH,24,NAVY)
    for i,h in enumerate(headers):p.txt(xs[i]+7,228,h,8,white,True)
    for j,r in enumerate(f):
        t=245+j*25
        if j%2==0:p.rect(M,t,WIDTH,25,PALE)
        values=[r['quarter'],f"{r['weighted_gbv_musd']:,.1f}",f"{100*r['lambda_decimal']:.3f}%",f"{r['revenue_musd']:,.1f}",f"{r['implied_guide_musd']:,.1f}",'Issued: diagnostic' if j==0 else 'Conditional']
        for i,v in enumerate(values):p.txt(xs[i]+7,t+7,v,8.7,TEAL if i==4 else NAVY,i==4)
    p.para(M,354,WIDTH,'USD millions. Q3\'26 actual issued guide: <b>$4,690-4,770m; midpoint $4,730m</b> [1]. Its modeled guide is a diagnostic, not an unknown forecast. Quarterly Q1/Q2\'27 Street revenue and all direct guide-expectation panels are unavailable in the reviewed register.',8.6,GRAY,maxheight=35)
    p.para(M,395,WIDTH,'<b>R = conversion x (2/3 x prior-quarter GBV + 1/3 x two-quarter-prior GBV); G = R / (1 + cushion).</b> Conversion is same-season EWM, two-year half-life; cutoff 13 Sep, n=5/5/6/6. Cushion is the prior eight observations\' median, 1.7905%. Q3/Q4 GBV assumptions were component-derived; Q1\'27 GBV is inherited and unvalidated. No second RNPL haircut. [2]',8.6,maxheight=48)

    # Figure 1: absolute guide proxies plotted on a cropped numeric axis, with explicit scale.
    lx,rx=M,M+278
    p.txt(lx,457,'Q4 comparison changes with the panel',9.8,NAVY,True)
    p.txt(lx,474,'USDm; each Street revenue / same 1.017905',7.6,GRAY)
    left, right=lx+104,lx+252
    def gx(v):return left+(v-3090)/(3160-3090)*(right-left)
    entries=[('Our scenario',q4['implied_guide_musd'],TEAL),('Yahoo/LSEG',chosen['implied_street_guide_musd'],NAVY),('S&P',3160/(1+c),GRAY),('Zacks',3200/(1+c),AMBER)]
    for k,(name,val,color) in enumerate(entries):
        y=501+k*19
        p.txt(lx,y-5,name,8.1,color,k==0)
        p.line(left,y,right,y,GRID,.5);p.dot(gx(val),y,3,color)
        p.txt(right+3,y-5,f'{val:,.1f}',7.5,color)
    for tick in (3100,3120,3140):p.txt(gx(tick),580,str(tick),7,GRAY,align='center')
    p.para(lx,596,258,'Yahoo 13 Sep: revenue $3,161.0m, n=36; S&P 10 Sep: $3,160m; Zacks 11 Sep: $3,200m. DoltHub mirrors Zacks; Yahoo/Alpha Vantage share the LSEG family. The sign is panel-sensitive. [2]',7.9,GRAY,maxheight=44)

    # Figure 2: matched interval-score bars only; oracle remains prose to avoid mixed scoring.
    p.txt(rx,457,'Guide test fails the promotion hurdle',9.8,NAVY,True)
    p.txt(rx,474,'RMSE, USDm; matched first-issued-guide targets',7.6,GRAY)
    bx,by,bw,bh=rx+27,573,221,78
    for tick in (0,40,80):
        yy=by-tick/90*bh;p.line(bx,yy,bx+bw,yy);p.txt(bx-5,yy-4,str(tick),7,GRAY,align='right')
    for j,(window,n) in enumerate([('W1',12),('W2',10)]):
        vals=[]
        for method in ('candidate_k0_gbv','B1_guide_growth'):
            vals.append(next(r['rmse'] for r in audit['matched_scores'] if r['window']==window and r['method']==method and r['basis']=='interval'))
        for k,(val,color) in enumerate(zip(vals,(TEAL,GRAY))):
            x=bx+25+j*106+k*28;p.rect(x,by-val/90*bh,22,val/90*bh,color);p.txt(x+11,by-val/90*bh-13,f'{val:.1f}',7.7,color,True,'center')
        p.txt(bx+53+j*106,580,f'{window}  n={n}',7.6,GRAY,align='center')
    p.dot(rx+4,606,3,TEAL);p.txt(rx+12,601,'GBV candidate',8)
    p.dot(rx+117,606,3,GRAY);p.txt(rx+125,601,'Guide-growth B1',8)
    p.para(rx,619,258,'W1: 2023Q1-2026Q2; W2: 2024Q1-2026Q2, nested. Midpoint +/-$0.5m convention; raw RMSE $63.9m/$64.1m. Audit candidate uses ex-COVID conversion: different variant/origin from this EWM path. [3]',7.8,GRAY,maxheight=34)

    p.para(M,662,WIDTH,'<b>Errors move together.</b> W2 Shapley component variances sum to 7,759.7; covariance contributes -3,662.7, leaving total variance 4,097.0 (USDm squared). Raw ex-post actual-GBV oracle RMSE is $36.4m/$38.7m (W1/W2); it is unavailable before release. Attribution is accounting, not causality. [3]',8.35,maxheight=37)
    p.rect(M,709,WIDTH,38,PALE)
    p.para(M+10,716,WIDTH-20,f'<b>Short boundary, not a trade trigger:</b> fixing the chosen panel and other inputs, Q4 conversion below {lambda_boundary:.3f}% (base 12.040%) or Q3 GBV below ${q4_boundary:,.1f}m (base $26,008.6m) puts our guide below the proxy. A trade still needs robust expectations, uncertainty and executable returns.',8.15,leading=10,maxheight=31)
    p.c.showPage()

    p.header(2,'Daily event evidence | no true call bars, fitted price target, or established trading edge')
    p.txt(M,55,'The overnight leg is not the call leg',22,NAVY,True)
    p.para(M,88,WIDTH,'Large earnings moves are real, but daily OHLC cannot reveal their intraday order or cause. All 23 ledger events are shown, including events with missing usable consensus; no large-move subsample is selected. [4]',10.1,GRAY,maxheight=40)
    p.txt(M,140,'02  |  Earnings price legs across the full held event history',11,NAVY,True)
    p.txt(M,159,'ABNB less QQQ simple return, percentage points',8,GRAY)
    p.dot(M+315,164,3,TEAL);p.txt(M+323,159,'Preclose to next open',7.6)
    p.dot(M+441,164,3,AMBER);p.txt(M+449,159,'Open to close',7.6)
    x0,x1,t0,t1=M+25,W-M,186,327
    ymin,ymax=-20,20
    def ey(v):return t1-(v-ymin)/(ymax-ymin)*(t1-t0)
    for tick in (-20,-10,0,10,20):
        y=ey(tick);p.line(x0,y,x1,y,GRAY if tick==0 else GRID,.8 if tick==0 else .5)
        p.txt(x0-5,y-4,f'{tick:+d}' if tick else '0',7,GRAY,align='right')
    step=(x1-x0)/len(events)
    for j,r in enumerate(events):
        x=x0+step*(j+.5)
        for k,(field,color) in enumerate([('gap_excess_pct',TEAL),('session_excess_pct',AMBER)]):
            val=float(r[field]);assert ymin<=val<=ymax
            z=ey(0);top=min(z,ey(val));p.rect(x-6+k*6,top,5.5,abs(ey(val)-z),color)
        p.c.saveState();p.c.translate(x+2,H-337);p.c.rotate(60);p.c.setFont('Arial',6.8);p.c.setFillColor(GRAY);p.c.drawRightString(0,0,r['print_quarter'][2:]);p.c.restoreState()
    p.txt(W-M,372,'Labels identify the reported quarter, not the forward guide target.',7.5,GRAY,align='right')
    p.para(M,390,WIDTH,'<b>23 events; 20 numeric first guides; 16 usable original revenue-consensus comparisons; 15 with a prior-data cushion.</b> Across 12 primary tests (two expectation proxies x two daily legs x all/W1/W2 print windows), every Holm-adjusted p-value is 1.00. This neither proves zero effect nor establishes a tradeable guide-surprise rule. W1/W2 event proxy n=13/9. [4]',8.7,maxheight=46)

    p.txt(M,451,'03  |  Three entries require three different information sets',11,NAVY,True)
    cardw=(WIDTH-20)/3
    cards=[('BEFORE THE RELEASE','Use only the frozen early-origin prediction and contemporaneous expectations. Bear the entire origin-to-event return. Reconstruction is not an archived live signal.'),
           ('AT THE NEXT OPEN','The guide and call are public; the overnight gap is already gone. Test only returns available after entry, with costs and a rule fixed before evaluation.'),
           ('DURING THE CALL','Requires timestamped bars and exact publication, call start/end clocks. Held daily data cannot certify fills, wick order, stop execution or a call-only move.')]
    for j,(title,body) in enumerate(cards):
        x=M+j*(cardw+10);p.rect(x,476,cardw,99,PALE);p.txt(x+9,486,title,8,TEAL,True);p.para(x+9,503,cardw-18,body,8.3,maxheight=65)

    p.para(M,590,258,'<b>What would strengthen a short?</b> A dated, direct guide-expectation panel; a GBV or conversion downside that survives credible vendor/cushion choices; and a preregistered, net-of-cost entry test. RNPL cancellation/timing risk needs matched evidence before a numerical haircut.',8.5,maxheight=64)
    p.para(M+278,590,258,'<b>What would falsify it?</b> Net realized growth and conversion holding up through rollout laps; a guide consistent with the market\'s actual expectations; or a negative guide surprise that fails to predict returns available after the chosen entry. The present $18m Q4 gap is not a calibrated probability.',8.5,maxheight=64)

    p.para(M,661,WIDTH,'<b>Immediate work:</b> refresh the named expectation panel at the decision time; validate the conditional future GBV inputs; obtain ABNB+QQQ timestamped intraday history only if a call-entry trade is pursued. November 5 is a project expected date, not an official future schedule verified here. Daily gaps include the release, call, overnight and premarket.',8.25,maxheight=37)
    p.line(M,707,W-M,707)
    p.para(M,714,WIDTH,'<b>Sources / version trail.</b> [1] <link href="https://www.sec.gov/Archives/edgar/data/1559720/000119312526337928/d70413dex991.htm" color="#087F82">SEC Q2 2026 shareholder letter</link>, 6 Aug (Q3 guide; scheduled 17:00 NY call). [2] integration_v2/model.json; GE_SOURCE_RESULTS_v2.md; dated L0 Yahoo/LSEG 13 Sep 15:20:58Z, S&amp;P 10 Sep, Zacks 11 Sep. [3] forecast_v1/results_v1 (matched scores, Shapley covariance, oracle); GE frozen protocol. [4] events_v1/run_v3; 2,895 held ticker-days, 115 return tieouts; sources_v1/review_v2: 314 checks. Exact hashes and editable prose accompany this memo.',7.15,GRAY,leading=9.1,maxheight=37)
    p.c.save()
    extracted=PdfReader(pdf)
    assert len(extracted.pages)==2
    text='\n\n'.join(page.extract_text() for page in extracted.pages)
    assert '3,123.4' in text and '3,977.2' in text and '1.00' in text
    assert '\u25a0' not in text
    (out/'extracted_text.txt').write_text(text,encoding='utf-8')
    (out/'layout_bounds.json').write_text(json.dumps(p.bounds,indent=2),encoding='utf-8')

    # Human-editable memo preserves richer source links and definitions than the compressed print layout.
    md=f'''# Airbnb: the guide, the gap, and the evidence

Prepared 15 September 2026. Scope: Q3 2026 through Q2 2027. Conditional operating scenario, not a promoted forecasting or trading strategy.

The four-quarter model turns lagged GBV into revenue and then a first-guide estimate. Its Q4 implied guide is ${q4['implied_guide_musd']:,.1f}m, compared with ${chosen['implied_street_guide_musd']:,.1f}m when dated Yahoo/LSEG revenue expectations receive the same cushion: +${chosen['implied_guide_gap_musd']:.1f}m, +{chosen['revenue_gap_pct']:.2f}%. Comparing our guide directly with eventual-revenue consensus would compare different objects. Applying the same cushion makes the revenue and guide gap percentages identical by construction.

| Target | Weighted GBV ($m) | Conversion | Revenue ($m) | Implied guide ($m) | Status |
|---|---:|---:|---:|---:|---|
'''
    for r in f:
        md+=f"| {r['quarter']} | {r['weighted_gbv_musd']:,.1f} | {100*r['lambda_decimal']:.3f}% | {r['revenue_musd']:,.1f} | {r['implied_guide_musd']:,.1f} | {'Already-issued diagnostic' if r['quarter']=='2026Q3' else 'Conditional future guide'} |\n"
    md+=f'''
The Q3 guide is already observed: $4,690-4,770m, midpoint $4,730m, in the [6 August SEC letter](https://www.sec.gov/Archives/edgar/data/1559720/000119312526337928/d70413dex991.htm). The Q3 model comparison is not an earlier forecast of that announcement. No quarterly Q1/Q2 2027 Street revenue or directly observed guide-expectation panel is available in the reviewed register.

## Model and source boundaries

Revenue = season-specific conversion x (2/3 x prior-quarter GBV + 1/3 x two-quarter-prior GBV). Implied guide = revenue / (1 + cushion). Same-season EWM conversion has a two-year half-life and a 13 September cutoff, n=5/5/6/6. The common cushion is the median of eight prior observations, {100*c:.4f}%. Q3/Q4 GBV working inputs were originally component-derived and carry shared-input uncertainty; Q1 2027 GBV is an inherited, unvalidated assumption. Q2 2027 now uses explicit lagged-GBV conversion. There is no second RNPL haircut or extra FX/fee overlay. Precise-filed-GBV substitution is a separate sensitivity, not a silent rebasing.

Yahoo/LSEG revenue expectations were captured 13 September at 15:20:58Z: Q3 $4,744.88187m and Q4 $3,161.02149m, n=36 each. S&P Q4 $3,160m is dated 10 September; Zacks $3,200m is dated 11 September. DoltHub mirrors Zacks, while Yahoo/Alpha Vantage are channels of the same LSEG family; channels are not independent panels. With a common cushion, S&P and Zacks imply Q4 guide proxies of ${3160/(1+c):,.1f}m and ${3200/(1+c):,.1f}m. The sign versus our forecast changes with the panel. These are dated snapshots, not September 15 live refreshes.

Holding the chosen Yahoo/LSEG panel and other inputs fixed, Q4 conversion below {lambda_boundary:.6f}% (base {q4['lambda_decimal']*100:.6f}%) or Q3 GBV below ${q4_boundary:,.6f}m (base $26,008.556m) puts our guide below the common-cushion proxy. These are algebraic zero-gap boundaries, not calibrated entry thresholds. Consensus revenue divided by our weighted GBV is a break-even conversion conditional on our GBV, not an observed Street conversion forecast.

## Forecast validation and uncertainty

The frozen candidate fails the promotion hurdle. Matched guide-target W1 is 2023Q1-2026Q2, n=12; W2 is 2024Q1-2026Q2, n=10 and nested. The earlier origin is target-quarter start minus 18 calendar days, aligned to the preceding eligible QQQ session. Candidate interval RMSE is $63.4m/$63.7m versus guide-growth B1 $74.3m/$60.8m. Raw candidate RMSE is $63.9m/$64.1m. The audit candidate uses the ex-COVID conversion variant, while the current four-quarter scenario uses inherited same-season EWM: the historical error figures do not directly validate this different variant and horizon. The midpoint +/-$0.5m convention is administrative, not the source endpoint interval or the full guide range. Frozen-panel reconstruction is not an archived live forecast; these are repeated earlier-origin first-guide tests, not empirical validation of a four-quarter path.

Shapley assigns interaction effects symmetrically among GBV, conversion and cushion. It does not identify causes. In W2, diagonal population variances sum to 7,759.7 and covariance contributes -3,662.7, leaving 4,097.0 (USDm squared). Do not assume components independent or add their RMSEs. With actual GBV substituted ex post while retaining early-origin conversion/cushion, raw guide RMSE falls to $36.4m/$38.7m. This oracle is unavailable before release and does not establish a trade. The $18m Q4 proxy gap is not a calibrated probability or a share-price target.

## Daily earnings legs and entry choices

All 23 held ledger events are displayed, reported quarters 2020Q4-2026Q2. Twenty have numeric first guides; 16 have admissible original pre-guide revenue consensus, and 15 also have a strictly prior-data cushion. W1/W2 event print windows begin 2023Q1/2024Q1, with proxy n=13/9, distinct from forecast target windows. Twelve primary tests cover two expectation proxies, two daily legs and three windows; all Holm-adjusted p-values are 1.00. This does not prove no effect; it supplies no established guide-surprise trading edge. Published-guide association is a post-release diagnostic.

The full held daily source contains 2,895 ticker-days (ABNB 1,444; QQQ 1,451), with 115 event-return tieouts. Preclose-to-nextopen includes release, call, overnight and premarket. Nextopen-to-close is the regular session. Simple returns compound within each security before subtracting QQQ; excess gap and excess session cannot themselves be compounded. Daily OHLC gives neither true call bars nor wick order, fills or stop execution. No held timestamped ABNB/QQQ intraday panel was found.

- Before release: use only the frozen early-origin forecast and contemporaneous expectations, bearing all intervening price risk. Reconstructed signal association is not archived strategy performance.
- At next open: the guide and call are public; the gap is no longer available to a new position. Evaluate only subsequent returns under an ex-ante rule and costs.
- During call: require consistently sourced timestamped ABNB and QQQ bars, exact publication/call-start/call-end clocks, timezone/DST and adjustment metadata. Held daily data do not support this entry test.

## Missing evidence and falsifiers

A short would require a dated direct guide-expectation panel, a GBV/conversion downside robust to credible vendor/cushion choices, and a preregistered net-of-cost executable entry test. RNPL cancellation/timing risk requires matched evidence before a numerical haircut. The case weakens if net realized growth and conversion hold through rollout laps, the issued guide matches the market's actual expectations, or a negative guide surprise fails to predict returns still available after entry.

Refresh the named expectation panel at decision time; validate future GBV assumptions; obtain intraday data only for a call-entry question. November 5 remains a project expected/planning date rather than a company future schedule verified in this audit. The latest SEC letter specifies the completed August 6 call at 17:00 New York. An inherited 2025Q3 L3 webcast/public-by proxy at 21:30Z differs from the [official 17:00 ET / 22:00Z schedule](https://investors.airbnb.com/press-releases/news-details/2025/Airbnb-to-Announce-Third-Quarter-2025-Results/default.aspx); it must not become a precise call boundary.

## Reproducible version trail

Model: integration_v2/model.json. Events: events_v1/run_v3. Forecast diagnostics: forecast_v1/results_v1. Independent arithmetic/source joins: sources_v1/review_v2 (314/314 checks, maximum absolute error 3.64e-12). Source inventory and dates: GE_SOURCE_RESULTS_v2.md. Exact input/output hashes accompany the PDF. The daily CSV's raw CRLF SHA differs from the retained LF-normalized hash only by line endings; both are documented in the source note. No new research fits or registry changes were performed by the memo builder.
'''
    (out/'ABNB_GBV_two_pager.md').write_text(md,encoding='utf-8')
    manifest={'operation':'create','pages':2,'source_hashes':{str(v.relative_to(ROOT)).replace('\\','/'):sha(v) for v in INPUTS.values()},
              'builder_sha256':sha(Path(__file__)),'model_zero_gap_q3_gbv_musd':q4_boundary,
              'model_zero_gap_q4_conversion_pct':lambda_boundary,'source_checks':{'four_quarters':True,'event_n':23,'holm_family_n':12,'all_primary_holm_1':True,'independent_checks':314},
              'artifacts':{x.name:sha(x) for x in out.iterdir() if x.is_file()},'render_qa':'Pending PNG inspection; additive QA receipt required'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'pdf':str(pdf),'pages':2,'q3_gbv_zero_gap':q4_boundary,'manifest':str(out/'manifest.json')}))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',default='output/pdf/gbv-event-20260915')
    args=ap.parse_args();build((ROOT/args.out).resolve())
