import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../../../..');
const out=path.join(root,'outputs/gbv-event-20260915');
const d=JSON.parse(await fs.readFile(path.join(out,'artifact_inputs.json'),'utf8'));
const wb=Workbook.create();
const runtimeStatus=[{stage:'created',exitCode:process.exitCode??null}];
const names=['Decision','Conversion','Inputs','Forecast audit','Event study','Event data','Sources'];
const sheets=Object.fromEntries(names.map(n=>[n,wb.worksheets.add(n)]));
const navy='#17324D',teal='#167D8D',red='#B34C3E',ink='#243746',muted='#64748B',pale='#EDF3F6';
const money='#,##0.0;(#,##0.0);"-"';
const pct='0.00%;(0.00%);"-"';
const num='0.00;(0.00);"-"';
const cell=(s,a,v)=>s.getRange(a).values=[[v]];
const formula=(s,a,f)=>{s.getRange(a).formulas=[[f]];s.getRange(a).format.font.color=f.includes("'!")||f.includes("'Inputs'")||f.includes("'Conversion'")?'#00804A':'#111111';};
const vals=(s,a,v)=>s.getRange(a).values=v;
function title(s,t,sub){cell(s,'B2',t);s.getRange('B2:M2').format={font:{name:'Arial',size:17,bold:true,color:navy},rowHeight:32};cell(s,'B3',sub);s.getRange('B3:M3').format.font={name:'Arial',size:10,color:muted};}
function head(s,a,arr){vals(s,a,[arr]);s.getRange(a).format={fill:navy,font:{name:'Arial',bold:true,color:'#FFFFFF'},rowHeight:32,wrapText:true};}
function band(s,a,t){cell(s,a.split(':')[0],t);s.getRange(a).format={fill:pale,font:{name:'Arial',bold:true,color:navy},rowHeight:27};}
function note(s,range,t){s.getRange(range).merge();cell(s,range.split(':')[0],t);s.getRange(range).format={font:{name:'Arial',size:10,color:muted},wrapText:true};}
function chart(s,type,range,start,end,t,fmt=money){const c=s.charts.add(type,Array.isArray(range)?range.map(r=>s.getRange(r)):s.getRange(range));c.setPosition(start,end);c.title=t;c.titleTextStyle.typeface='Arial';c.titleTextStyle.fontSize=13;c.legend={position:'top',textStyle:{typeface:'Arial',fontSize:10}};c.xAxis={axisType:type==='scatter'?'valueAxis':'textAxis',textStyle:{typeface:'Arial',fontSize:10}};c.yAxis={numberFormatCode:fmt,numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:10}};c.series.items.forEach((ss,i)=>{ss.fill=[teal,navy,red,'#D2A44C'][i%4];});return c;}
for(const s of Object.values(sheets)){s.showGridLines=false;s.getRange('A1:W120').format.font={name:'Arial',size:10,color:ink};s.getRange('A:A').format.columnWidth=3;s.getRange('B:B').format.columnWidth=28;s.getRange('C:W').format.columnWidth=13;s.getRange('A1:W120').format.rowHeight=23;s.freezePanes.freezeRows(5);}

// Explicit inputs, dates and provenance. Missing guide expectations stay blank.
const ins=sheets.Inputs;
title(ins,'Model inputs | one conditional working path','Blue values are editable. Green cells link to another sheet. USD millions unless stated.');
head(ins,'B5:F5',['GBV quarter','GBV $m','Input status','Available by','Lineage / limitation']);
ins.getRange('D:D').format.columnWidth=29;ins.getRange('E:E').format.columnWidth=16;ins.getRange('F:F').format.columnWidth=57;
vals(ins,'B6:F10',d.model.gbv_inputs.map(r=>[r.quarter,r.gbv_musd,r.status,r.information_date,r.limitation]));
ins.getRange('C6:C10').setNumberFormat(money);ins.getRange('C6:C10').format.font.color='#0000FF';ins.getRange('D6:F10').format.wrapText=true;ins.getRange('B6:F10').format.rowHeight=38;
head(ins,'B13:F13',['Target','Conversion lambda','Cushion','Lambda n','Last lambda observation']);
vals(ins,'B14:F17',d.model.forecast.map(r=>[r.quarter,r.lambda_decimal,r.cushion_decimal,r.lambda_n_train,r.lambda_knowable_from]));
ins.getRange('C14:D17').setNumberFormat(pct);ins.getRange('C14:D17').format.font={name:'Arial',color:'#0000FF',italic:true};
note(ins,'B19:F20','Lambda is a revenue / weighted-lag-GBV ratio, not a commission take rate. Weights are a fixed empirical mapping, not literal booking-cohort shares. Cushion = revenue / issued guide - 1. Eight realized quarters supply the inherited median.');
head(ins,'B23:F23',['Quarter','Street revenue','Direct guide expectation','Observed at (UTC)','Named source']);
vals(ins,'B24:F27',d.model.selected_comparisons.map(r=>[r.quarter,r.consensus_revenue_musd,null,r.observed_at,r.consensus_revenue_musd===null?'Unavailable; no vendor substitution':r.vendor]));
ins.getRange('C24:D27').format.font.color='#0000FF';ins.getRange('C24:D27').setNumberFormat(money);ins.getRange('E24:F27').format.wrapText=true;ins.getRange('B24:F27').format.rowHeight=41;
note(ins,'B29:F30','Direct guide expectations are unobserved. If an admissible direct estimate is entered, add its vendor and timestamp here before using it. Q1/Q2 2027 Street revenue remains unavailable; do not split annual estimates.');
head(ins,'B33:D33',['Observed Q3 guide','USDm','Disclosure date']);
vals(ins,'B34:D36',[['Low',4690,'2026-08-06'],['Midpoint',4730,'2026-08-06'],['High',4770,'2026-08-06']]);ins.getRange('C34:C36').setNumberFormat(money);
band(ins,'B39:F39','Precision check: change the GBV inputs only, not lambda');
head(ins,'B40:E40',['Quarter','Exact-input revenue','Delta from rounded','Scope']);
vals(ins,'B41:E44',d.model.precision_comparison.map(r=>[r.quarter,r.revenue_musd,r.revenue_delta_musd,'Frozen lambda; SEC GBV 29,187 / 27,247']));ins.getRange('C41:D44').setNumberFormat(money);ins.getRange('E41:F44').format.wrapText=true;
note(ins,'B47:F49','The current GBV assumptions inherit the prior L4 working case, including inputs originally derived from the component track. This is a shared input dependency, not independent confirmation. Q1 2027 GBV is an assumption needed for the explicit Q2 conversion. No second RNPL, fee or FX haircut is added.');

