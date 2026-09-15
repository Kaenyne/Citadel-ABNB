import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {FileBlob, SpreadsheetFile} from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../../..');
const out=path.join(root,'data/processed/forecast_methods/lane4_model_v1');
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(root,'model/ABNB_driver_model.xlsx')));
const info=await wb.inspect({kind:'workbook,sheet',maxChars:6000,tableMaxRows:3,tableMaxCols:4});
await fs.writeFile(path.join(out,'source_workbook_inspection.ndjson'),info.ndjson);
console.log(info.ndjson);
for (const sheetName of ['Costs','Cash','Valuation']) {
 const x=await wb.inspect({kind:'table',range:`${sheetName}!A1:N18`,include:'values,formulas',maxChars:4000,tableMaxRows:18,tableMaxCols:14});
 await fs.writeFile(path.join(out,`source_${sheetName}.ndjson`),x.ndjson);
 const im=await wb.render({sheetName,range:'A1:N18',scale:1});
 await fs.writeFile(path.join(out,`source_${sheetName}.png`),new Uint8Array(await im.arrayBuffer()));
}
