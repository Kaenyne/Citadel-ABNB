"""Stage independently audited numerical evidence for artifact-tool authoring."""
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
BASE = ROOT / 'data/processed/forecast_methods/gbv_event_v1'
p = argparse.ArgumentParser()
p.add_argument('--events', default='run_v3')
a = p.parse_args()
out = ROOT / 'outputs/gbv-event-20260915'
out.mkdir(parents=True, exist_ok=True)
paths = {'model': BASE/'integration_v2/model.json',
         'scores': BASE/'forecast_v1/results_v1/frozen_scores.csv',
         'decomposition': BASE/'forecast_v1/results_v1/per_event_decomposition.csv',
         'variance': BASE/'forecast_v1/results_v1/variance_reconciliation.csv',
         'moments': BASE/'forecast_v1/results_v1/shapley_cross_moments.csv',
         'events': BASE/f'events_v1/{a.events}/event_panel.csv',
         'associations': BASE/f'events_v1/{a.events}/associations.csv',
         'early_origins': BASE/f'events_v1/{a.events}/pre_event_forecast_join.csv'}
data = {}
for k, f in paths.items():
    data[k] = json.loads(f.read_text()) if f.suffix == '.json' else json.loads(pd.read_csv(f).to_json(orient='records'))
data['manifest'] = [{'path': str(f.relative_to(ROOT)), 'sha256': hashlib.sha256(f.read_bytes()).hexdigest()} for f in paths.values()]
data['event_run'] = a.events
(out/'artifact_inputs.json').write_text(json.dumps(data, indent=2, allow_nan=False))
print(out/'artifact_inputs.json')