// Fully editable four-quarter economic chain, with explicit missing-input propagation.
const conv=sheets.Conversion;
title(conv,'GBV conversion | four-quarter build','Prepared 15 Sep 2026; inherited parameters through 13 Sep. No 2028 extension.');
head(conv,'B5:F5',['USDm, except ratios',...d.model.forecast.map(r=>r.quarter)]);
const labels={6:'GBV: previous quarter',7:'GBV: two quarters prior',8:'Weight: previous quarter',9:'Weighted lagged GBV',10:'Conversion lambda',11:'Revenue forecast',12:'Guidance cushion',13:'Implied guide midpoint',14:'Guide status',16:'Street revenue',17:'Assumed Street cushion',18:'Implied Street guide proxy',19:'Guide gap to proxy ($m)',20:'Guide gap to proxy (%)',21:'Direct guide expectation',22:'Gap to direct guide ($m)',24:'Break-even lambda*',25:'Lambda change (bp)*',26:'Break-even recent GBV*',27:'Recent GBV change (%)*'};
for(const [r,t]of Object.entries(labels))cell(conv,`B${r}`,t);
for(let i=0;i<4;i++){const c='CDEF'[i],ir=14+i,sr=24+i;const lag1=7+i,lag2=6+i;formula(conv,`${c}6`,`=IF(ISNUMBER('Inputs'!C${lag1}),'Inputs'!C${lag1},"n.a.")`);formula(conv,`${c}7`,`=IF(ISNUMBER('Inputs'!C${lag2}),'Inputs'!C${lag2},"n.a.")`);formula(conv,`${c}8`,'=2/3');formula(conv,`${c}9`,`=IF(AND(ISNUMBER(${c}6),ISNUMBER(${c}7)),IF(AND(${c}6>0,${c}7>0),${c}8*${c}6+(1-${c}8)*${c}7,"n.a."),"n.a.")`);formula(conv,`${c}10`,`=IF(ISNUMBER('Inputs'!C${ir}),'Inputs'!C${ir},"n.a.")`);formula(conv,`${c}11`,`=IF(AND(ISNUMBER(${c}9),ISNUMBER(${c}10)),IF(${c}10>0,${c}9*${c}10,"n.a."),"n.a.")`);formula(conv,`${c}12`,`=IF(ISNUMBER('Inputs'!D${ir}),'Inputs'!D${ir},"n.a.")`);formula(conv,`${c}13`,`=IF(AND(ISNUMBER(${c}11),ISNUMBER(${c}12)),IF(${c}12>-1,${c}11/(1+${c}12),"n.a."),"n.a.")`);cell(conv,`${c}14`,i===0?'Already issued':'Conditional');formula(conv,`${c}16`,`=IF(ISNUMBER('Inputs'!C${sr}),'Inputs'!C${sr},"n.a.")`);formula(conv,`${c}17`,`=${c}12`);formula(conv,`${c}18`,i===0?'="Already issued"':`=IF(AND(ISNUMBER(${c}16),ISNUMBER(${c}17)),IF(${c}17>-1,${c}16/(1+${c}17),"n.a."),"n.a.")`);formula(conv,`${c}19`,`=IF(AND(ISNUMBER(${c}13),ISNUMBER(${c}18)),${c}13-${c}18,"n.a.")`);formula(conv,`${c}20`,`=IF(AND(ISNUMBER(${c}13),ISNUMBER(${c}18)),IF(${c}18>0,${c}13/${c}18-1,"n.a."),"n.a.")`);formula(conv,`${c}21`,i===0?'="Already issued"':`=IF(ISNUMBER('Inputs'!D${sr}),'Inputs'!D${sr},"n.a.")`);formula(conv,`${c}22`,`=IF(AND(ISNUMBER(${c}13),ISNUMBER(${c}21)),${c}13-${c}21,"n.a.")`);formula(conv,`${c}24`,`=IF(AND(ISNUMBER(${c}16),ISNUMBER(${c}9)),${c}16/${c}9,"n.a.")`);formula(conv,`${c}25`,`=IF(AND(ISNUMBER(${c}24),ISNUMBER(${c}10)),(${c}24-${c}10)*10000,"n.a.")`);formula(conv,`${c}26`,`=IF(AND(ISNUMBER(${c}16),ISNUMBER(${c}10),ISNUMBER(${c}7)),(${c}16/${c}10-(1-${c}8)*${c}7)/${c}8,"n.a.")`);formula(conv,`${c}27`,`=IF(AND(ISNUMBER(${c}26),ISNUMBER(${c}6)),${c}26/${c}6-1,"n.a.")`);}
conv.getRange('C6:F27').setNumberFormat(money);for(const r of [8,10,12,17,20,24,27]){conv.getRange(`C${r}:F${r}`).setNumberFormat(pct);conv.getRange(`C${r}:F${r}`).format.font.italic=true;}
for(const r of[9,11,13,19])conv.getRange(`B${r}:F${r}`).format.fill=pale;
note(conv,'B29:F31','*Break-even ratios hold our other inputs fixed and equate model revenue with Street revenue. They are not observed Street GBV/conversion forecasts. A common cushion cancels from the relative guide gap. Q3 guide output is a diagnostic, never a future surprise.');
head(conv,'H5:J5',['Quarter','Revenue','Implied guide']);for(let i=0;i<4;i++){cell(conv,`H${i+6}`,d.model.forecast[i].quarter);formula(conv,`I${i+6}`,`=${'CDEF'[i]}11`);formula(conv,`J${i+6}`,`=${'CDEF'[i]}13`);}conv.getRange('I6:J9').setNumberFormat(money);
chart(conv,'bar','H5:J9','H11','O27','Conditional revenue and implied guide');
band(conv,'B34:H34','Q4 guide sensitivity | lambda change (basis points) across columns');
vals(conv,'C35:G35',[[-20,-10,0,10,20]]);cell(conv,'B35','Q3 GBV change');
[-.04,-.02,0,.02,.04].forEach((v,i)=>{const r=36+i;cell(conv,`B${r}`,v);for(const c of 'CDEFG')formula(conv,`${c}${r}`,`=IF(AND(ISNUMBER($D$6),ISNUMBER($D$7),ISNUMBER($D$10),ISNUMBER($D$12)),(($D$6*(1+$B${r})*$D$8+$D$7*(1-$D$8))*($D$10+${c}$35/10000))/(1+$D$12),"n.a.")`);});conv.getRange('B36:B40').setNumberFormat(pct);conv.getRange('C36:G40').setNumberFormat(money);conv.getRange('C36:G40').conditionalFormats.add('colorScale',{colors:['#F1D4CF','#FFFFFF','#CEE6DE'],thresholds:['min',{type:'percentile',value:50},'max']});note(conv,'B42:G44','Sensitivity values are conditional guide levels, not forecasts with assigned probabilities. GBV and conversion can move together. RNPL could affect booking timing, cancellations or conversion; without identified incremental data, adding another haircut would double-count an assumption.');

