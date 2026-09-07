"""Fetch public registry and performance inputs. Never sends project data or credentials."""
import concurrent.futures, hashlib, json
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'data/raw/regulatory/phase2'
RAW.mkdir(parents=True,exist_ok=True)
URLS={
 'barcelona_metadata.json':'https://opendata-ajuntament.barcelona.cat/data/api/3/action/package_show?id=habitatges-us-turistic',
 'maui_26129_metadata.json':'https://services1.arcgis.com/x4h61KaW16vFs7PM/ArcGIS/rest/services/maucotmk_2026_Reso26129/FeatureServer/0?f=json',
 'nyc_cra_2025.pdf':'https://news.airbnb.com/wp-content/uploads/sites/4/2025/05/The-Costs-of-STR-Restrictions.pdf',
 'maui_26110_cd1.pdf':'https://mauicounty.legistar.com/View.ashx?GUID=DBCD5114-742F-42ED-B617-96F81350B84E&ID=15655122&M=F',
 'maui_26111_cd1.pdf':'https://mauicounty.legistar.com/View.ashx?GUID=E6A46143-686C-4937-92B2-8248695FE385&ID=15655121&M=F',
 'barcelona_datastore.json':'https://opendata-ajuntament.barcelona.cat/data/api/3/action/datastore_search?resource_id=b32fa7f6-d464-403b-8a02-0292a64883bf&limit=20000',
 'maui_minatoya_mirror.pdf':'https://u.realgeeks.media/mauipropety/240725TVRList_WEB_202407252055590080.pdf',
 'barcelona_registry_current.csv':'https://opendata-ajuntament.barcelona.cat/data/dataset/c748799e-1079-44b1-9e60-88d936a3fe70/resource/b32fa7f6-d464-403b-8a02-0292a64883bf/download',
 'barcelona_registry_2026q1.zip':'https://opendata-ajuntament.barcelona.cat/data/dataset/c748799e-1079-44b1-9e60-88d936a3fe70/resource/297cf7da-2b43-4c83-91e2-210bfe5c33e9/download',
 'maui_minatoya.pdf':'https://www.mauicounty.gov/DocumentCenter/View/112945/Short-Term-Occupancy-List-as-of-03202024',
 'maui_26129_parcels.json':'https://services1.arcgis.com/x4h61KaW16vFs7PM/ArcGIS/rest/services/maucotmk_2026_Reso26129/FeatureServer/0/query?where=1%3D1&outFields=TMK_txt,cty_tmk,PROJECT_PR,MASTER_TMK,NumUnits,category,Reason,Unit_numbe,Non_Minato,Reso26129&returnGeometry=false&f=json',
 'hawaii_2026-07.pdf':'https://files.hawaii.gov/dbedt/economic/tourism/vacation-rental/hawaii-vacation-rental-performance-2026-07.pdf',
 'hawaii_2026-07.xlsx':'https://files.hawaii.gov/dbedt/economic/tourism/vacation-rental/hawaii-vacation-rental-performance-2026-07.xlsx',
 'hawaii_2025-12.xlsx':'https://files.hawaii.gov/dbedt/economic/tourism/vacation-rental/hawaii-vacation-rental-performance-2025-12.xlsx',
 'hawaii_2025-12.pdf':'https://files.hawaii.gov/dbedt/economic/tourism/vacation-rental/hawaii-vacation-rental-performance-2025-12.pdf',
 'maui_hlu.html':'https://mauicounty.us/hlu/',
}
for year,months in [(2025,range(1,13)),(2026,range(1,8))]:
 for month in months:
  stamp=f'{year}-{month:02d}'
  URLS[f'hawaii_{stamp}.xlsx']=f'https://files.hawaii.gov/dbedt/economic/tourism/vacation-rental/hawaii-vacation-rental-performance-{stamp}.xlsx'

def fetch(item):
 name,url=item;p=RAW/name
 try:
  if not p.exists():
   r=requests.get(url,timeout=50);r.raise_for_status();p.write_bytes(r.content)
  if p.suffix in ['.csv','.zip','.xlsx','.pdf'] and p.read_bytes()[:100].lower().find(b'<!doctype html')>=0:
   return dict(file=name,url=url,error='HTML bot-detection response, not a dataset')
  row=dict(file=name,url=url,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),retrieved='2026-09-05')
  print(name,row['bytes'],flush=True);return row
 except Exception as e:
  print(name,type(e).__name__,flush=True);return dict(file=name,url=url,error=type(e).__name__)

if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: rows=list(pool.map(fetch,URLS.items()))
 (RAW/'download_manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
