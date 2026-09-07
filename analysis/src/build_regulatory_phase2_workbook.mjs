import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root=process.cwd(),input=path.join(root,'research/regulatory/phase2');
const out=path.join(root,'outputs/regulatory-20260905'),qa=path.join(root,'data/raw/regulatory/quantification/workbook_build/phase2');
await fs.mkdir(qa,{recursive:true});
const read=async n=>JSON.parse(await fs.readFile(path.join(input,n),'utf8'));
const [b,m,parcels,monthly,ytd,reconciliation,scenarios,nyc]=await Promise.all(['barcelona_match_summary.json','maui_match_summary.json','maui_parcel_register.json','hawaii_monthly_latest.json','hawaii_ytd_vintages.json','hawaii_reconciliation.json','matched_cohort_scenarios.json','nyc_activity_benchmark.json'].map(read));
const wb=Workbook.create(),names=['Findings','Matched supply','Maui parcels','Hawaii performance','NYC benchmark','Sensitivities'];
const sh=Object.fromEntries(names.map(n=>[n,wb.worksheets.add(n)]));
const col=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
function table(s,title,subtitle,headers,rows,widths,height=55){
 const end=col(headers.length),last=rows.length+6;s.showGridLines=false;
 s.getRange(`A1:${end}${last}`).format.font={name:'Arial',size:11,color:'#202020'};
 s.getRange('A1').values=[[title]];s.getRange('A1').format.font={name:'Arial',size:14,bold:true};s.getRange('A1').format.rowHeight=30;
 s.getRange('A2').values=[[subtitle]];s.getRange('A2').format.font={name:'Arial',size:11,italic:true};
 s.getRange(`A6:${end}6`).values=[headers];s.getRange(`A6:${end}6`).format={fill:'#283F50',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:45,verticalAlignment:'center'};
 s.getRange(`A7:${end}${last}`).values=rows;s.getRange(`A7:${end}${last}`).format.wrapText=true;s.getRange(`A7:${end}${last}`).format.rowHeight=height;s.getRange(`A7:${end}${last}`).format.verticalAlignment='top';
 for(let r=7;r<=last;r++)if(r%2===0)s.getRange(`A${r}:${end}${r}`).format.fill='#F1F4F6';
 widths.forEach((w,i)=>s.getRange(`${col(i+1)}1:${col(i+1)}${last}`).format.columnWidth=w);
 s.freezePanes.freezeRows(6);return last;
}
const facts=[
 ['Barcelona','5,910 short-minimum entire-home ads match 5,146 unique six-digit HUTB registry identifiers. 4,823 of those identifiers have at least one reviewed listing in the past year. Registry matches are candidate exposure, not legal certification.'],
 ['Maui','4,350 short-minimum entire-home ads match 92 historical Minatoya parcels. They contain 3,862 distinct nonzero unit keys. Some listings give only a master parcel identifier.'],
 ['Maui exemptions','1,452 matched ads appear in the retrieved proposal union. These are incomplete/versioned proposal subsets. They are not enacted exemptions and cannot be subtracted as a forecast.'],
 ['Historical NYC evidence','An Airbnb-commissioned CRA report shows guest-nights falling 56.1% in the first post-LL18 year. The LL18 benchmark is a year-over-year comparison. It does not isolate consolidated fee revenue or external recapture.'],
 ['Hawaii data revision','Downloaded monthly vintages do not reconcile to July 2026 restated year-to-date demand. Use the same-report year-to-date comparison. Do not fit a causal model to the mixed-vintage monthly panel.'],
 ['Financial meaning','Use booked value of distinct affected inventory, then subtract revenue retained elsewhere on Airbnb. Multiply the net fee loss by incremental contribution margin. Keep compliance spending and one-off fines separate.'],
 ['Guidance','No city-level regulatory revenue/EBITDA bridge was found in the archived calls and filings. Known historical effects may be embedded in booking trends; this is an inference. Future Barcelona/Maui phase-outs do not justify a mechanical 2026 haircut.'],
 ['Spain mitigation spending','Airbnb announced a $50m rural-Spain commitment over three years in Nov 2025. An even $16.7m annual split is arithmetic, not expense guidance. Incrementality versus the existing budget is unknown.'],
 ['Sensitivity inputs','Count is derived from identifier matching. Annual room value, fee rate, recapture, retained legal scope and contribution margin are assumptions. Room value excludes fees and tax; do not substitute Hawaii total rate.'],
 ['Timing','Barcelona phase-out is scheduled for 2028. Maui is phased for 2029/2031. Sensitivities show steady-state annualized exposure after relevant deadlines and assume full legal scope before exemptions.'],
 ['Access','Refinitiv credentials work: refreshed Spain headlines and retrieved two additional stories. Some targeted queries returned 503. Fourteen transcripts remain archived. No listing-level transaction export was found.'],
 ['Data required','Monthly Airbnb-only listing IDs, property IDs, booked nights, realized room revenue, fees, cancellations, licence history and delisting dates, including vanished listings. Need legal-zone membership and destination recapture.'],
 ['Comparison workbook','This companion refines selected priority cohorts. The original workbook retains the complete 32-factor inventory and quarterly guidance history.'],
 ['Latest filing','https://www.sec.gov/Archives/edgar/data/1559720/000155972026000027/abnb-20260630.htm'],
 ['Spain commitment source','https://news.airbnb.com/es/compromiso-rural-una-apuesta-por-el-turismo-descentralizado-en-espana'],
];
table(sh.Findings,'Airbnb regulatory exposure: matched inventory','Research cutoff: 5 September 2026',['Topic','Finding and interpretation'],facts,[32,118],62);
const supply=[
 ['Barcelona','Entire-home listings, minimum under 30 nights',b.short_entire_listings,'Airbnb listing IDs','2026-06-24',b.source_url],
 ['Barcelona','Single six-digit HUTB registry match',b.short_entire_single_registry_matches,'Airbnb listing IDs','Self-reported licence only',b.source_url],
 ['Barcelona','Distinct matched HUTB identifiers',b.distinct_matched_licences,'Licence numbers','Not verified current legal units',b.source_url],
 ['Barcelona','Distinct matched licences with reviews in last year',b.distinct_matched_licences_with_review_ltm,'Licence numbers','Review activity is not booked revenue',b.source_url],
 ['Barcelona','Matched listings more than 300m from registry location',b.beyond_300m_listings,'Airbnb listing IDs','Analyst geographic sensitivity',b.source_url],
 ['Barcelona','Within-300m distinct matched licences',b.within_300m_distinct_licences,'Licence numbers','Coordinates are approximate',b.source_url],
 ['Barcelona','Unique HUTB IDs in downloaded registry',b.registry_unique_hutb,'Licence numbers','Does not reconcile to announced 10,101 licences',b.source_url],
 ['Maui','Historical apartment-district list',m.registry_units,'Condominium/property units','104 parcels; June 27 2024',m.source_url],
 ['Maui','Entire-home listings, minimum under 30 nights',m.short_entire_listings,'Airbnb listing IDs','2026-06-21',m.source_url],
 ['Maui','Listings with one matched parcel identifier',m.short_entire_matched_listings,'Airbnb listing IDs','92 of 104 historical parcels',m.source_url],
 ['Maui','Distinct nonzero unit identifiers',m.matched_unique_nonzero_unit_keys,'TMK unit identifiers','Some duplicates and incorrect identifiers remain possible',m.source_url],
 ['Maui','Distinct matched unit IDs with reviews in last year',m.matched_unique_unit_keys_with_review_ltm,'TMK unit identifiers','Review activity is not booked revenue',m.source_url],
 ['Maui','2029 phase: West Maui parcel screen',m.west_2029_matched_listings,'Airbnb listing IDs','Before unit-level exemptions',m.source_url],
 ['Maui','2031 phase: remaining parcel screen',m.other_2031_matched_listings,'Airbnb listing IDs','Before unit-level exemptions',m.source_url],
 ['Maui','Matched ads in retrieved proposal union',m.listings_in_retrieved_proposal_union,'Airbnb listing IDs','Incomplete proposals; not approved exemptions',m.source_url],
 ['Maui','Short-minimum entire-home ads without parsed TMK',m.short_entire_without_contiguous_tmk,'Airbnb listing IDs','Unmatched does not mean unaffected',m.source_url],
];
table(sh['Matched supply'],'Matched listing and property counts','Different count units must not be added or treated as equivalent',['Market','Measure','Count','Count unit','Qualification','Registry source'],supply,[18,57,16,27,67,85],56);
sh['Matched supply'].getRange('C7:C22').setNumberFormat('#,##0');
table(sh['Maui parcels'],'Historical Minatoya parcel register','Retrieved proposal versions identify candidates. They do not establish enacted exemptions.',
 ['Property','County parcel key','Listed units','Phase-out year','Proposal documents','Qualification'],parcels.map(p=>[p.property_name,p.parcel_key,p.listed_units,p.phase_out_year,p.proposal_documents,p.proposal_status]),[40,23,17,20,29,95],45);