// Matched-window fixed-candidate audit; source results remain separate from live inputs.
const fa=sheets['Forecast audit'];title(fa,'Forecast risk | fixed earlier-origin replay','W1 and W2 are nested. Historical analysis is already explored; these results are not a new holdout.');
head(fa,'B5:E5',['Guide RMSE, $m','W1 (n=12)','W2 (n=10)','Interpretation']);
const meth=['candidate_k0_gbv','B1_guide_growth','B2_revenue_naive_cushion'];const mlabels=['GBV conversion candidate','Guide-growth baseline','Revenue-naive + cushion'];
for(let i=0;i<3;i++){cell(fa,`B${6+i}`,mlabels[i]);for(const[w,c]of [['W1','C'],['W2','D']]){const rr=d.scores.find(r=>r.window===w&&r.scope==='all_three'&&r.basis==='interval'&&r.method===meth[i]);cell(fa,`${c}${6+i}`,rr.rmse);}cell(fa,`E${6+i}`,i===0?'Promotion hurdle failed':'Same target rows');}fa.getRange('C6:D8').setNumberFormat(money);fa.getRange('E:E').format.columnWidth=24;
note(fa,'B10:F12','Scores use the project midpoint +/- $0.5m convention. Raw candidate RMSE is $63.9m / $64.1m. Candidate does not beat the guide-growth baseline in W2 and fails deletion robustness. Historical origins were roughly 48-62 days before the guide; this is not a calibrated Q1/Q2 2027 risk band.');
chart(fa,'bar','B5:D8','H5','O20','Guide error | lower is better');
head(fa,'B15:D15',['Variance, USDm squared','W1','W2']);
const fl=[['GBV input','gbv_shapley_musd'],['Conversion','conversion_shapley_musd'],['Cushion','cushion_shapley_musd']];
fl.forEach(([label,key],i)=>{cell(fa,`B${16+i}`,label);for(const[w,c]of[['W1','C'],['W2','D']])cell(fa,`${c}${16+i}`,d.moments.find(r=>r.window===w&&r.factor_a===key&&r.factor_b===key).contribution_to_population_variance);});
cell(fa,'B19','Covariance contribution');cell(fa,'B20','Reconciled total');for(const[w,c]of[['W1','C'],['W2','D']]){cell(fa,`${c}19`,d.variance.find(r=>r.window===w).covariance_contribution);formula(fa,`${c}20`,`=SUM(${c}16:${c}19)`);}fa.getRange('C16:D20').setNumberFormat(money);chart(fa,'bar','B15:D19','H22','O38','Correlated errors partly offset');
note(fa,'B22:F25','Exact symmetric (Shapley) attribution sums to raw guide error. Standalone factor variance cannot be added without covariance. The exact cells reconcile the W1 diagonal and covariance terms to 4,027.3 USDm squared. Observed population SD is $63.5m; independence would imply $82.6m. This ex-post decomposition explains historical error, not available trading features.');
note(fa,'B27:F30','Replacing only unknown GBV with realized GBV lowers raw guide RMSE to $36.4m / $38.7m. That is an oracle diagnostic, not a tradable strategy. Two events account for 51% / 61% of squared error; small samples and influential events prevent stable promotion. No new optimized predictor was fitted.');
head(fa,'B34:F34',['Target quarter','GBV effect','Conversion effect','Cushion effect','Raw guide error']);
const dec=d.decomposition.filter(r=>r.quarter>='2023Q1'&&r.status==='forecast'&&r.gbv_shapley_musd!==null);
const usable=dec.length?dec:d.decomposition.filter(r=>r.quarter>='2023Q1'&&r.gbv_shapley_musd!==null);
vals(fa,`B35:F${34+usable.length}`,usable.map(r=>[r.quarter,r.gbv_shapley_musd,r.conversion_shapley_musd,r.cushion_shapley_musd,r.error_raw_musd]));fa.getRange(`C35:F${34+usable.length}`).setNumberFormat(money);
cell(fa,'B49','Historical outputs stay frozen when working inputs change.');

