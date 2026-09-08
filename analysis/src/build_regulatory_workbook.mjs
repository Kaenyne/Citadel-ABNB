import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';

const root=process.cwd();
const input=path.join(root,'research/regulatory/quantification');
const out=path.join(root,'outputs/regulatory-20260905');
const qa=path.join(root,'data/raw/regulatory/quantification/workbook_build');
await fs.mkdir(out,{recursive:true});await fs.mkdir(qa,{recursive:true});
const read=async n=>JSON.parse(await fs.readFile(path.join(input,n),'utf8'));
const [markets,rules,observed,guidance,scenarios]=await Promise.all([
 read('market_inventory.json'),read('factor_exposures.json'),read('spain_supply_history.json'),
 read('guidance_history.json'),read('illustrative_scenarios.json')]);
const wb=Workbook.create();
const names=['Read me','Supply','Rules','Observed changes','Guidance','Scenarios'];
const sheets=Object.fromEntries(names.map(n=>[n,wb.worksheets.add(n)]));
const col=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const number='#,##0;(#,##0);0';
const money='$0.0;($0.0);$0.0';
function setup(sh,title,subtitle,headers,rows,widths,height=66){
 const end=col(headers.length),last=rows.length+6;
 sh.showGridLines=false;
 sh.getRange(`A1:${end}${last}`).format.font={name:'Arial',size:11,color:'#202020'};
 sh.getRange('A1').values=[[title]];
 sh.getRange(`A1:${end}1`).format.rowHeight=32;
 sh.getRange('A1').format.font={name:'Arial',size:14,bold:true};
 sh.getRange(`A1:${end}1`).format.borders={bottom:{style:'thin',color:'#8497A2'}};
 sh.getRange('A2').values=[[subtitle]];
 sh.getRange('A2').format.font={name:'Arial',size:11,italic:true};
 sh.getRange(`A6:${end}6`).values=[headers];
 sh.getRange(`A6:${end}6`).format={fill:'#283F50',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:46,verticalAlignment:'center'};
 if(rows.length){sh.getRange(`A7:${end}${last}`).values=rows;
  sh.getRange(`A7:${end}${last}`).format.wrapText=true;
  sh.getRange(`A7:${end}${last}`).format.verticalAlignment='top';
  sh.getRange(`A7:${end}${last}`).format.rowHeight=height;
  for(let r=7;r<=last;r++)if(r%2===0)sh.getRange(`A${r}:${end}${r}`).format.fill='#F1F4F6';}
 widths.forEach((w,i)=>sh.getRange(`${col(i+1)}1:${col(i+1)}${last}`).format.columnWidth=w);
 if(rows.length>10)sh.freezePanes.freezeRows(6);
 return last;
}
const notes=[
 ['Purpose','Quantify housing- and overtourism-related regulatory exposure for Airbnb. Research cutoff: 5 September 2026.'],
 ['Coverage','All 32 factors in the prior register, plus Lisbon insurance cleanup. 20 downloaded Airbnb market snapshots. Country denominators use official or attributed data when Airbnb totals are unavailable.'],
 ['What counts mean','Airbnb IDs, registered properties, tourist dwellings and removed advertisements are different units. They are labeled separately and must not be divided by mismatched denominators.'],
 ['Airbnb supply screen','Minimum nights below 30 identifies advertised short-stay eligibility. It does not prove a booking, legal compliance or primary-residence status. Ireland, BC and Greece use different statutory duration definitions.'],
 ['Geography','Lisbon, Porto, Maui and Thessaloniki are filtered to municipality/county. Legal subdistricts, parcels and licences still need matching. No England-wide or EU-wide Airbnb total was verified.'],
 ['Revenue mechanics','Gross fee loss = affected cohort × Airbnb channel share × unique productive share × lost nights × room ADR × fee rate × net scope/enforcement. Net loss subtracts revenue retained elsewhere on Airbnb.'],
 ['Caps and freezes','Night caps remove only nights above the new limit. Entry freezes affect the future supply pipeline and transfer attrition. They do not remove every current listing.'],
 ['Scenario meaning','Every unit-economics and behavioral driver is illustrative. Scenario outputs are annualized sensitivities, not investment forecasts or company disclosures. Alternative and overlapping rows must not be summed.'],
 ['Guidance conclusion','No jurisdiction-by-jurisdiction regulatory revenue or EBITDA bridge was found in the reviewed calls and filings. Known effects may be embedded in current booking trends. This is an inference, not management confirmation.'],
 ['Latest outlook','August 2026 guidance raised FY26 revenue growth to at least mid teens and adjusted EBITDA margin to at least 35.5%. Reported resilience does not identify the no-regulation counterfactual.'],
 ['Spain fine update','Q2 2026 filing reports a EUR70m surety bond to suspend fine enforcement. Potential loss remains neither probable nor estimable. Bond face value is not an expense or proof of a cash payment.'],
 ['Stock model treatment','Deduct only incremental losses absent from the baseline. Separate revenue, incremental contribution margin, compliance/legal spending and contingent one-off fines. Do not mechanically haircut consolidated EBITDA by the reported average margin.'],
 ['Next data purchase or pull','Obtain monthly Airbnb-only listing IDs, booked nights, realized ADR and revenue before/after each event, plus matched licences and exact policy boundaries. No paid dataset was purchased.'],
 ['Causal design','Use same-month comparisons and matched untreated destinations with pre-trend checks. Nearby destinations may receive displaced demand, making them poor untreated controls. Track cohort exits, new entry and platform recapture.'],
 ['Input colors','Blue numeric cells with pale yellow fill are editable scenario assumptions. Black formulas calculate on the same tab; green formulas link other tabs. Blank unknowns remain unknown.'],
 ['Primary financial sources','https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm'],
 ['Latest shareholder letter','https://www.sec.gov/Archives/edgar/data/1559720/000119312526337928/d70413dex991.htm'],
 ['Listing data attribution','Inside Airbnb, CC BY 4.0. Download URLs and snapshot dates appear in Supply. https://insideairbnb.com/get-the-data/'],
 ['Refinitiv and transcripts','Existing LSEG connection and downloaded news were reused. Fourteen quarterly transcripts are archived separately: 13 company-hosted PDFs and a public Q2 2026 fallback. LSEG transcript entries linked to EventsViewer rather than supplying full text.'],
];
setup(sheets['Read me'],'Airbnb regulatory exposure','First quantitative inventory and editable annualized sensitivities', ['Topic','Interpretation'],notes,[34,115],62);
setup(sheets.Supply,'Listing and registration counts','Snapshot dates vary. Units and geographic scope are not interchangeable.',
 ['Market','Total inventory','Short-stay listings','Short-stay entire homes','As of','Count unit','Scope and limitations','Source URL'],
 markets.map(m=>[m.market,m.total,m.short_minimum,m.short_entire,m.as_of,m.count_type,m.scope_note,m.source_url]),[28,17,20,24,15,45,75,80],76);
