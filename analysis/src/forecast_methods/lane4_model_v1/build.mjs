import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob, SpreadsheetFile, Workbook} from '@oai/artifact-tool';

const args=process.argv.slice(2);
const fmt='#,##0.0;(#,##0.0);"–"';
const pct='0.0%;(0.0%);"–"';
const money='"$"#,##0.00;("$"#,##0.00);"–"';
const navy='#203858',blue='#0000FF',green='#008000',amber='#FFF2CC';
const letters=n=>String.fromCharCode(65+n);
let wb,data,out,book,tracked=[];
const sheets={};
function V(s,a,x){sheets[s].getRange(a).values=[[x]];}
function F(s,a,x){sheets[s].getRange(a).formulas=[[x]];sheets[s].getRange(a).format.font.color=['Summary','Case comparison'].includes(s)?'#162B43':x.includes('!')?green:'#111111';}
function input(s,a,x){V(s,a,x);sheets[s].getRange(a).format.font.color=blue;tracked.push([s,a]);}
function row(s,r,label,unit=''){V(s,`C${r}`,label);if(unit)V(s,`D${r}`,unit);}
function band(s,r,label,last='L'){row(s,r,label);sheets[s].getRange(`C${r}:${last}${r}`).format={fill:'#DCE5F0',font:{bold:true,color:navy},rowHeight:23};}
function init(s,title,end='L',rows=70){
 const sh=sheets[s]=wb.worksheets.add(s);sh.showGridLines=false;
 sh.getRange(`A1:${end}${rows}`).format={font:{name:'Arial',size:10,color:'#111111'},rowHeight:19,verticalAlignment:'center'};
 sh.getRange(`A1:B${rows}`).format.columnWidth=2;
 sh.getRange(`C1:C${rows}`).format.columnWidth=48;
 sh.getRange(`D1:D${rows}`).format.columnWidth=9;
 sh.getRange(`E1:${end}${rows}`).format.columnWidth=16;
 sh.getRange(`E1:${end}${rows}`).setNumberFormat(fmt);
 V(s,'C2',title);sh.getRange(`C2:${end}2`).format={font:{name:'Arial',size:14,bold:true,color:navy},rowHeight:27,borders:{bottom:{style:'thin',color:navy}}};
 V(s,'C4','Case selected:');
 sh.getRange('E4:H4').format.font.color=green;
 if(!['Summary','Case comparison','Valuation'].includes(s)){sh.freezePanes.freezeRows(7);sh.freezePanes.freezeColumns(4);}
 return sh;
}
const annualKeys=['cor_per_gbv','ops_cpn','pd_cash','bpm_cash','fop_cash','ga_cash','addback_pct','sbc_growth','int_income','int_expense','cash_tax_pct','d_unearned_pct','eff_tax_rate','ai_referral_pct','buybacks','capex_pct','wc_resid_pct','da_pct','inherited_revenue_growth','inherited_nights_growth','inherited_gbv_growth','nb_cost'];
const annualLabels=['Processing cost per GBV growth','Support cost per night growth','Product development growth','Brand/performance marketing growth','Field operations/policy growth','G&A growth','Total EBITDA addbacks including D&A / revenue','SBC growth','Interest income','Interest expense','Cash taxes / revenue','Change in unearned fees / revenue','Effective tax rate','AI referral expense / revenue','Buybacks','Capex / revenue','Working capital residual / revenue','D&A / revenue (within total addbacks)','Inherited revenue growth','Inherited nights growth','Inherited GBV growth','New initiative costs (inherited dollars)'];
const annualRow=Object.fromEntries(annualKeys.map((k,i)=>[k,91+i]));
const globalKeys=['price','net_cash_2q26','shares_2q26','cost_of_equity','terminal_growth','dcf_start_growth','exit_ev_ebitda','exit_ev_fcf','exit_p_sbcfcf','exit_p_earnings','withholding_pct','price_growth','margin_cap'];
const globalLabels=['Buyback/issuance price anchor, 4 Sep 2026','Opening net cash ex customer funds, 30 Jun 2026','Opening diluted share proxy, 30 Jun 2026','Cost of equity','Terminal growth','DCF starting FCF growth','EV / FY27 adjusted EBITDA','EV / FY27 FCF','P / FY27 SBC-adjusted FCF','P / FY27 earnings proxy','RSU withholding / SBC','Price growth for share issuance/buybacks','Adjusted EBITDA margin cap'];
const globalRow=Object.fromEntries(globalKeys.map((k,i)=>[k,119+i]));
const gr=k=>`'Assumptions'!$F$${globalRow[k]}`;
const ar=(k,c)=>`'Assumptions'!${c}${annualRow[k]}`;
const sourceRow={rev:9,nights:10,gbv:11,cor:12,ops:13,pd:14,bpm:15,fop:16,ga:17,sbc:18,adj:19};
const h1Row={rev:25,nights:26,gbv:27,fcf:28,buybacks:29,withholding:30,sbc:31};
const costRows={revenue:8,gbv:9,nights:10,cor:13,ops:14,pd:15,bpm:16,fop:17,ga:18,nb_cost:19,ai_cost:20,cash_costs:21,addbacks:23,adj_uncapped:24,adj_ebitda:25,margin:26,sbc:29,da:30,op_income:31,interest_income:32,interest_expense:33,pretax:34,net_income:36};
const cashRows={net_income:8,fcf:18,sbc_adj_fcf:20,net_cash:28,shares:36,eps:37};