// Full universe and precise daily price-leg definitions, no invented call candles.
const ed=sheets['Event data'];title(ed,'Earnings data | all 23 events','Daily raw ABNB and QQQ OHLC; gap = pre-release close to next open; session = next open to close.');
const headers=['Reported quarter','Release date','Guided quarter','Issued guide $m','Revenue Street $m','Guide / revenue proxy %','Guide / implied proxy %','ABNB gap %','ABNB session %','QQQ gap %','QQQ session %','Excess gap %','Excess session %','Excess close-close %','Vendor','Consensus timestamp','Eligibility'];
head(ed,'B5:R5',headers);vals(ed,'B6:R28',d.events.map(r=>[r.print_quarter,r.event_date,r.guided_quarter,r.first_guide_mid_musd,r.consensus_revenue_musd,r.published_guide_vs_revenue_consensus_pct,r.published_guide_vs_implied_guide_pct,r.abnb_gap_pct,r.abnb_session_pct,r.qqq_gap_pct,r.qqq_session_pct,r.gap_excess_pct,r.session_excess_pct,r.cc_excess_pct,r.consensus_vendor,r.consensus_as_of,r.primary_eligibility]));ed.getRange('B:B').format.columnWidth=18;ed.getRange('C:C').format.columnWidth=14;ed.getRange('D:O').format.columnWidth=14;ed.getRange('P:R').format.columnWidth=32;ed.getRange('E6:F28').setNumberFormat(money);ed.getRange('G6:O28').setNumberFormat(num);ed.getRange('B6:R28').format.rowHeight=42;ed.getRange('P6:R28').format.wrapText=true;
note(ed,'B31:K33','Returns in this sheet are percentage points, not decimal fractions. Excess = ABNB leg minus QQQ leg. Close-close is calculated from each ticker\'s compounded legs, not the sum of excess gap and excess session. A guide comparison is known only after the release; it cannot be used to earn the completed gap.');

