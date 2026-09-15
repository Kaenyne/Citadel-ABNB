import {Workbook} from '@oai/artifact-tool';
const wb=Workbook.create();
console.log(wb.help('ChartSeries', {include:'index,notes,examples', maxChars:6000}).ndjson);