const perf=monthly.filter(r=>r.market==='Maui County').sort((a,b)=>a.month.localeCompare(b.month));
table(sh['Hawaii performance'],'Maui rental-performance history','All channels. Mixed vintages below do not reconcile to restated 2026 YTD.',
 ['Month','Supply nights','Demand nights','Occupancy','Total rate USD','Demand × total rate USD m','Report vintage','Interpretation'],
 perf.map(r=>[r.month,r.supply_nights,r.demand_nights,r.occupancy,r.total_rate_usd,null,r.report_vintage,r.causal_use]),[18,21,21,18,21,26,20,89],42);
for(let r=7;r<7+perf.length;r++)sh['Hawaii performance'].getRange(`F${r}`).formulas=[[`=C${r}*E${r}/1000000`]];
sh['Hawaii performance'].getRange('B7:C37').setNumberFormat('#,##0');sh['Hawaii performance'].getRange('D7:D37').setNumberFormat('0.0%');sh['Hawaii performance'].getRange('E7:F37').setNumberFormat('0.00');
const y=ytd.filter(r=>r.market==='Maui County'&&r.report_vintage==='2026-07');
sh['Hawaii performance'].getRange('A41:H44').values=[['Same-report YTD','Supply nights','Demand nights','Occupancy','Total rate USD','Implied total-rate value USD m','Vintage','Use'],...y.map(r=>[r.month,r.supply_nights,r.demand_nights,r.occupancy,r.total_rate_usd,r.implied_total_rate_value_usd/1e6,r.report_vintage,'Preferred published comparison; not a causal estimate']),['Monthly reconciliation',null,reconciliation.find(r=>r.market==='Maui County').difference,null,null,null,null,'Monthly file sum minus restated YTD. Do not splice vintages.']];
sh['Hawaii performance'].getRange('A41:H44').format={wrapText:true,rowHeight:56,verticalAlignment:'top',font:{name:'Arial',size:11,color:'#202020'}};sh['Hawaii performance'].getRange('A41:H41').format={fill:'#283F50',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'}};
sh['Hawaii performance'].getRange('B42:C44').setNumberFormat('#,##0');sh['Hawaii performance'].getRange('D42:D43').setNumberFormat('0.0%');sh['Hawaii performance'].getRange('E42:F43').setNumberFormat('0.00');
sh['Hawaii performance'].getRange('A47').values=[['Source: https://files.hawaii.gov/dbedt/economic/tourism/vacation-rental/hawaii-vacation-rental-performance-2026-07.xlsx']];
table(sh['NYC benchmark'],'NYC activity after Local Law 18','Airbnb-commissioned CRA study dated December 20, 2024. PDF pages 9, 15–17.',
 ['Measure','Prior period','Post period','Change','Interpretation'],[
 ['Guest-nights stayed',6560000,2880000,null,'Sep 2022–Aug 2023 versus Sep 2023–Aug 2024. Counts people × nights; not booked listing-nights.'],
 ['Gross host earnings loss',null,351000000,null,'USD. Study estimate includes NYC direct taxes; not Airbnb fee revenue.'],
 ['Method',null,null,null,'LL18 comparison is YoY, not synthetic control. It cannot isolate causality or consolidation-level recapture.'],
 ['Recapture',null,null,null,'An observed citywide decline already incorporates retained activity within that measured city. Further recapture must be incremental and measured consistently.'],
 ['Source',null,null,null,nyc[0].source_url]], [35,23,23,21,100],64);
sh['NYC benchmark'].getRange('D7').formulas=[['=C7/B7-1']];sh['NYC benchmark'].getRange('B7:C8').setNumberFormat('#,##0');sh['NYC benchmark'].getRange('D7').setNumberFormat('0.0%');
table(sh.Sensitivities,'Annualized exposure sensitivities','Assumptions apply after phase-out. Alternatives within each cohort must not be summed.',
 ['Matched cohort','Distinct identifiers','Annual room value per ID USD','Fee rate','Recapture','Contribution margin','Net legal scope','Gross fee USD m','Net revenue loss USD m','EBITDA loss USD m','FY25 revenue share','FY25 margin loss bps'],
 scenarios.map(s=>[s.market,s.matched_identifiers,s.annual_room_value_per_identifier_usd,s.fee_rate,s.recapture,s.contribution_margin,s.retained_legal_scope_fraction,null,null,null,null,null]),[39,21,26,17,18,22,19,23,25,23,23,24],53);
const sc=sh.Sensitivities;
for(let r=7;r<25;r++)sc.getRange(`H${r}:L${r}`).formulas=[[
 `=IF(COUNT(B${r}:G${r})<6,"",B${r}*C${r}*D${r}*G${r}/1000000)`,
 `=IF(H${r}="","",H${r}*(1-E${r}))`,
 `=IF(I${r}="","",I${r}*F${r})`,
 `=IF(I${r}="","",I${r}/$B$28)`,
 `=IF(I${r}="","",($B$29/$B$28-($B$29-J${r})/($B$28-I${r}))*10000)`]];
sc.getRange('A28:B29').values=[['FY25 revenue USD m',12241],['FY25 adjusted EBITDA USD m',4297]];
sc.getRange('A31').values=[['Room value includes zero-production identifiers in the average. Fee rate, recapture, contribution and legal scope are assumptions.']];
sc.getRange('A32').values=[['Full scope is assumed before exemptions. Matched counts are an observed subset; omitted/misreported identifiers can change exposure.']];
sc.getRange('A33').values=[['FY25 denominator source: https://www.sec.gov/Archives/edgar/data/1559720/000119312526048670/d58192dex991.htm']];
sc.getRange('B7:C24').setNumberFormat('#,##0');sc.getRange('D7:G24').setNumberFormat('0.0%');sc.getRange('H7:J24').setNumberFormat('0.00');sc.getRange('K7:K24').setNumberFormat('0.00%');sc.getRange('L7:L24').setNumberFormat('0.0');
sc.getRange('C7:G24').format.font.color='#0000FF';sc.getRange('C7:G24').format.fill='#FFF2CC';
for(const c of ['D','E','F','G'])sc.dataValidations.add({range:`${c}7:${c}24`,rule:{type:'decimal',operator:'between',formula1:0,formula2:1}});
for(let i=0;i<scenarios.length;i++)if(Math.abs(sc.getRange(`I${i+7}`).values[0][0]-scenarios[i].net_revenue_loss_musd)>1e-8)throw Error('Scenario reconciliation '+i);
sc.getRange('E7').values=[[1]];if(sc.getRange('I7').values[0][0]!==0)throw Error('Full recapture check');
sc.getRange('E7').values=[[null]];if(!['',null].includes(sc.getRange('I7').values[0][0]))throw Error('Missing input check');sc.getRange('E7').values=[[.25]];
const scan=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:100},summary:'Formula error scan'});
await fs.writeFile(path.join(qa,'formula_scan.ndjson'),scan.ndjson);console.log(scan.ndjson);
for(const [name,range] of [['Findings','A6:B11'],['Matched supply','A6:E12'],['Maui parcels','A6:F10'],['Hawaii performance','A41:H44'],['NYC benchmark','A6:E11'],['Sensitivities','A6:G12'],['Sensitivities','H6:L12']]){
 const img=await wb.render({sheetName:name,range,scale:1.2,format:'png'});await fs.writeFile(path.join(qa,name.replaceAll(' ','_')+'_'+range.split(':')[0]+'.png'),new Uint8Array(await img.arrayBuffer()));
}
const file=await SpreadsheetFile.exportXlsx(wb);await file.save(path.join(out,'ABNB_regulatory_matched_cohorts.xlsx'));
console.log('Saved ABNB_regulatory_matched_cohorts.xlsx; formula and sensitivity checks completed.');
