import fs from 'node:fs/promises';
import path from 'node:path';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const [file,out]=process.argv.slice(2);
await fs.mkdir(out,{recursive:true});
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(file));
wb.recalculate();
const ranges=[['Summary','C2:J39'],['Case comparison','C2:M28'],['Valuation','C2:J23'],
 ['Assumptions','C88:L167'],['Revenue','C2:L32'],['Costs','C2:H39'],['Cash','C2:H41'],['Source','C2:J68']];
for(const [sheetName,range] of ranges){
 const blob=await wb.render({sheetName,range,scale:1,format:'png'});
 await fs.writeFile(path.join(out,sheetName.replaceAll(' ','_')+'.png'),new Uint8Array(await blob.arrayBuffer()));
 console.log(JSON.stringify({sheet:sheetName,range,status:'PNG written'}));
}
process.exit(0);
