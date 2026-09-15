import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const [file,sheetName,range,output]=process.argv.slice(2);
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(file));
wb.recalculate();
const blob=await wb.render({sheetName,range,scale:1,format:'png'});
await fs.writeFile(output,new Uint8Array(await blob.arrayBuffer()));
console.log(`Rendered ${sheetName}!${range}`);
process.exit(0);
