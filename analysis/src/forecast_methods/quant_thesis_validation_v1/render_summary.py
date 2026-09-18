"""Render the reviewed one-page decision summary from explicit content JSON."""
from pathlib import Path
import argparse
import json
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[4]

def main(source,out):
    if out.exists(): raise FileExistsError(out)
    content=json.loads(source.read_text(encoding='utf-8-sig'))
    out.parent.mkdir(parents=True,exist_ok=True)
    navy=colors.HexColor('#17344d')
    styles={
        'title':ParagraphStyle('title',fontName='Helvetica-Bold',fontSize=18,leading=21,textColor=navy,spaceAfter=8),
        'subtitle':ParagraphStyle('subtitle',fontName='Helvetica',fontSize=9,leading=11,textColor=colors.HexColor('#596977'),spaceAfter=10),
        'body':ParagraphStyle('body',fontName='Helvetica',fontSize=10.3,leading=13.5,spaceAfter=8),
        'heading':ParagraphStyle('heading',fontName='Helvetica-Bold',fontSize=10.5,leading=13.5,textColor=navy,spaceBefore=6,spaceAfter=5),
        'cell':ParagraphStyle('cell',fontName='Helvetica',fontSize=9.2,leading=12),
        'source':ParagraphStyle('source',fontName='Helvetica',fontSize=7.8,leading=10,textColor=colors.HexColor('#53616f'),spaceAfter=4),
    }
    flow=[Paragraph(content['title'],styles['title']),Paragraph(content['subtitle'],styles['subtitle']),Paragraph(content['lead'],styles['body'])]
    if content.get('rows'):
        matrix=[[Paragraph(x,styles['cell']) for x in row] for row in content['rows']]
        table=Table(matrix,colWidths=[83,315,130],hAlign='LEFT')
        table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#edf2f5')),
                                  ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),6),
                                  ('RIGHTPADDING',(0,0),(-1,-1),6),('TOPPADDING',(0,0),(-1,-1),6),
                                  ('BOTTOMPADDING',(0,0),(-1,-1),6),
                                  ('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#b6c5cf')),
                                  ('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#dce3e8'))]))
        flow.extend([table,Spacer(1,7)])
    for section in content['sections']:
        flow.append(Paragraph(section['heading'],styles['heading']))
        flow.append(Paragraph(section['text'],styles['body']))
    flow.append(Spacer(1,3))
    flow.append(Paragraph(content['sources'],styles['source']))
    def footer(canvas,doc):
        canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#596977'))
        canvas.drawString(42,23,'ABNB independent validation | Frozen evidence; research use')
        canvas.drawRightString(570,23,str(doc.page))
    doc=SimpleDocTemplate(str(out),pagesize=letter,rightMargin=42,leftMargin=42,topMargin=35,bottomMargin=38,
                          title=content['title'],author='Independent quantitative validation',pageCompression=1)
    doc.build(flow,onFirstPage=footer,onLaterPages=footer)
    reader=PdfReader(str(out))
    if len(reader.pages)!=1: raise AssertionError(f'Expected one page, got {len(reader.pages)}; preserve and revise')
    text='\n'.join(page.extract_text() for page in reader.pages)
    if len(text)<1500: raise AssertionError('Unexpectedly little extracted summary text')
    print(json.dumps({'path':str(out),'pages':len(reader.pages),'extracted_characters':len(text)}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();main(a.source,a.out)