sheets.Supply.getRange(`B7:D${markets.length+6}`).setNumberFormat(number);
sheets.Supply.freezePanes.freezeColumns(1);
setup(sheets.Rules,'Inventory affected by each rule','A reported cohort is not necessarily the number of productive Airbnb listings lost.',
 ['Factor','Tier','Jurisdiction','Inventory','Inventory unit and date','Reported affected count','What the affected count means','Mechanism','Data still needed','Overlap group','Guidance assessment','Sources'],
 rules.map(r=>[r.factor_id,r.tier,r.jurisdiction,r.total_inventory,r.inventory_type+'; '+r.inventory_date,r.affected_reported_count,
  r.affected_count_definition,r.mechanism,r.next_data_needed,r.overlap_group,r.guidance_assessment,r.sources]),
 [19,9,44,17,47,20,90,40,92,27,70,120],130);
sheets.Rules.getRange(`D7:D${rules.length+6}`).setNumberFormat(number);
sheets.Rules.getRange(`F7:F${rules.length+6}`).setNumberFormat(number);
sheets.Rules.freezePanes.freezeColumns(1);
setup(sheets['Observed changes'],'Observed supply changes','Same-month INE comparisons across platforms. These changes do not identify causality.',
 ['Market','Prior May 2025','Current May 2026','Change in dwellings','Change %','Nov 2024','Nov 2025','Nov YoY %','Metric and interpretation','Source URL'],
 observed.map(s=>[s.market,s.prior,s.current,null,null,s.nov2024,s.nov2025,null,s.unit+'. '+s.inference,s.source_url]),
 [26,19,20,21,16,18,18,17,100,90],76);