const es=sheets['Event study'];title(es,'Earnings reactions | association, not a price law','23 events / 20 numeric forward guides / 16 raw comparison proxies / 15 implied-guide proxies.');
head(es,'B5:G5',['All-event association','n','Pearson r','Slope','95% low','95% high']);
const pairs=[['published_guide_vs_revenue_consensus_pct','gap_excess_pct','Raw proxy: gap'],['published_guide_vs_revenue_consensus_pct','session_excess_pct','Raw proxy: session'],['published_guide_vs_implied_guide_pct','gap_excess_pct','Implied proxy: gap'],['published_guide_vs_implied_guide_pct','session_excess_pct','Implied proxy: session']];
const ar=pairs.map(([signal,outcome,label])=>{const a=d.associations.find(r=>r.window==='all'&&r.signal===signal&&r.outcome===outcome);if(!a)throw Error('Association schema mismatch '+JSON.stringify(Object.keys(d.associations[0])));return {a,label};});
vals(es,'B6:G9',ar.map(({a,label})=>[label,a.n,a.pearson,a.slope,a.slope_95_lo,a.slope_95_hi]));es.getRange('D6:G9').setNumberFormat(num);
note(es,'B11:G14','Slope units: percentage points of excess stock return per 1 percentage point of comparison proxy. All 12 primary Holm-adjusted p-values are 1.0. Intervals include zero; leave-event/year results are unstable. This does not prove no relationship; it means this panel has not established a reliable trading response.');
head(es,'I5:K5',['Raw proxy %','Excess gap %','Excess session %']);const eligible=d.events.filter(r=>r.published_guide_vs_revenue_consensus_pct!==null);vals(es,`I6:K${5+eligible.length}`,eligible.map(r=>[r.published_guide_vs_revenue_consensus_pct,r.gap_excess_pct,r.session_excess_pct]));es.getRange(`I6:K${5+eligible.length}`).setNumberFormat(num);
chart(es,'scatter',[`I5:I${5+eligible.length}`,`J5:J${5+eligible.length}`],'B17','H33','Published guide proxy vs excess gap',num);
chart(es,'scatter',[`I5:I${5+eligible.length}`,`K5:K${5+eligible.length}`],'I24','O40','Same proxy vs next-session leg',num);
head(es,'B36:E36',['Entry method','Signal available','What can be measured','Current verdict']);
vals(es,'B37:E39',[
 ['Before release','Earlier GBV/conversion forecast + contemporaneous expectations','Origin-to-exit return, including intervening exposure','No promoted edge; sparse matched history'],
 ['Next regular open','Published guide comparison; other release news already known','Next open-to-close or explicitly chosen later exit','Gap is already completed; association is insufficient'],
 ['During release / call','Timestamped guide/news and executable quote','Release-to-call and call legs with costs','Unavailable: no verified intraday panel']]);es.getRange('B37:E39').format.wrapText=true;es.getRange('B37:E39').format.rowHeight=85;es.getRange('C:E').format.columnWidth=19;
note(es,'B42:G45','The original proxy compares an issued guide with expected realized revenue. The adjusted proxy assumes a historical common cushion; it is not observed guide expectations. In the earlier-origin model comparison, the shared cushion cancels exactly, so the relative signal is the same as candidate revenue / origin Street revenue - 1. No causal call attribution or calibrated stock-price target is assigned.');
head(es,'B48:D48',['Reported quarter','Excess gap %','Excess session %']);for(let i=0;i<23;i++){formula(es,`B${49+i}`,`='Event data'!B${6+i}`);formula(es,`C${49+i}`,`='Event data'!M${6+i}`);formula(es,`D${49+i}`,`='Event data'!N${6+i}`);}es.getRange('C49:D71').setNumberFormat(num);chart(es,'bar','B48:D71','F48','P70','Full earnings universe | daily legs',num);