async function build(){
 wb=Workbook.create();
 for(const [s,title,rows] of [['Summary','Airbnb financial review',30],['Assumptions','Editable operating and financial assumptions',145],['Revenue','Operating inputs and revenue recognition',35],['Costs','Operating costs and earnings',40],['Cash','Free cash flow, net cash and shares',40],['Valuation','Conditional valuation at 31 December 2027',87],['Case comparison','Scenario results captured from one model',230],['Source','Read-only source inputs and provenance',78]])init(s,title,'L',rows);
 sheets.Summary.tabColor=navy;sheets.Assumptions.tabColor='#557599';
 // One authoritative selector. Every operating driver has its active row above its seven cases.
 V('Assumptions','C4','Case number (1–7)');input('Assumptions','E4',1);
 sheets.Assumptions.getRange('E4').dataValidation={rule:{type:'whole',operator:'between',formula1:1,formula2:7}};
 sheets.Assumptions.getRange('E4').format.fill=amber;
 sheets.Assumptions.getRange('E4').setNumberFormat('0');
 data.cases.forEach((c,i)=>V('Assumptions',`K${119+i}`,`${i+1}: ${c.label}`));
 F('Assumptions','G4',`=CHOOSE($E$4,${data.cases.map(c=>'"'+c.label+'"').join(',')})`);
 sheets.Assumptions.getRange('G4').format.font.color=green;
 const qcols=Array.from({length:8},(_,i)=>letters(i+4));
 const qkeys=data.cases[0].quarters.map(q=>q.quarter);
 for(const s of ['Assumptions','Revenue']){
   qcols.forEach((c,i)=>V(s,`${c}7`,`Q${qkeys[i].slice(-1)}:${qkeys[i].slice(2,4)}`));
   sheets[s].getRange('E7:L7').format={fill:navy,font:{bold:true,color:'#FFFFFF'},horizontalAlignment:'center'};
 }
 const drivers=[['nights',10,'Nights through Q4:26 (K0: cost proxy)','m'],['adr',20,'ADR through Q4:26 (K0 unavailable)','USD'],['gbv_override',30,'GBV-only override (K0 case)','USD m'],['lambda',40,'Seasonal lambda (fixed 2/3 benchmark)','%'],['cushion',50,'Guidance cushion','%'],['adjustment',60,'Net after-hedge revenue sensitivity','%'],['rev_growth',70,'Inherited revenue growth after kernel coverage','%'],['nights_growth',150,'Inherited nights growth Q1:27 onward','%'],['adr_growth',160,'Inherited ADR growth Q1:27 onward','%']];
 const fidx=new Map(data.forecasts.map(r=>[`${r.scenario}/${r.quarter}`,r]));
 const oidx=new Map(data.operating_inputs.map(r=>[`${r.scenario}/${r.quarter}`,r]));
 for(const [key,r,label,unit] of drivers){
   row('Assumptions',r,label,unit);sheets.Assumptions.getRange(`C${r}:L${r}`).format.fill='#E9EFF6';
   data.cases.forEach((c,i)=>row('Assumptions',r+i+1,c.label));
   qcols.forEach((col,qi)=>{
     const q=qkeys[qi];let refs=[];
     data.cases.forEach((c,ci)=>{
       const qr=c.quarters[qi],f=fidx.get(`${c.source_scenario}/${q}`),op=oidx.get(`${c.source_scenario}/${q}`);
       let x=null;
       if(key==='nights')x=qi<4?qr.nights:null;
       if(key==='adr')x=qi>=4||c.source_scenario==='k0_conditional'&&qi>=2&&qi<=3?null:qr.gbv/qr.nights;
       if(key==='gbv_override')x=c.source_scenario==='k0_conditional'&&qi>=2&&qi<=3?qr.gbv:null;
       if(key==='lambda')x=f?Number(f.lambda_pct)/100:null;
       if(key==='cushion')x=f?Number(f.cushion_decimal):null;
       if(key==='adjustment')x=f?c.adjustment:null;
       if(key==='rev_growth')x=qr.kind==='Inherited growth'?qr.inherited_growth:null;
       if(key==='nights_growth'&&qi>=4)x=qr.nights/c.quarters[qi-4].nights-1;
       if(key==='adr_growth'&&qi>=4)x=(qr.gbv/qr.nights)/(c.quarters[qi-4].gbv/c.quarters[qi-4].nights)-1;
       input('Assumptions',`${col}${r+ci+1}`,qi<2?null:x);refs.push(`${col}${r+ci+1}`);
     });
     F('Assumptions',`${col}${r}`,`=IF(CHOOSE($E$4,${refs.map(ref=>`ISBLANK(${ref})`).join(',')}),"",CHOOSE($E$4,${refs.join(',')}))`);
     if(qi<2&&key==='nights')F('Assumptions',`${col}${r}`,`='Source'!${letters(qi+4)}35`);
     if(qi<2&&key==='adr')F('Assumptions',`${col}${r}`,`='Source'!${letters(qi+4)}36/'Source'!${letters(qi+4)}35`);
     if(['lambda','cushion','adjustment','rev_growth','nights_growth','adr_growth'].includes(key))sheets.Assumptions.getRange(`${col}${r}:${col}${r+7}`).setNumberFormat(pct);
   });
 }
 V('Assumptions','C81','Blue inputs are editable. Shared financial drivers below apply to every operating case.');
 V('Assumptions','C82','Blank sensitivity means unestimated. ±1% is a generic net after-hedge consolidated-revenue perturbation.');
 V('Assumptions','C83','K0: GBV is identified. Reference-case nights drive support costs; its ADR is not identified.');
 V('Assumptions','C84','Kernel coefficients are fixed 2/3 and 1/3. A quarter’s input GBV first affects next-quarter revenue.');
 band('Assumptions',88,'Inherited financial assumptions','H');
 ['FY:26','FY:27','FY:28'].forEach((y,i)=>V('Assumptions',`${letters(i+5)}89`,y));
 annualKeys.forEach((key,i)=>{
   const r=annualRow[key];row('Assumptions',r,annualLabels[i]);
   for(let j=0;j<3;j++){const year=String(2026+j),col=letters(j+5);input('Assumptions',`${col}${r}`,key.startsWith('inherited_')&&j<2?null:key==='nb_cost'?data.nb_cost[year]:data.inputs[year][key]);
    if(!['int_income','int_expense','buybacks','nb_cost'].includes(key))sheets.Assumptions.getRange(`${col}${r}`).setNumberFormat(pct);}
 });
 band('Assumptions',117,'Capital and valuation assumptions','H');
 globalKeys.forEach((k,i)=>{row('Assumptions',globalRow[k],globalLabels[i]);input('Assumptions',`F${globalRow[k]}`,data.globals[k]);
 if(['cost_of_equity','terminal_growth','dcf_start_growth','withholding_pct','price_growth','margin_cap'].includes(k))sheets.Assumptions.getRange(`F${globalRow[k]}`).setNumberFormat(pct);});
 sheets.Assumptions.getRange(`F${globalRow.price}`).setNumberFormat(money);
 V('Assumptions','C133','Valuation date');V('Assumptions','F133',new Date('2027-12-31T00:00:00Z'));sheets.Assumptions.getRange('F133').setNumberFormat('mm/dd/yy');
 V('Assumptions','C134','DCF fade: 10 years, fixed layout. All future rates are inherited assumptions.');
 V('Assumptions','C135','Inputs: legacy driver-model base scenario; L4 forecast.csv and operating_inputs.csv. Version/hash manifest delivered.');
 V('Assumptions','C136','No adopted direction, target or probabilities. Multiple assumptions are editable; no growth-to-multiple regression.');
 V('Assumptions','C137','L3 conversion-study acceptance is pending. The current fixed 2/3 K0 benchmark is provisional for conversion claims.');
 V('Assumptions','C138','L3 FX/RNPL evidence and incremental adapter are separately pending; no new conversion parameters estimated here.');
 row('Assumptions',140,'Fixed benchmark prior-quarter GBV weight');input('Assumptions','F140',2/3);sheets.Assumptions.getRange('F140').setNumberFormat(pct);
 V('Assumptions','C141','Replacement weight requires matching seasonal coefficients from one accepted L3 conversion version.');
 // Source inputs preserve the original fiscal and share-count basis.
 row('Source',7,'FY2025 source anchors','USD m');
 const sourceLabels={rev:'Revenue',nights:'Nights (millions)',gbv:'Booked GBV',cor:'Cost of revenue',ops:'Operations and support',pd:'Product development excluding SBC',bpm:'Brand/performance marketing',fop:'Field operations and policy',ga:'G&A excluding SBC',sbc:'Stock-based compensation',adj:'Adjusted EBITDA',fcf:'Free cash flow',buybacks:'Share repurchases',withholding:'RSU withholding'};
 for(const [k,r] of Object.entries(sourceRow)){row('Source',r,sourceLabels[k]);V('Source',`E${r}`,data.fy25[k]);}
 row('Source',23,'First-half 2026 actuals');
 for(const [k,r] of Object.entries(h1Row)){row('Source',r,sourceLabels[k]);V('Source',`E${r}`,data.h1[k]);}
 row('Source',34,'Reported quarter');V('Source','E34','Q1:26');V('Source','F34','Q2:26');
 for(const [key,r] of [['nights',35],['gbv',36],['revenue',37]]){row('Source',r,key);for(let i=0;i<2;i++)V('Source',`${letters(i+4)}${r}`,data.cases[0].quarters[i][key]);}
 V('Source','C40','Sources: 13_driver_model.py FY25/H1_26 and reported KPI panel; copied with source hash.');
 V('Source','C41','Opening net cash excludes $12,224m customer funds matched by liabilities. Net debt financing held unchanged.');
 V('Source','C42','597m shares: Q2:26 diluted weighted-average proxy for period-end fully diluted shares.');
 V('Source','C43','Issuance uses SBC / assumed price after withholding. EPS uses ending shares; it is an earnings proxy.');
 V('Source','C44','Legacy price anchor is the 4 Sep 2026 close, $181.94, for repurchases/issuance only; not a current quote.');
 V('Source','C45','Financial inputs inherited from model/assumptions.md and 13_driver_model.py, completed model vintage 7 Sep 2026.');
 V('Source','C46','Revenue sources: L4 versioned bridge. L3 cohort/currency/timing evidence is pending an explicit handoff.');
 V('Source','C48','Legacy base model inputs for arithmetic reproduction');V('Source','E49','FY:27');V('Source','F49','FY:28');
 const legacyKeys=['adj_ebitda','fcf','sbc_adj_fcf','net_income','net_cash','shares_end'];
 legacyKeys.forEach((k,i)=>{row('Source',50+i,['Adjusted EBITDA','Free cash flow','SBC-adjusted free cash flow','Net income','Net cash ex customer funds','Ending diluted share proxy (millions)'][i]);for(let j=0;j<2;j++)V('Source',`${letters(j+4)}${50+i}`,data.legacy_annual[String(2027+j)][k]);});
 row('Source',58,'Legacy EV/EBITDA');V('Source','E58',16.5);row('Source',59,'Legacy EV/FCF');V('Source','E59',14.3);
 row('Source',60,'Legacy P/FCF and P/E');V('Source','E60',19.5);row('Source',61,'Legacy cost of equity');V('Source','E61',.105);
 row('Source',62,'Legacy DCF start growth');V('Source','E62',.09);row('Source',63,'Legacy terminal growth');V('Source','E63',.03);
 sheets.Source.getRange('E61:E63').setNumberFormat(pct);
 // Revenue build: active assumptions -> nights/ADR -> GBV -> fixed seasonal kernel.
 for(const [r,label,unit] of [[8,'Nights (K0 uses reference support-cost proxy)','m'],[9,'ADR','USD'],[10,'Booked GBV','USD m'],[12,'Seasonal lambda','%'],[13,'Prior-quarter GBV','USD m'],[14,'Two-quarters-prior GBV','USD m'],[15,'Kernel weighted GBV (2/3, 1/3)','USD m'],[16,'Consolidated kernel revenue','USD m'],[17,'Hypothetical incremental dollars','USD m'],[18,'Revenue used by model','USD m'],[19,'Guidance cushion','%'],[20,'Implied management guide','USD m'],[23,'Inherited revenue growth','%'],[25,'Basis']])row('Revenue',r,label,unit);
 qcols.forEach((col,i)=>{
   F('Revenue',`${col}8`,i<2?`='Source'!${letters(i+4)}35`:i<4?`=IF(ISNUMBER('Assumptions'!${col}10),'Assumptions'!${col}10,"Missing nights")`:`=${qcols[i-4]}8*(1+'Assumptions'!${col}150)`);
   F('Revenue',`${col}9`,i<2?`='Source'!${letters(i+4)}36/'Source'!${letters(i+4)}35`:i<4?`=IF('Assumptions'!${col}20="","n.a.",'Assumptions'!${col}20)`:`=${qcols[i-4]}10/${qcols[i-4]}8*(1+'Assumptions'!${col}160)`);
   if(i<2){F('Revenue',`${col}10`,`='Source'!${letters(i+4)}36`);F('Revenue',`${col}18`,`='Source'!${letters(i+4)}37`);V('Revenue',`${col}25`,'Actual');}
   else{
     F('Revenue',`${col}10`,`=IF('Assumptions'!${col}30="",${col}8*${col}9,'Assumptions'!${col}30)`);
     if(i<=4){
       F('Revenue',`${col}12`,`='Assumptions'!${col}40`);F('Revenue',`${col}13`,`=${qcols[i-1]}10`);F('Revenue',`${col}14`,`=${qcols[i-2]}10`);
       F('Revenue',`${col}15`,`=${col}13*'Assumptions'!$F$140+${col}14*(1-'Assumptions'!$F$140)`);F('Revenue',`${col}16`,`=${col}12*${col}15`);
       F('Revenue',`${col}17`,`=IF(ISNUMBER('Assumptions'!${col}60),${col}16*'Assumptions'!${col}60,"Unestimated")`);
       F('Revenue',`${col}18`,`=IF(ISNUMBER('Assumptions'!${col}60),${col}16+${col}17,${col}16)`);
       F('Revenue',`${col}19`,`='Assumptions'!${col}50`);F('Revenue',`${col}20`,`=${col}18/(1+${col}19)`);V('Revenue',`${col}25`,'Kernel covered');V('Revenue',`${col}24`,i===2?'Issued diagnostic':'Conditional guide');
     }else{
       F('Revenue',`${col}23`,`='Assumptions'!${col}70`);F('Revenue',`${col}18`,`=${qcols[i-4]}18*(1+${col}23)`);V('Revenue',`${col}25`,'Inherited growth');
     }
   }
 });
 for(const r of [12,19,23])sheets.Revenue.getRange(`E${r}:L${r}`).setNumberFormat(pct);
 row('Revenue',24,'Guide status');
 sheets.Revenue.getRange('C18:L18').format.font.bold=true;
 V('Revenue','C28','USD GBV already embeds booking FX. No full FX factor, old take-rate wedge or new-business revenue is added.');
 V('Revenue','C29','L3 FX/RNPL adjustment is pending. ±1% perturbs net after-hedge revenue; it is not a pre-hedge FX factor.');
 V('Revenue','C30','Q3 nights affect Q4 revenue. Q4 nights first affect Q1:27. No contemporaneous booking effect in this kernel.');
 V('Revenue','C31','K0 support-cost nights are assumed from the review case. K0 revenue still uses its independent GBV inputs.');
 V('Revenue','C32','Fixed 2/3 K0 is the benchmark. Conversion-dependent conclusions await a separately accepted L3 study.');
 // Costs: preserve the original cost-lever sequence, single active financial build.
 const costLabels={revenue:'Consolidated revenue',gbv:'Booked GBV',nights:'Nights for support cost',cor:'Cost of revenue, inherited definition',ops:'Operations and support',pd:'Product development excluding SBC',bpm:'Brand/performance marketing',fop:'Field operations and policy',ga:'G&A excluding SBC',nb_cost:'New initiative costs, inherited',ai_cost:'AI referral expense',cash_costs:'Operating costs excluding SBC',addbacks:'Total EBITDA addbacks including D&A',adj_uncapped:'Adjusted EBITDA before margin cap',adj_ebitda:'Adjusted EBITDA',margin:'Adjusted EBITDA margin',sbc:'Stock-based compensation',da:'D&A (included in total addbacks)',op_income:'Operating income proxy',interest_income:'Interest income',interest_expense:'Interest expense',pretax:'Pretax income',net_income:'Net income proxy'};
 for(const [k,r] of Object.entries(costRows))row('Costs',r,costLabels[k],k==='nights'?'m':k==='margin'?'%':'USD m');
 for(const [s,header] of [['Costs','FY:25A'],['Cash','30-Jun-26 anchor']]){
  V(s,'E7',header);['FY:26E','FY:27E','FY:28E'].forEach((y,i)=>V(s,`${letters(i+5)}7`,y));
  sheets[s].getRange('E7:H7').format={fill:navy,font:{bold:true,color:'#FFFFFF'},horizontalAlignment:'center'};
 }
 for(const k of ['revenue','gbv','nights','cor','ops','pd','bpm','fop','ga','sbc','adj_ebitda']){
 const sourceK=k==='revenue'?'rev':k==='adj_ebitda'?'adj':k;F('Costs',`E${costRows[k]}`,`='Source'!E${sourceRow[sourceK]}`);}
 for(let j=0;j<3;j++){
   const col=letters(j+5),prev=letters(j+4);
   for(const [k,rr] of [['revenue',18],['gbv',10],['nights',8]]){
     const r=costRows[k];F('Costs',`${col}${r}`,j<2?`=SUM('Revenue'!${j===0?'E':'I'}${rr}:${j===0?'H':'L'}${rr})`:`=${prev}${r}*(1+${ar('inherited_'+k+'_growth',col)})`);
   }
   F('Costs',`${col}13`,`=${prev}13/${prev}9*(1+${ar('cor_per_gbv',col)})*${col}9`);
   F('Costs',`${col}14`,`=${prev}14/${prev}10*(1+${ar('ops_cpn',col)})*${col}10`);
   for(const [r,k] of [[15,'pd_cash'],[16,'bpm_cash'],[17,'fop_cash'],[18,'ga_cash']])F('Costs',`${col}${r}`,`=${prev}${r}*(1+${ar(k,col)})`);
   F('Costs',`${col}19`,`=${ar('nb_cost',col)}`);F('Costs',`${col}20`,`=${col}8*${ar('ai_referral_pct',col)}`);F('Costs',`${col}21`,`=SUM(${col}13:${col}20)`);
   F('Costs',`${col}23`,`=${col}8*${ar('addback_pct',col)}`);F('Costs',`${col}24`,`=${col}8-${col}21+${col}23`);F('Costs',`${col}25`,`=MIN(${col}24,${col}8*${gr('margin_cap')})`);F('Costs',`${col}26`,`=${col}25/${col}8`);
   F('Costs',`${col}29`,`=${prev}29*(1+${ar('sbc_growth',col)})`);F('Costs',`${col}30`,`=${col}8*${ar('da_pct',col)}`);F('Costs',`${col}31`,`=${col}25-${col}29-${col}23`);
   F('Costs',`${col}32`,`=${ar('int_income',col)}`);F('Costs',`${col}33`,`=${ar('int_expense',col)}`);F('Costs',`${col}34`,`=SUM(${col}31:${col}32)-${col}33`);F('Costs',`${col}36`,`=${col}34*(1-${ar('eff_tax_rate',col)})`);
 }
 sheets.Costs.getRange('F26:H26').setNumberFormat(pct);
 for(const r of [8,21,25,36])sheets.Costs.getRange(`C${r}:H${r}`).format={font:{bold:true},borders:{top:{style:'thin',color:'#BCCADA'}}};
 V('Costs','C39','D&A is part of total addbacks. It is shown separately for disclosure and is not deducted twice.');
 // Cash and ending-share schedule preserves only H2 flows after the June anchor.
 const cashLabels={8:'Net income proxy',10:'Adjusted EBITDA',11:'Interest income',12:'Interest expense',13:'Cash taxes',14:'Change in unearned fees',15:'Working capital residual',16:'Capex',18:'Free cash flow (legacy convention)',19:'Stock-based compensation',20:'SBC-adjusted free cash flow',23:'Opening net cash ex customer funds',24:'FCF since opening balance',25:'Buybacks since opening balance',26:'RSU withholding since opening balance',28:'Ending net cash ex customer funds',30:'Opening diluted share proxy',31:'Assumed repurchase/issuance price',32:'Shares repurchased',33:'RSU shares issued after withholding',36:'Ending diluted share proxy',37:'Earnings per ending share proxy'};
 for(const [r,label] of Object.entries(cashLabels))row('Cash',Number(r),label,[30,32,33,36].includes(Number(r))?'m':Number(r)===31||Number(r)===37?'USD':'USD m');
 F('Cash','E28',`=${gr('net_cash_2q26')}`);F('Cash','E36',`=${gr('shares_2q26')}`);
 for(let j=0;j<3;j++){
   const c=letters(j+5),p=letters(j+4);
   for(const [r,cr] of [[8,36],[10,25],[11,32],[12,33],[19,29]])F('Cash',`${c}${r}`,`='Costs'!${c}${cr}`);
   for(const [r,k] of [[13,'cash_tax_pct'],[14,'d_unearned_pct'],[15,'wc_resid_pct'],[16,'capex_pct']])F('Cash',`${c}${r}`,`='Costs'!${c}8*${ar(k,c)}`);
   F('Cash',`${c}18`,`=SUM(${c}10:${c}11)-SUM(${c}12:${c}13)+SUM(${c}14:${c}15)-${c}16`);F('Cash',`${c}20`,`=${c}18-${c}19`);
   F('Cash',`${c}23`,`=${p}28`);F('Cash',`${c}24`,`=${c}18${j===0?"-'Source'!E28":''}`);F('Cash',`${c}25`,`=${ar('buybacks',c)}${j===0?"-'Source'!E29":''}`);
   F('Cash',`${c}26`,`=${c}19*${gr('withholding_pct')}${j===0?"-'Source'!E30":''}`);F('Cash',`${c}28`,`=SUM(${c}23:${c}24)-SUM(${c}25:${c}26)`);
   F('Cash',`${c}30`,`=${p}36`);F('Cash',`${c}31`,`=${gr('price')}*(1+${gr('price_growth')})^${j}`);F('Cash',`${c}32`,`=${c}25/${c}31`);
   F('Cash',`${c}33`,`=(${c}19${j===0?"-'Source'!E31":''})/${c}31*(1-${gr('withholding_pct')})`);F('Cash',`${c}36`,`=${c}30-${c}32+${c}33`);F('Cash',`${c}37`,`=${c}8/${c}36`);
 }
 sheets.Cash.getRange('F37:H37').setNumberFormat(money);sheets.Cash.getRange('F31:H31').setNumberFormat(money);
 for(const r of [18,20,28,36])sheets.Cash.getRange(`C${r}:H${r}`).format={font:{bold:true},borders:{top:{style:'thin',color:'#BCCADA'}}};
 V('Cash','C40','The model starts at 30 Jun 2026. Only H2:26 flows affect the FY26 net-cash and share roll.');
 V('Cash','C41','Zero change in unearned fees is an inherited cash assumption, not an estimated RNPL result.');
 // Valuation is a forward convention, not a target adoption. DCF explicitly uses FY27 FCF.
 const vl={8:'FY27 adjusted EBITDA',9:'Exit EV / EBITDA',10:'Enterprise value',11:'FY27 ending net cash ex customer funds',12:'Equity value',13:'FY27 ending diluted share proxy',14:'EV/EBITDA value per share',17:'EV / FY27 FCF',18:'P / FY27 SBC-adjusted FCF',19:'P / FY27 earnings proxy',20:'FY28 EV/EBITDA discounted one year',21:'DCF on FCF (legacy forward convention)',23:'Six-lens arithmetic mean',26:'DCF: year',27:'FCF growth',28:'FCF',29:'Discount factor',30:'Discounted FCF',32:'Terminal enterprise value',33:'DCF enterprise value',36:'Legacy reproduction (separate inputs)',38:'Legacy FY27 EBITDA lens',39:'Legacy FY27 FCF lens',40:'Legacy SBC-adjusted FCF lens',41:'Legacy earnings proxy lens',42:'Legacy FY28 EBITDA discounted lens',43:'Legacy DCF on FCF',45:'Legacy six-lens mean'};
 for(const [r,label] of Object.entries(vl))row('Valuation',Number(r),label);
 for(const [cell,formula] of Object.entries({E8:"='Costs'!G25",E9:`=${gr('exit_ev_ebitda')}`,E10:'=E8*E9',E11:"='Cash'!G28",E12:'=SUM(E10:E11)',E13:"='Cash'!G36",E14:'=E12/E13',E17:`=(${gr('exit_ev_fcf')}*'Cash'!G18+E11)/E13`,E18:`=${gr('exit_p_sbcfcf')}*'Cash'!G20/E13`,E19:`=${gr('exit_p_earnings')}*'Cash'!G37`,E20:`=(${gr('exit_ev_ebitda')}*'Costs'!H25+'Cash'!H28)/'Cash'!H36/(1+${gr('cost_of_equity')})`,E21:'=(E33+E11)/E13',E23:'=(SUM(E17:E21)+E14)/6'}))F('Valuation',cell,formula);
 // Ten-year strip, years in E:N, preserves explicit discount timing.
 sheets.Valuation.getRange('M1:N86').format={font:{name:'Arial',size:10},columnWidth:16,rowHeight:19};
 sheets.Valuation.getRange('M1:N86').setNumberFormat(fmt);
 for(let t=0;t<10;t++){
   const c=letters(4+t),p=letters(3+t);V('Valuation',`${c}26`,2028+t);
   F('Valuation',`${c}27`,`=${gr('dcf_start_growth')}+(${gr('terminal_growth')}-${gr('dcf_start_growth')})*${t}/9`);
   F('Valuation',`${c}28`,`=${t===0?"'Cash'!G18":p+'28'}*(1+${c}27)`);F('Valuation',`${c}29`,`=1/(1+${gr('cost_of_equity')})^${t+1}`);F('Valuation',`${c}30`,`=${c}28*${c}29`);
 }
 F('Valuation','E32',`=IF(${gr('cost_of_equity')}<=${gr('terminal_growth')},"Invalid discount rates",N28*(1+${gr('terminal_growth')})/(${gr('cost_of_equity')}-${gr('terminal_growth')}))`);
 F('Valuation','E33','=SUM(E30:N30)+E32*N29');
 const leg={E38:"=('Source'!E58*'Source'!E50+'Source'!E54)/'Source'!E55",E39:"=('Source'!E59*'Source'!E51+'Source'!E54)/'Source'!E55",E40:"='Source'!E60*'Source'!E52/'Source'!E55",E41:"='Source'!E60*'Source'!E53/'Source'!E55",E42:"=('Source'!E58*'Source'!F50+'Source'!F54)/'Source'!F55/(1+'Source'!E61)"};
 for(const [cell,formula] of Object.entries(leg))F('Valuation',cell,formula);
 for(let t=0;t<10;t++){const c=letters(4+t),p=letters(3+t);V('Valuation',`${c}49`,t+1);F('Valuation',`${c}50`,`='Source'!$E$62+('Source'!$E$63-'Source'!$E$62)*${t}/9`);F('Valuation',`${c}51`,`=${t===0?"'Source'!E51":p+'51'}*(1+${c}50)`);F('Valuation',`${c}52`,`=${c}51/(1+'Source'!$E$61)^${t+1}`);}
 F('Valuation','E54',"=SUM(E52:N52)+N51*(1+'Source'!E63)/('Source'!E61-'Source'!E63)/(1+'Source'!E61)^10");
 row('Valuation',49,'Legacy DCF period');row('Valuation',50,'Legacy FCF growth');row('Valuation',51,'Legacy FCF');row('Valuation',52,'Legacy discounted FCF');row('Valuation',54,'Legacy DCF enterprise value');
 sheets.Valuation.getRange('E26:N26').setNumberFormat('0');sheets.Valuation.getRange('E49:N49').setNumberFormat('0');
 F('Valuation','E43',"=(E54+'Source'!E54)/'Source'!E55");F('Valuation','E45','=AVERAGE(E38:E43)');
 for(const r of [14,17,18,19,20,21,23,38,39,40,41,42,43,45])sheets.Valuation.getRange(`E${r}`).setNumberFormat(money);
 sheets.Valuation.getRange('E27:N27').setNumberFormat(pct);sheets.Valuation.getRange('E50:N50').setNumberFormat(pct);
 V('Valuation','C57','New outputs use 31 Dec 2027 with FY27-end cash/shares. No interim cash is added separately.');
 V('Valuation','C58','Legacy labels used approximately Sep 2027 despite FY27-end cash/shares. Reproduction does not adopt that target.');
 V('Valuation','C59','DCF on FCF preserves the original model convention; it is not a newly underwritten unlevered enterprise DCF.');
 V('Valuation','C60','The six lenses share assumptions. Their mean is arithmetic, not six independent observations.');
 // Primary view links only completed financial results.
 V('Summary','C6','USD millions except per-share prices and share counts');
 ['FY:26','FY:27','FY:28'].forEach((y,i)=>V('Summary',`${letters(i+4)}7`,y));
 const summaryMetrics=[['Revenue','Costs',8],['Adjusted EBITDA','Costs',25],['Net income proxy','Costs',36],['Free cash flow','Cash',18],['SBC-adjusted FCF','Cash',20],['Ending net cash ex customer funds','Cash',28],['Ending diluted share proxy (m)','Cash',36],['Earnings per ending share proxy','Cash',37]];
 summaryMetrics.forEach(([label,sh,r],i)=>{row('Summary',8+i,label);for(let j=0;j<3;j++)F('Summary',`${letters(j+4)}${8+i}`,`='${sh}'!${letters(j+5)}${r}`);});
 row('Summary',18,'FY27 EV/EBITDA value per share');F('Summary','E18',"='Valuation'!E14");row('Summary',19,'FY27 six-lens arithmetic mean');F('Summary','E19',"='Valuation'!E23");
 row('Summary',20,'Q4:26 implied management guide (USD m)');F('Summary','E20',"='Revenue'!H20");
 sheets.Summary.getRange('E18:E19').setNumberFormat(money);sheets.Summary.getRange('E15:G15').setNumberFormat(money);
 V('Summary','C23','Valuation: 31 Dec 2027. Net cash excludes customer funds. Shares and earnings are proxies.');
 V('Summary','C24','Q2:27 onward and FY28 use inherited growth. L3 conversion and FX/RNPL inputs are separately pending.');
 V('Summary','C25','Scenario results are saved captures in Case comparison; use its refresh command after editing.');
 V('Summary','C26','No adopted direction, target, scenario probabilities or formal investment approval.');
 // Saved case results are a requested capture workflow; input changes visibly invalidate them.
 const metrics=[['Q4:26 guide (USD m)','Revenue','H20'],['FY26 revenue (USD m)','Costs','F8'],['FY27 revenue (USD m)','Costs','G8'],['FY27 EBITDA (USD m)','Costs','G25'],['FY27 net income (USD m)','Costs','G36'],['FY27 FCF (USD m)','Cash','G18'],['FY27 net cash (USD m)','Cash','G28'],['FY27 diluted shares (m)','Cash','G36'],['Enterprise value (USD m)','Valuation','E10'],['Equity value (USD m)','Valuation','E12'],['Value per share','Valuation','E14'],['Six-lens mean','Valuation','E23']];
 for(let ci=0;ci<7;ci++)V('Case comparison',`${letters(ci+4)}7`,data.cases[ci].label);
 sheets['Case comparison'].getRange('E7:K7').format={fill:navy,font:{bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:37,columnWidth:22};
 metrics.forEach(([label],i)=>row('Case comparison',i+8,label));
 V('Case comparison','C23','Captured results: selector → recalculate → read outputs → restore reference case.');
 V('Case comparison','C24','Refresh after edits: run build.mjs --refresh <saved.xlsx> --out <new-folder>.');
 V('Case comparison','C25','±1% cases perturb net after-hedge consolidated revenue. They are sensitivities, not measured FX/RNPL.');
 V('Case comparison','C26','K0 support-cost nights use the reference assumption; its revenue uses K0 GBV without an identified ADR.');
 V('Case comparison','C27','Sensitivity: Q3:26, Q4:26 and Q1:27; FY27 Q3/Q4 inherit changed bases. FY27 Q2 stays unchanged.');
 // Track all inputs except selector with per-cell comparisons; blank differs from zero.
 tracked=tracked.filter(([s,a])=>!(s==='Assumptions'&&a==='E4'));
 for(let i=0;i<tracked.length;i++){
   const r=35+i,[s,a]=tracked[i];V('Case comparison',`C${r}`,`${s}!${a}`);V('Case comparison',`E${r}`,sheets[s].getRange(a).values[0][0]);
   F('Case comparison',`F${r}`,`=IF(ISBLANK('${s}'!${a}),"__BLANK__",'${s}'!${a})`);
   F('Case comparison',`G${r}`,`=IF(ISBLANK(E${r}),IF(F${r}="__BLANK__",0,1),IF(E${r}=F${r},0,1))`);
 }
 F('Case comparison','E22',`=IF(SUM(G35:G${34+tracked.length})>0,"STALE: recapture all cases","Captured inputs unchanged")`);
 sheets['Case comparison'].getRange('E22:H22').conditionalFormats.add('containsText',{text:'STALE',format:{fill:'#FCE4D6',font:{color:'#B00020',bold:true}}});
 // Store non-business metadata for a reliable recapture of the exact single-build workflow.
 V('Case comparison','M1',JSON.stringify({tracked,metrics,caseCount:7}));
 for(const s of Object.keys(sheets)){
   if(s!=='Assumptions'){F(s,'E4',"='Assumptions'!G4");sheets[s].getRange('E4:H4').format.font.color=green;}
 }
 await capture(metrics);
 await verify(metrics);
 await finish();
}

async function capture(metrics){
 const prior=sheets.Assumptions.getRange('E4').values[0][0];
 for(let ci=0;ci<7;ci++){
   V('Assumptions','E4',ci+1);wb.recalculate();
   for(let mi=0;mi<metrics.length;mi++){
      const [,sh,a]=metrics[mi],val=sheets[sh].getRange(a).values[0][0];
      if(typeof val!=='number'||!Number.isFinite(val))throw Error(`Invalid case output ${ci+1}/${sh}!${a}: ${val}`);
      V('Case comparison',`${letters(ci+4)}${mi+8}`,val);
   }
 }
 for(let i=0;i<tracked.length;i++){const [s,a]=tracked[i];V('Case comparison',`E${35+i}`,sheets[s].getRange(a).values[0][0]);}
 V('Assumptions','E4',prior);wb.recalculate();
 sheets['Case comparison'].getRange('E18:K19').setNumberFormat(money);
}
async function verify(metrics){
 const diffs=[];
 for(let ci=0;ci<7;ci++){
  const c=data.cases[ci],a=c.annual,v=c.valuation;
  const expected=[c.quarters[3].guide,a[0].revenue,a[1].revenue,a[1].adj_ebitda,a[1].net_income,a[1].fcf,a[1].net_cash,a[1].shares,v.enterprise_value_musd,v.equity_value_musd,v.value_per_share,v.six_lens_mean];
  for(let mi=0;mi<metrics.length;mi++){const actual=sheets['Case comparison'].getRange(`${letters(ci+4)}${mi+8}`).values[0][0];const delta=actual-expected[mi];diffs.push({scenario:c.scenario,metric:metrics[mi][0],python:expected[mi],workbook:actual,delta});if(Math.abs(delta)>.001)throw Error(`Independent tie-out ${c.scenario}/${metrics[mi][0]} delta ${delta}`);}
 }
 for(const [cell,expected] of [['E38',180.876286],['E45',156.786845]])if(Math.abs(sheets.Valuation.getRange(cell).values[0][0]-expected)>.001)throw Error('Legacy workbook reproduction failed');
 // Input perturbation: booking timing, later costs, blank unselected case and valid zero.
 V('Assumptions','E4',1);wb.recalculate();
 const before={q3:sheets.Revenue.getRange('G18').values[0][0],q4:sheets.Revenue.getRange('H18').values[0][0],fy27:sheets.Costs.getRange('G25').values[0][0],actual:sheets.Revenue.getRange('E18').values[0][0]};
 const n=sheets.Assumptions.getRange('G11').values[0][0];V('Assumptions','G11',n+1);wb.recalculate();
 if(sheets.Revenue.getRange('G18').values[0][0]!==before.q3||sheets.Revenue.getRange('H18').values[0][0]===before.q4)throw Error('Quarter timing perturbation failed');
 if(sheets.Revenue.getRange('E18').values[0][0]!==before.actual)throw Error('Actuals moved');
 if(!sheets['Case comparison'].getRange('E22').values[0][0].startsWith('STALE'))throw Error('Capture stale detection failed');
 V('Assumptions','G11',n);
 const old=sheets.Assumptions.getRange(`G${annualRow.pd_cash}`).values[0][0];V('Assumptions',`G${annualRow.pd_cash}`,old+.01);wb.recalculate();
 if(sheets.Costs.getRange('G25').values[0][0]===before.fy27)throw Error('Later-period assumption does not update financial results');
 V('Assumptions',`G${annualRow.pd_cash}`,old);
 const unselected=sheets.Assumptions.getRange('G12').values[0][0];V('Assumptions','G12',null);wb.recalculate();
 if(sheets.Revenue.getRange('G8').values[0][0]!==n)throw Error('Unselected blank blocks active case');
 V('Assumptions','G12',unselected);
 V('Assumptions','G11',null);wb.recalculate();if(sheets.Revenue.getRange('G8').values[0][0]!=='Missing nights')throw Error('Selected missing nights are hidden');
 V('Assumptions','G11',n);
 V('Assumptions','G61',0);wb.recalculate();if(sheets.Revenue.getRange('G17').values[0][0]!==0)throw Error('Zero sensitivity not preserved');
 V('Assumptions','G61',null);wb.recalculate();if(sheets.Revenue.getRange('G17').values[0][0]!=='Unestimated')throw Error('Blank sensitivity is not pending');
 const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},maxChars:3000});
 await fs.writeFile(path.join(out,'formula_error_scan.ndjson'),errors.ndjson);
 await fs.writeFile(path.join(out,'workbook_tieout.json'),JSON.stringify({differences:diffs,max_abs_delta:Math.max(...diffs.map(d=>Math.abs(d.delta))),perturbation_checks:'passed'},null,2));
 const key=await wb.inspect({kind:'table',range:'Summary!C7:G20',include:'values,formulas',tableMaxRows:14,tableMaxCols:5,maxChars:8000});await fs.writeFile(path.join(out,'summary_inspection.ndjson'),key.ndjson);
}
async function finish(){
 wb.recalculate();
 const x=await SpreadsheetFile.exportXlsx(wb);const file=path.join(book,'ABNB_L4_review.xlsx');await x.save(file);
 await fs.writeFile(path.join(out,'workbook_path.txt'),file+'\n');
 console.log(JSON.stringify({workbook:file,sheets:8,status:data?'Recalculated, independently tied, input perturbations verified':'Recaptured seven cases and restored the selected case; original-input numerical tie-out is not applicable to edited inputs'}));
}
if(args[0]==='--refresh'){
 const inputFile=args[1],outIndex=args.indexOf('--out');if(outIndex<0)throw Error('Required --out <new-folder>');
 book=path.resolve(args[outIndex+1]);await fs.mkdir(book,{recursive:false});out=book;
 wb=await SpreadsheetFile.importXlsx(await FileBlob.load(inputFile));
 for(const s of ['Summary','Assumptions','Revenue','Costs','Cash','Valuation','Case comparison','Source'])sheets[s]=wb.worksheets.getItem(s);
 const meta=JSON.parse(sheets['Case comparison'].getRange('M1').values[0][0]);tracked=meta.tracked;
 await capture(meta.metrics);await finish();
}else{
 data=JSON.parse(await fs.readFile(args[0],'utf8'));out=data.data_dir;book=data.book_dir;
 await build();
}