for(let r=7;r<7+observed.length;r++){
 sheets['Observed changes'].getRange(`D${r}:E${r}`).formulas=[[`=C${r}-B${r}`,`=C${r}/B${r}-1`]];
 sheets['Observed changes'].getRange(`H${r}`).formulas=[[`=G${r}/F${r}-1`]];
}
sheets['Observed changes'].getRange('B7:D13').setNumberFormat(number);
sheets['Observed changes'].getRange('F7:G13').setNumberFormat(number);
sheets['Observed changes'].getRange('E7:E13').setNumberFormat('0.0%');
sheets['Observed changes'].getRange('H7:H13').setNumberFormat('0.0%');
const obsnotes=[
 ['NYC','AirDNA reported an 83% short-stay listing decline one year after enforcement. Nearby and longer-stay recapture are unquantified.','https://www.airdna.co/blog/nycs-short-term-rental-crackdown'],
 ['British Columbia','Government reported active STR listings declining from 28,000 to just over 23,000 by its June 2026 release. About 5,000 net decline; not a causal Airbnb-only loss.','https://archive.news.gov.bc.ca/releases/news_releases_2024-2028/2026HMA0028-000639.pdf'],
 ['Lisbon','City cancelled 6,765 registrations described as inactive. Match prior productive listings before attributing revenue.','https://informacao.lisboa.pt/en/news/detail/local-authority-cancels-40-of-inactive-local-accommodation-registrations'],
 ['Greece','ELSTAT 2025 lease days rose 4.7% nationally; Attiki rose 0.8%. Regions exceed regulated districts and include multiple platforms.','https://www.statistics.gr/documents/20181/9520c869-6216-4180-2282-d92150044d23']];
sheets['Observed changes'].getRange('A17').values=[['Other observed evidence']];
sheets['Observed changes'].getRange('I17:J21').values=[['Interpretation','Source URL'],...obsnotes.map(x=>[x[1],x[2]])];
sheets['Observed changes'].getRange('A18:A21').values=obsnotes.map(x=>[x[0]]);
sheets['Observed changes'].getRange('A17:J21').format.wrapText=true;
sheets['Observed changes'].getRange('A17:J21').format.rowHeight=75;
sheets['Observed changes'].getRange('A17:J17').format.fill='#DDE5EB';

setup(sheets.Guidance,'Revenue guidance and reported margins','USD millions. Quarterly margins are seasonal; consolidated results cannot isolate local regulation.',
 ['Quarter','Issued on call','Guide low','Guide high','Guide midpoint','Actual revenue','Beat / miss midpoint','Adjusted EBITDA','EBITDA margin','Policy context','Source URL'],
 guidance.map(g=>[g.guided_quarter,g.issued_on_call,g.guide_low_musd,g.guide_high_musd,null,g.actual_musd,null,
   g.adjusted_ebitda_musd,g.adj_ebitda_margin_pct===null?null:g.adj_ebitda_margin_pct/100,g.policy_context,g.source_url]),
 [17,19,17,17,19,20,21,20,20,100,90],74);
