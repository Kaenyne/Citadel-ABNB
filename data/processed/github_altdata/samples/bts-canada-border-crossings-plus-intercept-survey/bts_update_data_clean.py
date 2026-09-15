import pandas as pd
from pathlib import Path

script_dir = Path(__file__).parent

raw_path = script_dir.parent / 'data' / 'raw' / 'Border_Crossing_Entry_Data_20260728.csv'

processed_path = script_dir.parent / 'data' / 'processed' / 'bts_cleaned_20260728.csv' 

df = pd.read_csv(raw_path, dtype={'Port Code': str})

# Value arrives comma-formatted from the source export (e.g. '23,185')
df['Value'] = df['Value'].str.replace(',' , '') 

df['Value'] = df['Value'].astype(int)

# Source format switched between Mon-YY and YY-Mon across different
# BTS releases; normalize to Mon-YY for consistent date parsing
df['Date'] = df['Date'].str.replace(r'^(\d{2})-(\w{3})$', r'\2-\1', regex=True)

df.to_csv(processed_path, index=False)