"""Independent integration invariants, without creating a forecast combination."""
import csv
from pathlib import Path

STATUSES={'usable_as_observed_input','usable_as_conditional_scenario','descriptive_only',
          'comparator_only','unavailable','rejected'}
KEY=('package','quarter','metric','scenario')

def read(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def index(rows):
    out={}
    for r in rows:
        key=tuple(r[k] for k in KEY)
        if key in out:raise ValueError('Duplicate source semantic key: '+str(key))
        out[key]=r
    return out

def consumption(original,classified):
    source=index(original);matrix=index(classified)
    if set(source)!=set(matrix):raise ValueError('Consumption coverage differs from original bundle')
    counts={s:0 for s in sorted(STATUSES)}
    for key,old in source.items():
        new=matrix[key]
        if any(new.get(field)!=value for field,value in old.items()):
            raise ValueError('Original value/metadata lexeme changed: '+str(key))
        status=new.get('consumption_status')
        if status not in STATUSES:raise ValueError('Unknown consumption status')
        if old['value'].strip().lower() in {'','nan','null'} and status!='unavailable':
            raise ValueError('Unavailable numerical value promoted: '+str(key))
        if status=='usable_as_observed_input':
            evidence=old['evidence_status'].lower()
            if any(x in evidence for x in ['scenario_only','fullsample_descriptive','unidentified','conditional']):
                raise ValueError('Scenario or descriptive calibration promoted to observed input')
        counts[status]+=1
    return {'original_rows':len(source),'classified_rows':len(matrix),'all_original_fields_exact':True,
            'status_counts':counts}