for(let r=7;r<7+guidance.length;r++){
 sheets.Guidance.getRange(`E${r}`).formulas=[[`=(C${r}+D${r})/2`]];
 sheets.Guidance.getRange(`G${r}`).formulas=[[`=IF(F${r}="","",F${r}/E${r}-1)`]];
 if(r<7+guidance.length-1)sheets.Guidance.getRange(`I${r}`).formulas=[[`=H${r}/F${r}`]];
}
sheets.Guidance.getRange('C7:F19').setNumberFormat(number);sheets.Guidance.getRange('H7:H19').setNumberFormat(number);
sheets.Guidance.getRange('G7:G19').setNumberFormat('0.0%');sheets.Guidance.getRange('I7:I19').setNumberFormat('0.0%');
sheets.Guidance.freezePanes.freezeColumns(1);
setup(sheets.Scenarios,'Annualized revenue sensitivities','Illustrative inputs. Alternative rows overlap. Do not sum these outputs or treat them as a forecast.',
 ['Scenario','Cohort count','Airbnb channel share','Unique productive share','Lost nights / listing','Room ADR, USD','Fee on room value','Revenue recapture','Contribution margin','Net scope / enforcement','Gross fee loss, $m','Net revenue loss, $m','EBITDA loss, $m','% FY25 revenue','Margin after loss','Margin change, bps','Timing and assumptions'],
 scenarios.map(s=>[s.scenario,s.cohort_count,s.airbnb_channel_share,s.unique_productive_share,s.lost_nights_per_productive_listing,
 s.room_adr_usd,s.fee_on_room_value,s.revenue_recapture,s.incremental_contribution_margin,s.net_scope_enforced_share,null,null,null,null,null,null,s.notes]),
 [39,19,19,21,20,20,20,20,20,23,22,24,23,21,23,24,115],100);
const sc=sheets.Scenarios;
sc.getRange('A4:D4').values=[['FY25 revenue, $m',12241,'FY25 adjusted EBITDA, $m',4297]];
sc.getRange('A4:D4').format.rowHeight=38;sc.getRange('A4:D4').format.wrapText=true;
sc.getRange('B4').setNumberFormat(number);sc.getRange('D4').setNumberFormat(number);
const modelnotes=[['Model detail','Definition'],
 ['Fee basis','15.5% of assumed room value is a scenario input informed by announced fee migration. Not the 13.2% revenue/GBV ratio, whose denominator includes fees and taxes.'],
 ['Costs','Contribution margin assumes variable-cost savings. No incremental legal/compliance spend or fine is included. EBITDA margin uses the smaller revenue denominator.'],
 ['Recapture','Share of lost fee revenue retained via other Airbnb homes, hotels, destinations or longer stays. Includes monetization differences; not just guest-count retention.']];