const ov=sheets.Decision;title(ov,'ABNB | guidance-led event model','GBV conversion track only. Q3 2026 through Q2 2027. Prepared 15 Sep 2026.');
note(ov,'B5:M7','Current conclusion: the working Q4 case is mildly above a common-cushion Street proxy. Forecast and reaction tests have not established an investable edge. This model specifies what must change before a directional earnings trade can be justified.');ov.getRange('B5:M7').format.font={name:'Arial',bold:true,size:12,color:navy};ov.getRange('B5:M7').format.fill=pale;
head(ov,'B9:F9',['Quarter','Revenue $m','Guide $m','Street revenue $m','Guide treatment']);for(let i=0;i<4;i++){const r=10+i,c='CDEF'[i];cell(ov,`B${r}`,d.model.forecast[i].quarter);formula(ov,`C${r}`,`='Conversion'!${c}11`);formula(ov,`D${r}`,i===0?"='Inputs'!C35":`='Conversion'!${c}13`);formula(ov,`E${r}`,`='Conversion'!${c}16`);cell(ov,`F${r}`,i===0?'Observed midpoint':'Conditional estimate');}ov.getRange('C10:E13').setNumberFormat(money);ov.getRange('F:F').format.columnWidth=23;
band(ov,'B16:F16','Next key guide: Q4 2026');
const olabels=['Our implied guide ($m)','Street guide proxy ($m)','Conditional gap ($m)','Conditional gap (%)','Q3 GBV break-even ($m)','Q3 GBV change to break-even','Q4 lambda change to break-even (bp)'];const orefs=['D13','D18','D19','D20','D26','D27','D25'];for(let i=0;i<7;i++){cell(ov,`B${17+i}`,olabels[i]);formula(ov,`F${17+i}`,`='Conversion'!${orefs[i]}`);}ov.getRange('F17:F23').setNumberFormat(money);ov.getRange('F20').setNumberFormat(pct);ov.getRange('F22').setNumberFormat(pct);ov.getRange('B17:E23').merge(true);
note(ov,'B25:F28','A lower conditional guide requires weaker lagged GBV, lower conversion, or a larger management cushion. RNPL risk belongs in a measurable change to those inputs. A guide below revenue consensus alone is not evidence of a bearish surprise. Break-even thresholds are conditions, not probabilities or calibrated short triggers.');
chart(ov,'line',['B9:B13','C9:C13','D9:D13'],'H9','O27','Four-quarter path | Q3 guide observed');
band(ov,'B31:M31','Decision gates and next steps');
head(ov,'B33:E33',['Gate','Evidence in hand','Missing evidence','Next action']);
vals(ov,'B34:E37',[
 ['Forecast quality','Reproduced fixed replay; 12 / 10 matched observations','Outperformance in both windows and stable deletions','Keep conditional status; prospectively track input revisions'],
 ['Variant view','Dated Q3 / Q4 revenue expectations; explicit Q4 threshold','Observed guide expectations and Q1/Q2 Street quarters','Refresh vendor-dated expectations before the event'],
 ['Price response','23-event daily gap and next-session panel','Stable coefficient; release/call attribution','Obtain entitled ABNB + QQQ timestamped event bars'],
 ['Trade execution','Entry windows and information timing separated','Net costs, borrow/option pricing, robust ex-ante rule','Pre-register a rule before testing; do not infer a trade from this correlation']]);ov.getRange('B34:E37').format.wrapText=true;ov.getRange('B34:E37').format.rowHeight=85;ov.getRange('C:E').format.columnWidth=22;
note(ov,'B40:M42','Read order: Decision → Conversion → Forecast audit → Event study. Inputs holds the editable working assumptions; Event data keeps the full universe; Sources records evidence and limitations. The two-page memo is a static dated companion. Changing workbook inputs does not rewrite the historical audit or memo.');

const src=sheets.Sources;title(src,'Sources and audit trail','Source precision is not forecast accuracy. Vendor families are not independent replications.');
head(src,'B5:F5',['Item','Coverage / date','Source or path','Interpretation','Status']);src.getRange('C:C').format.columnWidth=22;src.getRange('D:D').format.columnWidth=65;src.getRange('E:E').format.columnWidth=43;src.getRange('F:F').format.columnWidth=20;
const sourceRows=[
 ['Q3 issued guide','6 Aug 2026','https://www.sec.gov/Archives/edgar/data/1559720/000119312526337928/d70413dex991.htm','$4,690–4,770m; midpoint $4,730m','Observed'],
 ['Current expectations','13 Sep 2026 15:20:58 UTC','L0_vintage_register.csv; Yahoo / LSEG-family API','Q3 $4,744.88187m; Q4 $3,161.02149m; n=36','Revenue estimates'],
 ['Other vendor panels','10–13 Sep 2026','L0 current/pit_history rows, separate vendor families','Zacks/DoltHub one family; S&P separately attributed','No silent mixing'],
 ['Parameters','Frozen through 13 Sep 2026','kernel_engine_v2/engine.py; KPI panel; calendar; cushion series','4 seasonal EWM ratios + 1 cushion; zero new optimized parameters','Inherited estimates'],
 ['GBV scenario','L4 working case','lane4_revenue_v2/snapshot_v1 + lane4_model_v2/snapshot_v2','Shared component-derived input ancestry; Q1 GBV assumption','Conditional'],
 ['Forecast replay','Fixed earlier origins','gbv_event_v1/forecast_v1/results_v1','20 frozen CSVs reproduced; 617 strict date checks; leakage poisoning','Promotion failed'],
 ['Reaction study',d.event_run,`gbv_event_v1/events_v1/${d.event_run}`,'23 full events; 16 raw / 15 adjusted proxies; 12 primary tests','Descriptive'],
 ['Daily price provenance','Retrieved 13 Sep; through 11 Sep','returns_v1/ohlc_daily.csv; Yahoo/yfinance raw bars','CRLF and LF byte hashes differ; normalized content agrees','Daily only'],
 ['Intraday coverage','0 verified event panels','GE_SOURCE_RESULTS_v2.md','Daily gap combines release, call and overnight information','Unavailable'],
 ['Forward call date','Project planning estimate','GE_SOURCE_RESULTS_v2.md','5 Nov 2026 not confirmed by issuer in bounded source check','Planning only'],
 ['Validation scope','Historical audit','GE_PREREG_v1.md','Previously examined data; nested W1/W2; small samples','No new holdout']];
vals(src,`B6:F${5+sourceRows.length}`,sourceRows);src.getRange(`B6:F${5+sourceRows.length}`).format.wrapText=true;src.getRange(`B6:F${5+sourceRows.length}`).format.rowHeight=70;
head(src,'B20:D20',['Input file','SHA256','Local relative path']);d.manifest.forEach((m,i)=>{cell(src,`B${21+i}`,path.basename(m.path));cell(src,`C${21+i}`,m.sha256);cell(src,`D${21+i}`,m.path);});src.getRange(`B21:D${20+d.manifest.length}`).format.wrapText=true;src.getRange(`B21:D${20+d.manifest.length}`).format.rowHeight=53;

// Separate the expectation convention from our management-cushion input.
head(ins,'B52:D52',['Target','Street cushion assumption','Convention']);
vals(ins,'B53:D56',d.model.forecast.map(r=>[r.quarter,r.cushion_decimal,'Common at default; independently editable']));
ins.getRange('C53:C56').setNumberFormat(pct);ins.getRange('C53:C56').format.font={name:'Arial',color:'#0000FF',italic:true};
ins.getRange('D53:F56').merge(true);ins.getRange('D53:F56').format.wrapText=true;
note(ins,'B58:F60','The Street cushion is an assumption, not observed guide expectations. It starts equal to our cushion. Editing our cushion alone holds this benchmark fixed; shared-cushion cancellation applies only when both use the same value. Historical audit figures remain frozen.');
for(let i=0;i<4;i++)formula(conv,`${'CDEF'[i]}17`,`=IF(ISNUMBER('Inputs'!C${53+i}),'Inputs'!C${53+i},"n.a.")`);
for(const c of 'CDEF'){
 formula(conv,`${c}26`,`=IF(AND(ISNUMBER(${c}16),ISNUMBER(${c}10),ISNUMBER(${c}7)),IF(AND(${c}10>0,${c}7>0),(${c}16/${c}10-(1-${c}8)*${c}7)/${c}8,"n.a."),"n.a.")`);
 formula(conv,`${c}27`,`=IF(AND(ISNUMBER(${c}26),ISNUMBER(${c}6)),IF(${c}6>0,${c}26/${c}6-1,"n.a."),"n.a.")`);
}
for(let r=36;r<=40;r++)for(const c of 'CDEFG')formula(conv,`${c}${r}`,`=IF(AND(ISNUMBER($D$6),ISNUMBER($D$7),ISNUMBER($D$10),ISNUMBER($D$12)),IF(AND($D$6>0,$D$7>0,$D$10+${c}$35/10000>0,$D$12>-1),(($D$6*(1+$B${r})*$D$8+$D$7*(1-$D$8))*($D$10+${c}$35/10000))/(1+$D$12),"n.a."),"n.a.")`);
note(fa,'B51:O53','Validation boundary: this earlier-origin replay used the frozen ex-COVID conversion variant. The current working four-quarter case inherits seasonal EWM conversion. The replay identifies method risks and failed promotion; its error statistics are not a direct backtest or calibrated interval for the current EWM case.');
for(const s of Object.values(sheets))s.getRange('A1:W120').format.verticalAlignment='center';
for(const[s,r]of [[conv,'C6:F27'],[ov,'C10:E13'],[es,'C6:G9']])s.getRange(r).format.horizontalAlignment='right';
ins.getRange('E41:F44').merge(true);ins.getRange('B41:F44').format.rowHeight=42;
ins.getRange('B6:F10').format.borders={insideHorizontal:{style:'thin',color:'#E2E8F0'}};
ins.getRange('B24:F27').format.borders={insideHorizontal:{style:'thin',color:'#E2E8F0'}};
ed.getRange('B6:R28').format.borders={insideHorizontal:{style:'thin',color:'#E2E8F0'}};
es.getRange('B36:E36').format.rowHeight=47;
formula(ov,'B5','=IF(ISNUMBER(F19),IF(F19>0,"Working Q4 guide is above the assumed Street guide proxy. ",IF(F19<0,"Working Q4 guide is below the assumed Street guide proxy. ","Working Q4 guide equals the assumed Street guide proxy. ")),"Working Q4 comparison is unavailable. ")&"Forecast and reaction tests have not established an investable edge. The proxy is conditional, not observed guide expectations."');
ov.getRange('B5:M7').format.font={name:'Arial',bold:true,size:12,color:navy};
ed.getRange('B5:R5').format.rowHeight=48;
// Meaningful dependency tests: edits change live outputs only, missing does not become zero.
wb.recalculate();
const read=(s,c)=>s.getRange(c).values[0][0];
const baseGuide=read(conv,'D13'),baseRev=read(conv,'D11'),oldGBV=read(ins,'C8'),oldC=read(ins,'D15');
assert.ok(Math.abs(baseGuide-d.model.forecast[1].implied_guide_musd)<1e-7);
for(let i=0;i<4;i++){assert.ok(Math.abs(read(conv,`${'CDEF'[i]}11`)-d.model.forecast[i].revenue_musd)<1e-7);}
cell(ins,'C8',oldGBV*1.01);wb.recalculate();assert.ok(read(conv,'D13')>baseGuide);assert.equal(read(fa,'C6'),d.scores.find(r=>r.window==='W1'&&r.scope==='all_three'&&r.method===meth[0]&&r.basis==='interval').rmse);cell(ins,'C8',oldGBV);
const fixedBenchmark=read(conv,'D18');cell(ins,'D15',0);wb.recalculate();assert.ok(Math.abs(read(conv,'D13')-baseRev)<1e-7);assert.equal(read(conv,'D18'),fixedBenchmark);cell(ins,'D15',null);wb.recalculate();assert.equal(read(conv,'D13'),'n.a.');cell(ins,'D15',oldC);
cell(ins,'C10',null);wb.recalculate();assert.equal(read(conv,'F11'),'n.a.');cell(ins,'C10',d.model.gbv_inputs[4].gbv_musd);
cell(ins,'C15',0);wb.recalculate();assert.equal(read(conv,'D26'),'n.a.');cell(ins,'C15',d.model.forecast[1].lambda_decimal);
cell(ins,'C8',0);wb.recalculate();assert.equal(read(conv,'D27'),'n.a.');cell(ins,'C8',oldGBV);
cell(ins,'D15',-1);wb.recalculate();assert.equal(read(conv,'E38'),'n.a.');cell(ins,'D15',oldC);
wb.recalculate();assert.ok(Math.abs(read(conv,'D13')-baseGuide)<1e-7);assert.equal(read(conv,'E16'),'n.a.');assert.equal(read(conv,'D21'),'n.a.');
await fs.writeFile(path.join(out,'workbook_checks.json'),JSON.stringify({status:'pass',assertions:['four-quarter exact tie-out','GBV edit propagates','historical audit invariant','zero cushion valid','missing cushion unavailable','missing Q1 GBV blocks Q2','restored outputs','missing Street/guide retained'],q4_guide:baseGuide,q4_proxy_gap:read(conv,'D19'),q3_gbv_break_even:read(conv,'D26'),lambda_change_bp:read(conv,'D25')},null,2));
const inspect=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#N/A',options:{useRegex:true,maxResults:300},maxChars:12000});await fs.writeFile(path.join(out,'formula_error_inspection.json'),JSON.stringify(inspect,null,2));await fs.writeFile(path.join(out,'formula_error_inspection.ndjson'),inspect.ndjson??'');runtimeStatus.push({stage:'inspected',exitCode:process.exitCode??null});
const regions=[['Decision','B2:O42'],['Conversion','B2:O44'],['Inputs','B2:F49'],['Forecast audit','B2:O53'],['Event study','B2:O45'],['Event study','B48:P71'],['Event data','B2:O16'],['Event data','B17:O33'],['Sources','B2:F17'],['Sources','B20:D29'],['Inputs','B52:F60'],['Event data','P5:R28']];
if(process.argv.includes('--render'))for(let i=0;i<regions.length;i++){const[s,r]=regions[i];const im=await wb.render({sheetName:s,range:r,scale:1.5,format:'png'});await fs.writeFile(path.join(out,`preview_${i+1}_${s.replaceAll(' ','_')}.png`),new Uint8Array(await im.arrayBuffer()));}
for(const sh of Object.values(sheets))for(const c of sh.charts.items)if(c.type==='line')for(const [i,s]of c.series.items.entries())s.line={fill:[teal,navy][i%2],style:'solid',width:2};
runtimeStatus.push({stage:'rendered',exitCode:process.exitCode??null});const file=await SpreadsheetFile.exportXlsx(wb);runtimeStatus.push({stage:'exported',exitCode:process.exitCode??null});await file.save(path.join(out,'ABNB_GBV_guidance.xlsx'));runtimeStatus.push({stage:'saved',exitCode:process.exitCode??null});await fs.writeFile(path.join(out,'runtime_status.json'),JSON.stringify(runtimeStatus,null,2));
await fs.writeFile(path.join(out,'chart_bindings.json'),JSON.stringify(names.flatMap(n=>sheets[n].charts.items.map(c=>({sheet:n,title:c.title.text,type:c.type,series:c.series.items.map(s=>({values:s.formula,categories:s.categoryFormula}))}))),null,2));
console.log(JSON.stringify({output:path.join(out,'ABNB_GBV_guidance.xlsx'),sheets:names.length,charts:names.reduce((n,s)=>n+sheets[s].charts.items.length,0),checks:'pass'}));