sc.getRange('A17:A20').values=modelnotes.map(x=>[x[0]]);sc.getRange('Q17:Q20').values=modelnotes.map(x=>[x[1]]);
sc.getRange('A17:Q20').format.wrapText=true;sc.getRange('A17:Q20').format.rowHeight=75;
sc.getRange('A22:A23').values=[['FY25 financial source'],['Fee migration source']];
sc.getRange('Q22:Q23').values=[['https://www.sec.gov/Archives/edgar/data/1559720/000119312526048670/d58192dex991.htm'],['https://www.sec.gov/Archives/edgar/data/1559720/000119312526337928/d70413dex991.htm']];
sc.getRange('A22:Q23').format.wrapText=true;sc.getRange('A22:Q23').format.rowHeight=50;
for(let r=7;r<7+scenarios.length;r++){
 sc.getRange(`K${r}:P${r}`).formulas=[[
  `=IF(COUNT(B${r}:J${r})<9,"",B${r}*C${r}*D${r}*E${r}*F${r}*G${r}*J${r}/1000000)`,
  `=IF(K${r}="","",K${r}*(1-H${r}))`,`=IF(L${r}="","",L${r}*I${r})`,
  `=IF(L${r}="","",L${r}/$B$4)`,`=IF(L${r}="","",($D$4-M${r})/($B$4-L${r}))`,
  `=IF(O${r}="","",(O${r}-$D$4/$B$4)*10000)`]];
}
sc.getRange('B7:J14').format.font={name:'Arial',size:11,color:'#0000FF'};
sc.getRange('B7:J14').format.fill='#FFF2CC';
for(const c of ['C','D','G','H','I','J','N','O'])sc.getRange(`${c}7:${c}14`).setNumberFormat('0.0%');
for(const c of ['B','E','F'])sc.getRange(`${c}7:${c}14`).setNumberFormat(number);
sc.getRange('K7:M14').setNumberFormat(money);sc.getRange('P7:P14').setNumberFormat('0.0');sc.getRange('N7:O14').setNumberFormat('0.00%');
for(const c of ['C','D','G','H','I','J'])sc.dataValidations.add({range:`${c}7:${c}14`,rule:{type:'decimal',operator:'between',formula1:0,formula2:1}});
sc.freezePanes.freezeRows(6);sc.freezePanes.freezeColumns(1);

// Representative calculations and missing/zero-input behavior.
const check=await wb.inspect({kind:'table',range:'Scenarios!K7:P14',include:'values,formulas',tableMaxRows:8,tableMaxCols:6,maxChars:4000});
await fs.writeFile(path.join(qa,'scenario_inspect.ndjson'),check.ndjson);
const actual=sc.getRange('L7').values[0][0];
if(Math.abs(actual-23.25)>1e-8)throw Error('Unit scenario revenue reconciliation failed: '+actual);
sc.getRange('H7').values=[[1]];
if(sc.getRange('L7').values[0][0]!==0)throw Error('Full recapture should give zero loss');
sc.getRange('H7').values=[[null]];
if(sc.getRange('L7').values[0][0]!==''&&sc.getRange('L7').values[0][0]!==null)throw Error('Missing driver did not gate output');
sc.getRange('H7').values=[[.5]];
for(let i=0;i<scenarios.length;i++){
 const v=sc.getRange(`L${i+7}`).values[0][0];if(Math.abs(v-scenarios[i].net_revenue_loss_musd)>1e-8)throw Error('Scenario mismatch '+i);
}
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},summary:'Formula error scan'});
await fs.writeFile(path.join(qa,'formula_scan.ndjson'),errors.ndjson);
console.log(errors.ndjson);
for(const n of names){
 const range=n==='Read me'?'A6:B12':n==='Scenarios'?'A6:F10':n==='Rules'?'A6:G10':n==='Guidance'?'A6:I12':n==='Supply'?'A6:F12':'A6:H13';
 const img=await wb.render({sheetName:n,range,scale:1.3,format:'png'});
 await fs.writeFile(path.join(qa,n.replaceAll(' ','_')+'.png'),new Uint8Array(await img.arrayBuffer()));
}
const img=await wb.render({sheetName:'Scenarios',range:'K6:P14',scale:1.3,format:'png'});
await fs.writeFile(path.join(qa,'Scenario_outputs.png'),new Uint8Array(await img.arrayBuffer()));
for(const [n,range,file] of [['Observed changes','I17:J21','Observed_notes'],['Scenarios','Q17:Q23','Scenario_notes']]){
 const blob=await wb.render({sheetName:n,range,scale:1.2,format:'png'});await fs.writeFile(path.join(qa,file+'.png'),new Uint8Array(await blob.arrayBuffer()));
}
const file=await SpreadsheetFile.exportXlsx(wb);
await file.save(path.join(out,'ABNB_regulatory_exposure.xlsx'));
console.log('Saved ABNB_regulatory_exposure.xlsx. Formula checks and scenario input checks completed.');
