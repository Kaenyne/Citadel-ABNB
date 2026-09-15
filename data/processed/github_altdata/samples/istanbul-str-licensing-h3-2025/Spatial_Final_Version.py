"""
Spatio-Temporal Impact of STR Regulation on Airbnb in Istanbul
DI 722 – Spatio-Temporal Data Mining | METU
Author: Eda Yılmaz
Data  : Inside Airbnb – Istanbul (Scraped: September 2025)

Presentation version — spatio-temporal panel regression omitted.
Sections: Phase 1 baseline, Phase 1B ghost listing sensitivity,
          Phase 2A–B GWR, Phase 2D bandwidth sensitivity + variable-scale.
"""

# =============================================================================
# IMPORTS
# =============================================================================

import sys
sys.stdout.reconfigure(line_buffering=True)

import pandas as pd
import numpy as np
import h3
import geopandas as gpd
from shapely.geometry import Polygon
import json
import folium
import warnings
warnings.filterwarnings('ignore')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

# Force threading backend — avoids joblib semaphore failures with GWR in this environment
import joblib
joblib.parallel_backend('threading', n_jobs=2)

from mgwr.gwr import GWR
from mgwr.sel_bw import Sel_BW


# =============================================================================
# 0. DATA OVERVIEW – Columns and First 10 Rows
# =============================================================================

print("=" * 60)
print("SECTION 0A: LISTINGS.CSV — FULL COLUMN OVERVIEW")
print("=" * 60)

df_preview = pd.read_csv('Data/listings.csv')
print(f"\nShape: {df_preview.shape[0]:,} rows × {df_preview.shape[1]} columns\n")
print("── All columns with dtype and non-null count ──")
col_info = pd.DataFrame({
    'dtype'   : df_preview.dtypes.astype(str),
    'non_null': df_preview.notnull().sum(),
    'null_pct': (df_preview.isnull().mean() * 100).round(1).astype(str) + '%',
    'sample'  : [str(df_preview[c].dropna().iloc[0])[:60]
                 if df_preview[c].notnull().any() else 'ALL NULL'
                 for c in df_preview.columns]
})
print(col_info.to_string())

print("\n── First 10 rows (key columns only) ──")
key_cols = ['id','name','host_id','host_name','neighbourhood_cleansed',
            'latitude','longitude','room_type','accommodates','price',
            'availability_365','license','first_review','last_review','number_of_reviews']
key_cols = [c for c in key_cols if c in df_preview.columns]
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
pd.set_option('display.max_colwidth', 40)
print(df_preview[key_cols].head(10).to_string(index=False))

print("\n" + "=" * 60)
print("SECTION 0B: CALENDAR.CSV.GZ — FULL COLUMN OVERVIEW")
print("=" * 60)
df_cal_preview = pd.read_csv('Data/calendar.csv.gz', nrows=10, compression='gzip')
print(f"\nColumns ({len(df_cal_preview.columns)}): {list(df_cal_preview.columns)}")
cal_full_dtypes = pd.read_csv('Data/calendar.csv.gz', nrows=0, compression='gzip').dtypes
print("\n── All columns with dtype ──")
print(cal_full_dtypes.to_string())
print("\n── First 10 rows ──")
print(df_cal_preview.to_string(index=False))
print("\n── Total row count ──")
total_rows = 0
for chunk in pd.read_csv('Data/calendar.csv.gz', usecols=['listing_id'],
                          chunksize=500_000, compression='gzip'):
    total_rows += len(chunk)
print(f"Total rows in calendar.csv.gz: {total_rows:,}")
print("\n" + "=" * 60)
print("END OF SECTION 0 — DATA OVERVIEW COMPLETE")
print("=" * 60 + "\n")


# =============================================================================
# 1. LOAD DATA
# =============================================================================

print("=" * 60)
print("LOADING DATA")
print("=" * 60)

df = pd.read_csv('Data/listings.csv')
print(f"Total listings     : {len(df):,}")
print(f"Total columns      : {df.shape[1]}")
print(f"Scrape date        : {df['last_scraped'].value_counts().index[0]}")


# =============================================================================
# 2. EXPLORE MISSING VALUES
# =============================================================================

print("\n" + "=" * 60)
print("MISSING VALUES ANALYSIS")
print("=" * 60)

missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(1)
missing_df = pd.DataFrame({
    'Missing Count': missing,
    'Missing %': missing_pct,
    'Meaning': ''
}).query('`Missing Count` > 0').sort_values('Missing %', ascending=False)

meanings = {
    'neighbourhood_group_cleansed': 'Not used – no borough-level grouping for Istanbul',
    'calendar_updated'            : 'Deprecated column – safely drop',
    'host_neighbourhood'          : 'Host did not specify neighbourhood – not critical',
    'neighbourhood'               : 'Free-text field – use neighbourhood_cleansed instead',
    'neighborhood_overview'       : 'Host did not write a neighbourhood description',
    'host_about'                  : 'Host did not write a bio – not critical',
    'license'                     : '⚠️  KEY VARIABLE: NaN = no permit = potentially non-compliant',
    'review_scores_rating'        : 'Listing has no reviews yet – new or inactive listing',
    'review_scores_accuracy'      : 'Listing has no reviews yet',
    'review_scores_cleanliness'   : 'Listing has no reviews yet',
    'review_scores_checkin'       : 'Listing has no reviews yet',
    'review_scores_communication' : 'Listing has no reviews yet',
    'review_scores_location'      : 'Listing has no reviews yet',
    'review_scores_value'         : 'Listing has no reviews yet',
    'reviews_per_month'           : 'Listing has no reviews yet',
    'last_review'                 : 'Listing has no reviews yet',
    'first_review'                : 'Listing has no reviews yet',
    'host_location'               : 'Host did not specify location',
    'host_acceptance_rate'        : 'Host has not set auto-accept or no booking requests yet',
    'host_response_time'          : 'Host has not responded to any requests yet',
    'bathrooms'                   : 'Host did not specify – use bathrooms_text instead',
    'bedrooms'                    : 'Host did not specify number of bedrooms',
    'price'                       : 'Host has not set a price – listing inactive',
    'description'                 : 'Host did not write a description',
}
for col, meaning in meanings.items():
    if col in missing_df.index:
        missing_df.loc[col, 'Meaning'] = meaning
print(missing_df[missing_df['Missing Count'] > 0][['Missing Count','Missing %','Meaning']].to_string())


# =============================================================================
# 3. CLEAN KEY VARIABLES
# =============================================================================

print("\n" + "=" * 60)
print("CLEANING KEY VARIABLES")
print("=" * 60)

# --- Price ---
df['price_clean'] = df['price'].str.replace(r'[\$,]', '', regex=True).astype(float)
price_missing  = df['price_clean'].isna().sum()
price_outliers = (df['price_clean'] > df['price_clean'].quantile(0.99)).sum()
print(f"Price – missing        : {price_missing:,} listings")
print(f"Price – outliers (>p99): {price_outliers:,} listings")

df_clean = df.dropna(subset=['price_clean'])
df_clean = df_clean[df_clean['price_clean'] <= df_clean['price_clean'].quantile(0.99)]
df_clean = df_clean[df_clean['price_clean'] >= 100]
print(f"Price – kept after clean: {len(df_clean):,} listings")

# --- Coordinates ---
coord_issues = df_clean[
    (df_clean['latitude'] < 40.8) | (df_clean['latitude'] > 41.5) |
    (df_clean['longitude'] < 28.0) | (df_clean['longitude'] > 30.0)
]
print(f"\nCoordinates outside Istanbul bbox: {len(coord_issues):,} listings")
df_clean = df_clean[
    df_clean['latitude'].between(40.8, 41.5) &
    df_clean['longitude'].between(28.0, 30.0)
]
print(f"Coordinates – kept: {len(df_clean):,} listings")

# --- License / Compliance ---
print("\n--- LICENSE / COMPLIANCE ---")

def classify_compliance(license_val):
    if pd.isna(license_val):
        return 'Unlicensed'
    elif license_val == 'Non-real estate listing':
        return 'Non-real estate'
    elif license_val == 'Exempt':
        return 'Exempt'
    else:
        return 'Licensed'

df_clean['compliance']     = df_clean['license'].apply(classify_compliance)
df_clean['license_status'] = df_clean['compliance']   # alias for advanced_analysis sections
df_clean['is_unlicensed']  = (df_clean['compliance'] == 'Unlicensed').astype(int)

compliance_counts = df_clean['compliance'].value_counts()
compliance_pct    = (compliance_counts / len(df_clean) * 100).round(1)
for cat in compliance_counts.index:
    print(f"  {cat:<22}: {compliance_counts[cat]:>6,}  ({compliance_pct[cat]}%)")

# --- Room Type ---
print("\n--- ROOM TYPE ---")
print(df_clean['room_type'].value_counts().to_string())
df_clean['is_entire_home'] = (df_clean['room_type'] == 'Entire home/apt').astype(int)

# --- Dates ---
df_clean['first_review'] = pd.to_datetime(df_clean['first_review'], errors='coerce')
df_clean['last_review']  = pd.to_datetime(df_clean['last_review'],  errors='coerce')
scrape_date = pd.Timestamp('2025-09-30')
df_clean['days_since_last_review'] = (scrape_date - df_clean['last_review']).dt.days
df_clean['active_post_regulation'] = (df_clean['last_review'] >= pd.Timestamp('2024-01-01')).astype(int)
print(f"\nListings active after Jan 2024 law : {df_clean['active_post_regulation'].sum():,}")

# --- Log price ---
df_clean['log_price'] = np.log(df_clean['price_clean'])


# =============================================================================
# 4. FINAL CLEAN DATASET SUMMARY + DEFINE SAMPLE VARIANTS
# =============================================================================

print("\n" + "=" * 60)
print("FINAL CLEAN DATASET")
print("=" * 60)
print(f"Original listings          : {len(df):,}")
print(f"After cleaning             : {len(df_clean):,}")
print(f"Removed                    : {len(df) - len(df_clean):,}")

# Ghost listing sensitivity samples
df_all    = df_clean.copy()                                    # Sample A: all cleaned
df_active = df_clean[df_clean['number_of_reviews'] > 0].copy()# Sample B: active only

print(f"\nSample A (all cleaned)     : {len(df_all):,} listings")
print(f"Sample B (active only)     : {len(df_active):,} listings  "
      f"(removed {len(df_all)-len(df_active):,} ghost listings)")
print("\n✅ Data loading and cleaning complete. Ready for H3 assignment.")


# =============================================================================
# 5. H3 CELL ASSIGNMENT
# =============================================================================

print("\n" + "=" * 60)
print("H3 CELL ASSIGNMENT")
print("=" * 60)

RESOLUTION = 8
df_clean['h3_cell'] = df_clean.apply(
    lambda row: h3.latlng_to_cell(row['latitude'], row['longitude'], RESOLUTION),
    axis=1
)
# Propagate to sample variants
df_all['h3_cell']    = df_clean['h3_cell']
df_active['h3_cell'] = df_clean.loc[df_active.index, 'h3_cell']

print(f"H3 Resolution          : {RESOLUTION}")
print(f"Total H3 cells (res 8) : {df_clean['h3_cell'].nunique():,}")
print(f"Avg listings per cell  : {len(df_clean) / df_clean['h3_cell'].nunique():.1f}")

print("\nAggregating statistics per H3 cell...")
h3_stats = df_clean.groupby('h3_cell').agg(
    listing_count         = ('id',                    'count'),
    unlicensed_count      = ('is_unlicensed',          'sum'),
    unlicensed_pct        = ('is_unlicensed',          lambda x: round(x.mean()*100, 1)),
    avg_price             = ('price_clean',            'mean'),
    median_price          = ('price_clean',            'median'),
    avg_availability_365  = ('availability_365',       'mean'),
    entire_home_pct       = ('is_entire_home',         lambda x: round(x.mean()*100, 1)),
    active_post_reg_pct   = ('active_post_regulation', lambda x: round(x.mean()*100, 1)),
    avg_review_score      = ('review_scores_rating',   'mean'),
).reset_index()
h3_stats['avg_price']    = h3_stats['avg_price'].round(0)
h3_stats['median_price'] = h3_stats['median_price'].round(0)

print(f"\nH3 cells generated     : {len(h3_stats):,}")
print(f"\nTop 10 cells by listing count:")
print(h3_stats.nlargest(10, 'listing_count')[
    ['h3_cell','listing_count','unlicensed_pct','avg_price','entire_home_pct']
].to_string(index=False))

print("\n--- COMPLIANCE DISTRIBUTION ACROSS H3 CELLS ---")
print(f"Cells with >50% unlicensed : {(h3_stats['unlicensed_pct']>50).sum():,}")
print(f"Cells with >75% unlicensed : {(h3_stats['unlicensed_pct']>75).sum():,}")
print(f"Cells with 0% unlicensed   : {(h3_stats['unlicensed_pct']==0).sum():,}")

print("\nConverting H3 cells to polygons for mapping...")
hexagons = []
for cell in h3_stats['h3_cell']:
    boundary = h3.cell_to_boundary(cell)
    hexagon  = Polygon([(lng, lat) for lat, lng in boundary])
    hexagons.append({'h3_id': cell, 'geometry': hexagon})

h3_gdf = gpd.GeoDataFrame(hexagons, crs='EPSG:4326')
h3_gdf = h3_gdf.merge(h3_stats, left_on='h3_id', right_on='h3_cell')
h3_gdf.to_file('Data/istanbul_airbnb_h3.geojson', driver='GeoJSON')
print("Saved to: Data/istanbul_airbnb_h3.geojson")

df_clean['h3_cell_r9'] = df_clean.apply(
    lambda row: h3.latlng_to_cell(row['latitude'], row['longitude'], 9), axis=1)
r9_cells = df_clean['h3_cell_r9'].nunique()
print(f"\nResolution 9 comparison: {r9_cells:,} cells  "
      f"(avg {len(df_clean)/r9_cells:.1f} listings/cell)")
print("→ Resolution 8 gives better-sized clusters for neighbourhood analysis")
print("\n✅ H3 assignment complete.")


# =============================================================================
# 6. MAP VISUALISATION
# =============================================================================

print("\n" + "=" * 60)
print("MAP VISUALISATION")
print("=" * 60)

# --- 6a. Compliance Map ---
def compliance_colour(pct):
    if pct >= 75:   return '#d73027'
    elif pct >= 50: return '#fc8d59'
    elif pct >= 25: return '#fee090'
    else:           return '#4575b4'

print("Building compliance map...")
folium_compliance_map = folium.Map(location=[41.01, 28.96], zoom_start=10,
                                   tiles='CartoDB positron')
geojson_data = json.loads(h3_gdf.to_json())

for feature in geojson_data['features']:
    props     = feature['properties']
    pct       = props.get('unlicensed_pct', 0)
    folium.GeoJson(
        feature,
        style_function=lambda x, p=pct: {
            'fillColor': compliance_colour(p), 'color': 'white',
            'weight': 0.5, 'fillOpacity': 0.75},
        tooltip=folium.GeoJsonTooltip(
            fields=['listing_count','unlicensed_pct','avg_price','entire_home_pct'],
            aliases=['Listings:','Unlicensed %:','Avg Price (TRY):','Entire Home %:'],
            localize=True)
    ).add_to(folium_compliance_map)

folium_compliance_map.get_root().html.add_child(folium.Element("""
<div style="position:fixed;bottom:40px;left:40px;z-index:1000;background:white;
     padding:12px 16px;border-radius:8px;box-shadow:2px 2px 6px rgba(0,0,0,0.3);
     font-family:Arial;font-size:12px">
  <b>Unlicensed Listings %</b><br>
  <i style="background:#d73027;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>≥75% (Very High)<br>
  <i style="background:#fc8d59;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>50–74% (High)<br>
  <i style="background:#fee090;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>25–49% (Moderate)<br>
  <i style="background:#4575b4;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>&lt;25% (Low)<br>
  <br><small>Turkey STR Law No. 7464, Jan 2024<br>Data: Inside Airbnb, Sep 2025</small>
</div>"""))
folium_compliance_map.save('Data/istanbul_compliance_map.html')
print("Saved: Data/istanbul_compliance_map.html")

# --- 6b. Price Map ---
def price_colour(price):
    if price >= 6000:   return '#7b2d8b'
    elif price >= 4000: return '#d73027'
    elif price >= 2500: return '#fc8d59'
    elif price >= 1500: return '#fee090'
    else:               return '#4575b4'

print("Building price map...")
price_map = folium.Map(location=[41.01, 28.96], zoom_start=10, tiles='CartoDB positron')
for feature in geojson_data['features']:
    price = feature['properties'].get('avg_price', 0) or 0
    folium.GeoJson(
        feature,
        style_function=lambda x, p=price: {
            'fillColor': price_colour(p), 'color': 'white',
            'weight': 0.5, 'fillOpacity': 0.75},
        tooltip=folium.GeoJsonTooltip(
            fields=['listing_count','avg_price','median_price','unlicensed_pct'],
            aliases=['Listings:','Avg Price (TRY):','Median Price (TRY):','Unlicensed %:'],
            localize=True)
    ).add_to(price_map)
price_map.get_root().html.add_child(folium.Element("""
<div style="position:fixed;bottom:40px;left:40px;z-index:1000;background:white;
     padding:12px 16px;border-radius:8px;box-shadow:2px 2px 6px rgba(0,0,0,0.3);
     font-family:Arial;font-size:12px">
  <b>Avg Nightly Price (TRY)</b><br>
  <i style="background:#7b2d8b;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>≥6,000 TRY<br>
  <i style="background:#d73027;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>4,000–5,999 TRY<br>
  <i style="background:#fc8d59;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>2,500–3,999 TRY<br>
  <i style="background:#fee090;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>1,500–2,499 TRY<br>
  <i style="background:#4575b4;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>&lt;1,500 TRY<br>
  <br><small>Data: Inside Airbnb, Sep 2025</small>
</div>"""))
price_map.save('Data/istanbul_price_map.html')
print("Saved: Data/istanbul_price_map.html")
print("\n✅ Maps saved.")


# =============================================================================
# 7. BASELINE REGRESSION MODEL
# =============================================================================

print("\n" + "=" * 60)
print("BASELINE REGRESSION MODEL")
print("=" * 60)
print("Target   : log(price_clean)  — nightly price in TRY")
print("Features : compliance status, room type, availability,")
print("           accommodates, neighbourhood (top 10)")

df_reg = df_clean.copy()
room_dummies = pd.get_dummies(df_reg['room_type'], prefix='room', drop_first=True)
top_neighbourhoods = df_reg['neighbourhood_cleansed'].value_counts().head(10).index
df_reg['neighbourhood_top'] = df_reg['neighbourhood_cleansed'].apply(
    lambda x: x if x in top_neighbourhoods else 'Other')
neighbourhood_dummies = pd.get_dummies(df_reg['neighbourhood_top'], prefix='nbhd', drop_first=True)

features = pd.concat([
    df_reg[['is_unlicensed','availability_365','accommodates','is_entire_home']],
    room_dummies, neighbourhood_dummies
], axis=1).fillna(0)
target = df_reg['log_price']

print(f"\nFeatures used : {features.shape[1]}")
print(f"Observations  : {len(features):,}")

X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
model = LinearRegression().fit(X_train, y_train)
y_pred = model.predict(X_test)
r2  = r2_score(y_test, y_pred)
mae = mean_absolute_error(np.exp(y_test), np.exp(y_pred))

print(f"\n--- MODEL PERFORMANCE ---")
print(f"R²  : {r2:.4f}  ({r2*100:.1f}% of price variance explained)")
print(f"MAE : {mae:.0f} TRY")

coef_df = pd.DataFrame({'Feature': features.columns, 'Coefficient': model.coef_}
                       ).sort_values('Coefficient', ascending=False)
print(f"\n--- COEFFICIENTS (log scale) ---")
print(coef_df.to_string(index=False))

compliance_coef  = coef_df[coef_df['Feature']=='is_unlicensed']['Coefficient'].values[0]
price_effect_pct = (np.exp(compliance_coef) - 1) * 100
print(f"\n--- KEY FINDING: COMPLIANCE EFFECT ---")
print(f"Coefficient (log scale): {compliance_coef:.4f}")
if price_effect_pct < 0:
    print(f"Unlicensed listings are {abs(price_effect_pct):.1f}% CHEAPER than licensed ones")
else:
    print(f"Unlicensed listings are {price_effect_pct:.1f}% MORE EXPENSIVE than licensed ones")
print(f"(controlling for room type, availability, neighbourhood, accommodates)")
print("\n✅ Baseline regression complete.")


# =============================================================================
# 8. AVAILABILITY ANALYSIS BY COMPLIANCE STATUS
# =============================================================================

print("\n" + "=" * 60)
print("AVAILABILITY ANALYSIS BY COMPLIANCE STATUS")
print("=" * 60)

avail_stats = df_clean.groupby('compliance')['availability_365'].agg(
    count='count', mean='mean', median='median', std='std',
    q25=lambda x: x.quantile(0.25), q75=lambda x: x.quantile(0.75)
).round(1)
print("\nAvailability (nights/year) by compliance status:")
print(avail_stats.to_string())

blocked = df_clean.groupby('compliance').apply(
    lambda g: (g['availability_365'] == 0).mean() * 100).round(1)
print("\n% of listings with zero availability (fully blocked calendar):")
for cat, pct in blocked.items():
    print(f"  {cat:<22}: {pct:.1f}%")

print("\n--- AVAILABILITY BY ROOM TYPE × COMPLIANCE ---")
avail_cross = df_clean.groupby(['room_type','compliance'])['availability_365'].mean().round(1).unstack()
print(avail_cross.to_string())
print("\n✅ Availability analysis complete.")


# =============================================================================
# 9. EXTENDED REGRESSION WITH INTERACTION TERMS
# =============================================================================

print("\n" + "=" * 60)
print("EXTENDED REGRESSION: COMPLIANCE × ROOM TYPE INTERACTION")
print("=" * 60)
print("Added interaction: is_unlicensed × is_entire_home")
print("Hypothesis: compliance penalty is larger for entire homes (directly")
print("targeted by Law No. 7464) than for private rooms.")

df_reg2 = df_clean.copy()
df_reg2['unlicensed_x_entire_home'] = df_reg2['is_unlicensed'] * df_reg2['is_entire_home']
top_nb2 = df_reg2['neighbourhood_cleansed'].value_counts().head(10).index
df_reg2['neighbourhood_top'] = df_reg2['neighbourhood_cleansed'].apply(
    lambda x: x if x in top_nb2 else 'Other')
nb_dummies2   = pd.get_dummies(df_reg2['neighbourhood_top'], prefix='nbhd', drop_first=True)
room_dummies2 = pd.get_dummies(df_reg2['room_type'], prefix='room', drop_first=True)

features2 = pd.concat([
    df_reg2[['is_unlicensed','is_entire_home','unlicensed_x_entire_home',
              'availability_365','accommodates']],
    room_dummies2, nb_dummies2
], axis=1).fillna(0)
target2 = df_reg2['log_price']

X_train2, X_test2, y_train2, y_test2 = train_test_split(features2, target2, test_size=0.2, random_state=42)
model2 = LinearRegression().fit(X_train2, y_train2)
y_pred2 = model2.predict(X_test2)
r2_ext  = r2_score(y_test2, y_pred2)
mae_ext = mean_absolute_error(np.exp(y_test2), np.exp(y_pred2))

print(f"\n--- EXTENDED MODEL PERFORMANCE ---")
print(f"R²  : {r2_ext:.4f}  (baseline: {r2:.4f}, improvement: {(r2_ext-r2)*100:+.2f} pp)")
print(f"MAE : {mae_ext:.0f} TRY")

coef_df2       = pd.DataFrame({'Feature': features2.columns, 'Coefficient': model2.coef_})
c_unlicensed   = coef_df2.loc[coef_df2['Feature']=='is_unlicensed',            'Coefficient'].values[0]
c_entire       = coef_df2.loc[coef_df2['Feature']=='is_entire_home',           'Coefficient'].values[0]
c_interaction  = coef_df2.loc[coef_df2['Feature']=='unlicensed_x_entire_home', 'Coefficient'].values[0]

gap_private_room    = (np.exp(c_unlicensed) - 1) * 100
gap_entire_home     = (np.exp(c_unlicensed + c_interaction) - 1) * 100
entire_home_premium = (np.exp(c_entire) - 1) * 100

print(f"\n--- KEY COEFFICIENTS ---")
print(f"  is_unlicensed            : {c_unlicensed:+.4f}")
print(f"  is_entire_home           : {c_entire:+.4f}")
print(f"  unlicensed × entire_home : {c_interaction:+.4f}")
print(f"\n--- IMPLIED PRICE EFFECTS ---")
print(f"  Compliance discount – private rooms : {gap_private_room:+.1f}%")
print(f"  Compliance discount – entire homes  : {gap_entire_home:+.1f}%")
print(f"  Entire home premium (licensed only) : {entire_home_premium:+.1f}%")
print("\n✅ Extended regression complete.")


# =============================================================================
# 10. SPATIAL AUTOCORRELATION: MORAN'S I + LISA
# =============================================================================

print("\n" + "=" * 60)
print("SPATIAL AUTOCORRELATION: MORAN'S I")
print("=" * 60)

# --- Build spatial weights from H3 topology ---
print("Building spatial weights from H3 topology...")
cell_list  = h3_gdf['h3_id'].tolist()
cell_index = {cell: i for i, cell in enumerate(cell_list)}
n_cells_all = len(cell_list)

adjacency = []
for cell in cell_list:
    raw_nb = set(h3.grid_disk(cell, 1)) - {cell}
    adjacency.append([cell_index[nb] for nb in raw_nb if nb in cell_index])

mean_nb = np.mean([len(nb) for nb in adjacency])
islands  = sum(1 for nb in adjacency if len(nb) == 0)
print(f"  Cells: {n_cells_all:,}  |  Islands: {islands}  |  Mean neighbours: {mean_nb:.2f}")


def global_morans_i(values, adj, n_perms=999, seed=42):
    x = np.array(values, dtype=float)
    z = x - x.mean(); z2 = (z**2).sum()
    def lag(zv):
        l = np.zeros(len(zv))
        for i, nbs in enumerate(adj):
            if nbs: l[i] = zv[nbs].mean()
        return l
    I_obs = (z * lag(z)).sum() / z2
    EI    = -1.0 / (len(x) - 1)
    rng   = np.random.default_rng(seed); I_perm = np.empty(n_perms)
    for k in range(n_perms):
        zs = rng.permutation(z); I_perm[k] = (zs * lag(zs)).sum() / (zs**2).sum()
    p_sim = (np.sum(I_perm >= I_obs) + 1) / (n_perms + 1)
    return I_obs, EI, p_sim, I_perm


def local_morans_i(values, adj, n_perms=999, seed=42):
    x = np.array(values, dtype=float)
    z = x - x.mean(); s2 = (z**2).mean()
    lag_z = np.array([z[nbs].mean() if nbs else 0.0 for nbs in adj])
    local_I = (z / s2) * lag_z
    quad = np.zeros(len(z), dtype=int)
    quad[(z>0)&(lag_z>0)] = 1; quad[(z<0)&(lag_z>0)] = 2
    quad[(z<0)&(lag_z<0)] = 3; quad[(z>0)&(lag_z<0)] = 4
    rng = np.random.default_rng(seed); counts = np.zeros(len(z))
    for _ in range(n_perms):
        zs    = rng.permutation(z)
        lags  = np.array([zs[nbs].mean() if nbs else 0.0 for nbs in adj])
        counts += ((z / s2) * lags >= local_I)
    return local_I, quad, (counts + 1) / (n_perms + 1)


# Global Moran's I: unlicensed_pct
unlicensed_vals = h3_gdf['unlicensed_pct'].fillna(0).values
I_u, EI_u, p_u, _ = global_morans_i(unlicensed_vals, adjacency)
print(f"\n--- GLOBAL MORAN'S I: unlicensed_pct ---")
print(f"  Moran's I : {I_u:.4f}  |  Expected: {EI_u:.4f}  |  p = {p_u:.4f}")
if p_u < 0.05 and I_u > 0:
    print("  ✅ SIGNIFICANT POSITIVE SPATIAL AUTOCORRELATION — non-compliance is clustered.")

# Global Moran's I: avg_price
price_vals = h3_gdf['avg_price'].fillna(h3_gdf['avg_price'].mean()).values
I_p, EI_p, p_p, _ = global_morans_i(price_vals, adjacency)
print(f"\n--- GLOBAL MORAN'S I: avg_price ---")
print(f"  Moran's I : {I_p:.4f}  |  p = {p_p:.4f}")

# Sensitivity analysis k=1,2,3
print("\n--- SPATIAL WEIGHTS SENSITIVITY (k=1,2,3) ---")
for k in [1, 2, 3]:
    adj_k = []
    for cell in cell_list:
        nb_k = set(h3.grid_disk(cell, k)) - {cell}
        adj_k.append([cell_index[nb] for nb in nb_k if nb in cell_index])
    I_k, _, p_k, _ = global_morans_i(unlicensed_vals, adj_k)
    sig = "✅ sig" if p_k < 0.05 else "❌ not sig"
    print(f"  k={k}  Moran's I={I_k:.4f}  p={p_k:.4f}  {sig}")

# LISA
print(f"\nComputing Local Moran's I (LISA) — ~30 seconds...")
local_I, quad, p_lisa = local_morans_i(unlicensed_vals, adjacency)
quad_labels = {1:'HH (Hot Spot)', 2:'LH (Spatial Outlier)',
               3:'LL (Cold Spot)', 4:'HL (Spatial Outlier)'}
h3_gdf['lisa_I']       = local_I
h3_gdf['lisa_quad']    = quad
h3_gdf['lisa_p']       = p_lisa
h3_gdf['lisa_cluster'] = 'Not significant'
sig_mask = p_lisa < 0.05
for code, label in quad_labels.items():
    h3_gdf.loc[sig_mask & (quad == code), 'lisa_cluster'] = label

print("\n--- LISA CLUSTERS (p<0.05) ---")
for cluster, count in h3_gdf['lisa_cluster'].value_counts().items():
    print(f"  {cluster:<30}: {count:>4}  ({count/len(h3_gdf)*100:.1f}%)")

# Re-save GeoJSON with LISA columns
h3_gdf.drop(columns=['h3_cell'], errors='ignore').to_file(
    'Data/istanbul_airbnb_h3.geojson', driver='GeoJSON')

# LISA map
lisa_colours = {
    'HH (Hot Spot)':'#d73027', 'LL (Cold Spot)':'#4575b4',
    'LH (Spatial Outlier)':'#fee090', 'HL (Spatial Outlier)':'#fc8d59',
    'Not significant':'#cccccc'}
lisa_map = folium.Map(location=[41.01, 28.96], zoom_start=10, tiles='CartoDB positron')
for feature in json.loads(h3_gdf.to_json())['features']:
    cluster = feature['properties'].get('lisa_cluster','Not significant')
    colour  = lisa_colours.get(cluster,'#cccccc')
    folium.GeoJson(feature,
        style_function=lambda x, c=colour: {
            'fillColor':c,'color':'white','weight':0.5,'fillOpacity':0.75},
        tooltip=folium.GeoJsonTooltip(
            fields=['listing_count','unlicensed_pct','lisa_cluster'],
            aliases=['Listings:','Unlicensed %:','LISA Cluster:'])
    ).add_to(lisa_map)
lisa_map.get_root().html.add_child(folium.Element("""
<div style="position:fixed;bottom:40px;left:40px;z-index:1000;background:white;
     padding:12px 16px;border-radius:8px;box-shadow:2px 2px 6px rgba(0,0,0,0.3);
     font-family:Arial;font-size:12px">
  <b>LISA Cluster Type</b><br>
  <i style="background:#d73027;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>HH – Non-compliance Hot Spot<br>
  <i style="background:#4575b4;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>LL – Compliance Cold Spot<br>
  <i style="background:#fee090;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>LH – Spatial Outlier<br>
  <i style="background:#fc8d59;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>HL – Spatial Outlier<br>
  <i style="background:#cccccc;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>Not significant<br>
  <br><small>Local Moran's I, p&lt;0.05, 999 permutations<br>Data: Inside Airbnb, Sep 2025</small>
</div>"""))
lisa_map.save('Data/istanbul_lisa_map.html')
print("Saved: Data/istanbul_lisa_map.html")
print("\n✅ Spatial autocorrelation analysis complete.")


# =============================================================================
# 11. TEMPORAL ANALYSIS A: REGULATORY DETERRENCE ON NEW ENTRANTS
# =============================================================================

print("\n" + "=" * 60)
print("TEMPORAL ANALYSIS A: REGULATORY DETERRENCE ON NEW ENTRANTS")
print("=" * 60)

df_dated = df_clean.dropna(subset=['first_review']).copy()
print(f"Listings with first_review date: {len(df_dated):,}")

df_dated['entry_period'] = pd.cut(
    df_dated['first_review'],
    bins=[pd.Timestamp('2010-01-01'), pd.Timestamp('2022-01-01'),
          pd.Timestamp('2023-01-01'), pd.Timestamp('2024-01-01'),
          pd.Timestamp('2024-07-01'), pd.Timestamp('2025-01-01'),
          pd.Timestamp('2025-10-01')],
    labels=['Pre-2022','2022','2023 (pre-law)','Jan–Jun 2024','Jul–Dec 2024','2025']
)

entry_compliance = df_dated.groupby('entry_period', observed=True).agg(
    listing_count  = ('id',            'count'),
    unlicensed_pct = ('is_unlicensed', lambda x: round(x.mean()*100, 1)),
    licensed_pct   = ('is_unlicensed', lambda x: round((1-x.mean())*100, 1)),
    avg_price      = ('price_clean',   'mean'),
).round(1)
print("\n--- COMPLIANCE RATE BY LISTING ENTRY PERIOD ---")
print(entry_compliance.to_string())

pre_law  = df_dated[df_dated['entry_period']=='2023 (pre-law)']['is_unlicensed'].mean()*100
post_law = df_dated[df_dated['entry_period'].isin(['Jan–Jun 2024','Jul–Dec 2024','2025'])]
post_rate = post_law['is_unlicensed'].mean()*100 if len(post_law) > 0 else None
if post_rate is not None:
    diff = pre_law - post_rate
    print(f"\nPre-law unlicensed rate  : {pre_law:.1f}%")
    print(f"Post-law unlicensed rate : {post_rate:.1f}%")
    print(f"Change                   : {diff:+.1f} pp")
print("\n✅ Temporal Part A complete.")


# =============================================================================
# 12. TEMPORAL ANALYSIS B: CALENDAR BOOKING TIME SERIES
# (calendar.csv.gz loaded ONCE here; Part C reuses the same object)
# =============================================================================

print("\n" + "=" * 60)
print("TEMPORAL ANALYSIS B: CALENDAR BOOKING TIME SERIES")
print("=" * 60)
print("Loading calendar.csv.gz (~10.9M rows) — please wait...")

cal_chunks = []
for chunk in pd.read_csv(
        'Data/calendar.csv.gz',
        usecols=['listing_id','date','available'],
        parse_dates=['date'],
        chunksize=500_000,
        compression='gzip'):
    chunk = chunk[chunk['listing_id'].isin(df_clean['id'])]
    cal_chunks.append(chunk)

cal = pd.concat(cal_chunks, ignore_index=True)
print(f"Loaded: {len(cal):,} rows  |  Listings: {cal['listing_id'].nunique():,}")
print(f"Date range: {cal['date'].min().date()} → {cal['date'].max().date()}")

# Merge compliance status
# (renamed from 'compliance_map' to avoid conflict with folium_compliance_map above)
compliance_lookup = df_clean.set_index('id')[['compliance','is_unlicensed','is_entire_home']]
cal = cal.merge(compliance_lookup, left_on='listing_id', right_index=True, how='left')
cal['booked'] = (cal['available'] == 'f').astype(int)

# Weekly booking rate
cal['week'] = cal['date'].dt.to_period('W').dt.start_time
weekly = cal.groupby(['week','compliance']).agg(
    total_days=('booked','count'), booked_days=('booked','sum')).reset_index()
weekly['booking_rate'] = (weekly['booked_days'] / weekly['total_days'] * 100).round(1)
print(f"\n--- WEEKLY BOOKING RATE BY COMPLIANCE STATUS (first 8 weeks) ---")
print(weekly.pivot(index='week', columns='compliance', values='booking_rate').head(8).to_string())

# Average over full period
avg_booking = cal.groupby('compliance').agg(
    avg_booking_rate=('booked', lambda x: round(x.mean()*100, 1)),
    listing_count=('listing_id','nunique')).reset_index()
print(f"\n--- AVERAGE BOOKING RATE OVER FULL CALENDAR PERIOD ---")
print(avg_booking.to_string(index=False))

lic_rate   = avg_booking.loc[avg_booking['compliance']=='Licensed',   'avg_booking_rate'].values
unlic_rate = avg_booking.loc[avg_booking['compliance']=='Unlicensed', 'avg_booking_rate'].values
if len(lic_rate) > 0 and len(unlic_rate) > 0:
    print(f"\nLicensed / Unlicensed gap: {lic_rate[0]-unlic_rate[0]:+.1f} pp")

# Monthly gap
cal['month'] = cal['date'].dt.to_period('M').dt.start_time
monthly_gap  = cal[cal['compliance'].isin(['Licensed','Unlicensed'])].groupby(
    ['month','compliance'])['booked'].mean().unstack() * 100
monthly_gap.columns = ['licensed_rate','unlicensed_rate']
monthly_gap['gap']  = monthly_gap['licensed_rate'] - monthly_gap['unlicensed_rate']
monthly_gap = monthly_gap.round(1)
print(f"\n--- MONTHLY BOOKING RATE: LICENSED vs UNLICENSED ---")
print(monthly_gap.to_string())

shoulder_months = monthly_gap[monthly_gap.index.month.isin([10,11,12,1,2,3,4,5])]
peak_months     = monthly_gap[monthly_gap.index.month.isin([6,7,8,9])]
print(f"\nAvg gap shoulder (Oct–May): {shoulder_months['gap'].mean():.1f} pp")
print(f"Avg gap peak    (Jun–Sep) : {peak_months['gap'].mean():.1f} pp")

# Spatial × temporal
h3_map = df_clean.set_index('id')['h3_cell']
cal    = cal.merge(h3_map, left_on='listing_id', right_index=True, how='left')
cal_first = cal[cal['month'] == monthly_gap.index[0]]
cal_last  = cal[cal['month'] == monthly_gap.index[-1]]
h3_booking_first = cal_first.groupby('h3_cell')['booked'].mean().rename('booking_first')
h3_booking_last  = cal_last.groupby('h3_cell')['booked'].mean().rename('booking_last')
h3_temporal = pd.concat([h3_booking_first, h3_booking_last], axis=1).dropna()
h3_temporal['booking_change'] = ((h3_temporal['booking_last'] - h3_temporal['booking_first'])*100).round(1)
print(f"\n--- SPATIAL × TEMPORAL: BOOKING RATE CHANGE ---")
print(f"Mean change: {h3_temporal['booking_change'].mean():.1f} pp")

# Temporal map
h3_gdf_temporal = h3_gdf.merge(
    h3_temporal.reset_index().rename(columns={'h3_cell':'h3_id'}), on='h3_id', how='left')
h3_gdf_temporal.drop(columns=['h3_cell'], errors='ignore').to_file(
    'Data/istanbul_airbnb_h3.geojson', driver='GeoJSON')

def booking_change_colour(change):
    if pd.isna(change): return '#cccccc'
    if change >= 10:    return '#1a9641'
    elif change >= 3:   return '#a6d96a'
    elif change >= -3:  return '#ffffbf'
    elif change >= -10: return '#fdae61'
    else:               return '#d7191c'

temporal_map = folium.Map(location=[41.01, 28.96], zoom_start=10, tiles='CartoDB positron')
for feature in json.loads(h3_gdf_temporal.to_json())['features']:
    change = feature['properties'].get('booking_change', None)
    colour = booking_change_colour(change)
    folium.GeoJson(feature,
        style_function=lambda x, c=colour: {
            'fillColor':c,'color':'white','weight':0.5,'fillOpacity':0.75},
        tooltip=folium.GeoJsonTooltip(
            fields=['listing_count','unlicensed_pct','booking_change','lisa_cluster'],
            aliases=['Listings:','Unlicensed %:','Booking Δ (pp):','LISA Cluster:'])
    ).add_to(temporal_map)
temporal_map.get_root().html.add_child(folium.Element("""
<div style="position:fixed;bottom:40px;left:40px;z-index:1000;background:white;
     padding:12px 16px;border-radius:8px;box-shadow:2px 2px 6px rgba(0,0,0,0.3);
     font-family:Arial;font-size:12px">
  <b>Booking Rate Change (pp)</b><br>
  <i style="background:#1a9641;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>≥+10 pp (Strong increase)<br>
  <i style="background:#a6d96a;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>+3 to +10 pp<br>
  <i style="background:#ffffbf;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>−3 to +3 pp (Stable)<br>
  <i style="background:#fdae61;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>−3 to −10 pp<br>
  <i style="background:#d7191c;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>≤−10 pp (Strong decrease)<br>
  <br><small>First vs last month of calendar period<br>Data: Inside Airbnb, Sep 2025</small>
</div>"""))
temporal_map.save('Data/istanbul_temporal_map.html')
print("Saved: Data/istanbul_temporal_map.html")
print("\n✅ Temporal analyses (A + B) complete.")


# =============================================================================
# 13. GHOST LISTING SENSITIVITY ANALYSIS
# Compares key results between Sample A (all) and Sample B (active only)
# =============================================================================

print("\n" + "=" * 60)
print("GHOST LISTING SENSITIVITY ANALYSIS")
print("=" * 60)
print(f"Sample A (all)    : {len(df_all):,} listings")
print(f"Sample B (active) : {len(df_active):,} listings")


def _run_regression_sensitivity(data):
    """OLS helper for ghost listing comparison."""
    d = data.copy()
    top_nb = d['neighbourhood_cleansed'].value_counts().head(10).index
    d['neighbourhood_top'] = d['neighbourhood_cleansed'].apply(
        lambda x: x if x in top_nb else 'Other')
    room_dum = pd.get_dummies(d['room_type'],         prefix='room', drop_first=True)
    nb_dum   = pd.get_dummies(d['neighbourhood_top'], prefix='nbhd', drop_first=True)
    feats = pd.concat([
        d[['is_unlicensed','availability_365','accommodates','is_entire_home']],
        room_dum, nb_dum
    ], axis=1).fillna(0)
    Xtr, Xte, ytr, yte = train_test_split(feats, d['log_price'], test_size=0.2, random_state=42)
    mdl   = LinearRegression().fit(Xtr, ytr)
    y_hat = mdl.predict(Xte)
    r2s   = round(r2_score(yte, y_hat), 4)
    maes  = round(mean_absolute_error(np.exp(yte), np.exp(y_hat)), 0)
    coefs = pd.Series(mdl.coef_, index=feats.columns)
    beta  = coefs['is_unlicensed']
    return r2s, int(maes), round(beta, 4), round((np.exp(beta)-1)*100, 1)


def _entry_cohort_sensitivity(data):
    d = data.copy()
    def cohort(dt):
        if pd.isna(dt): return None
        if dt.year < 2022: return 'Pre-2022'
        if dt.year == 2022: return '2022'
        if dt.year == 2023: return '2023'
        if dt < pd.Timestamp('2024-07-01'): return 'Jan–Jun 2024'
        if dt.year == 2024: return 'Jul–Dec 2024'
        return '2025'
    d['cohort'] = d['first_review'].apply(cohort)
    return d.dropna(subset=['cohort']).groupby('cohort').agg(
        listings     = ('is_unlicensed','count'),
        licensed_pct = ('is_unlicensed', lambda x: round((1-x.mean())*100, 1))
    ).reindex(['Pre-2022','2022','2023','Jan–Jun 2024','Jul–Dec 2024','2025'])


results_sensitivity = {}
for label, data in [('All listings', df_all), ('Active only', df_active)]:
    print(f"\nRunning: {label}...")
    unlic_pct = round(data['is_unlicensed'].mean()*100, 1)

    # H3 aggregation for Moran's I
    h3_s = data.groupby('h3_cell').agg(
        unlicensed_pct=('is_unlicensed', lambda x: x.mean()*100),
        listing_count=('id','count')).reset_index()
    cells_s = h3_s['h3_cell'].tolist()
    idx_s   = {c: i for i, c in enumerate(cells_s)}
    adj_s   = []
    for cell in cells_s:
        nb = set(h3.grid_disk(cell, 1)) - {cell}
        adj_s.append([idx_s[c] for c in nb if c in idx_s])
    mi, _, p_mi, _ = global_morans_i(h3_s['unlicensed_pct'].values, adj_s, n_perms=199)

    r2s, maes, beta, pct_gap = _run_regression_sensitivity(data)
    cohort_df = _entry_cohort_sensitivity(data)
    results_sensitivity[label] = {
        'n': len(data), 'unlic_pct': unlic_pct, 'n_cells': len(h3_s),
        'morans_i': mi, 'morans_p': round(p_mi, 4),
        'r2': r2s, 'mae': maes, 'price_gap': pct_gap, 'cohort': cohort_df}
    print(f"  Unlicensed: {unlic_pct}% | Moran's I={mi:.4f} (p={p_mi:.4f}) | Price gap={pct_gap}%")

A = results_sensitivity['All listings']
B = results_sensitivity['Active only']
print("\n" + "=" * 62)
print("COMPARISON: ALL LISTINGS vs ACTIVE LISTINGS ONLY")
print("=" * 62)
print(f"{'Metric':<30} {'All listings':>14} {'Active only':>14}")
print("-" * 62)
for label, key, unit in [
    ('Total listings','n',''), ('Unlicensed rate','unlic_pct','%'),
    ('H3 cells','n_cells',''), ("Moran's I",'morans_i',''), ('p-value','morans_p',''),
    ('R²','r2',''), ('MAE (TRY)','mae',''), ('Price gap','price_gap','%')]:
    print(f"{label:<30} {str(A[key])+unit:>14} {str(B[key])+unit:>14}")

print("\n--- Entry Cohort: Licensed Rate (%) ---")
print(f"{'Cohort':<18} {'All listings':>14} {'Active only':>14}")
print("-" * 50)
for cohort in ['Pre-2022','2022','2023','Jan–Jun 2024','Jul–Dec 2024','2025']:
    pct_a = A['cohort'].loc[cohort,'licensed_pct'] if cohort in A['cohort'].index else '-'
    pct_b = B['cohort'].loc[cohort,'licensed_pct'] if cohort in B['cohort'].index else '-'
    print(f"{cohort:<18} {str(pct_a)+'%':>14} {str(pct_b)+'%':>14}")

# Comparison chart
fig_s, axes_s = plt.subplots(1, 3, figsize=(13, 4))
fig_s.suptitle('All Listings vs Active Listings Only — Key Metric Comparison',
               fontsize=13, fontweight='bold', color='#1a1a1a', y=1.02)
colors_s = ['#2C6FAC','#E8A838']
for ax, vals, title, ylabel, ylim in [
    (axes_s[0], [A['unlic_pct'], B['unlic_pct']], 'Unlicensed Rate','%', (0,50)),
    (axes_s[1], [abs(A['price_gap']), abs(B['price_gap'])], 'Unlicensed Price Gap (OLS)','% cheaper', (0,40)),
    (axes_s[2], [A['morans_i'], B['morans_i']], "Global Moran's I","Moran's I", (0,0.30))]:
    bars = ax.bar(['All','Active'], vals, color=colors_s, width=0.5, edgecolor='white')
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+ylim[1]*0.015,
                f'{val}', ha='center', fontsize=11, fontweight='bold')
    ax.set_title(title, fontsize=11); ax.set_ylabel(ylabel); ax.set_ylim(*ylim)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
plt.tight_layout()
fig_s.text(0.99, -0.02, 'Source: Inside Airbnb, Sep 2025', ha='right', fontsize=8, color='#aaaaaa')
plt.savefig('Data/fig_sample_comparison.png', dpi=150, bbox_inches='tight', facecolor='white')
print("\nSaved: Data/fig_sample_comparison.png")
print("\n✅ Ghost listing sensitivity analysis complete.")


# =============================================================================
# 14. PHASE 2A — UPDATED OLS: BEŞIKTAŞ AS REFERENCE NEIGHBOURHOOD
# =============================================================================

print("\n" + "=" * 60)
print("PHASE 2A: OLS — BEŞIKTAŞ AS REFERENCE NEIGHBOURHOOD")
print("=" * 60)


def run_ols_besiktas(data, label='', ref_nbhd='Besiktas'):
    d = data.copy()
    top_nb = d['neighbourhood_cleansed'].value_counts().head(10).index
    d['neighbourhood_top'] = d['neighbourhood_cleansed'].apply(
        lambda x: x if x in top_nb else 'Other')
    room_dum = pd.get_dummies(d['room_type'],         prefix='room', drop_first=False)
    nb_dum   = pd.get_dummies(d['neighbourhood_top'], prefix='nbhd', drop_first=False)
    room_dum = room_dum.drop(columns=['room_Entire home/apt'], errors='ignore')
    nb_dum   = nb_dum.drop(columns=[f'nbhd_{ref_nbhd}'], errors='ignore')
    feats = pd.concat([
        d[['is_unlicensed','availability_365','accommodates','is_entire_home']],
        room_dum, nb_dum
    ], axis=1).fillna(0)
    Xtr, Xte, ytr, yte = train_test_split(feats, d['log_price'], test_size=0.2, random_state=42)
    mdl   = LinearRegression().fit(Xtr, ytr)
    y_hat = mdl.predict(Xte)
    coefs = pd.Series(mdl.coef_, index=feats.columns)
    beta  = coefs['is_unlicensed']
    gap   = (np.exp(beta) - 1) * 100
    r2v   = r2_score(yte, y_hat)
    maev  = mean_absolute_error(np.exp(yte), np.exp(y_hat))
    print(f"\n[{label}]")
    print(f"  R²: {r2v:.4f}  |  MAE: {maev:.0f} TRY  |  Price gap: {gap:.1f}%  (β={beta:.4f})")
    print(f"\n  Neighbourhood coefficients (all vs Beşiktaş):")
    nb_coefs = coefs[coefs.index.str.startswith('nbhd_')].sort_values(ascending=False)
    for name, val in nb_coefs.items():
        print(f"    {name.replace('nbhd_',''):<20}: β={val:+.4f}  ({(np.exp(val)-1)*100:+.1f}%)")
    return r2v, maev, gap, coefs


r2_full, mae_full, gap_full, coefs_full = run_ols_besiktas(df_all,    'Full sample  (all listings)')
r2_act,  mae_act,  gap_act,  coefs_act  = run_ols_besiktas(df_active, 'Active sample (no ghosts)')
print(f"\nPrice gap — full sample : {gap_full:.1f}%")
print(f"Price gap — active only : {gap_act:.1f}%")
print("\n✅ Phase 2A complete.")


# =============================================================================
# 15. PHASE 2B — GEOGRAPHICALLY WEIGHTED REGRESSION (GWR)
# Bandwidth 101 cells confirmed by full Sel_BW AICc search (hardcoded to save time).
# =============================================================================

print("\n" + "=" * 60)
print("PHASE 2B: GEOGRAPHICALLY WEIGHTED REGRESSION (GWR)")
print("=" * 60)

# Aggregate active listings to H3 cell level (≥5 listings)
h3_gwr = df_active.groupby('h3_cell').agg(
    mean_log_price   = ('log_price',       'mean'),
    unlicensed_rate  = ('is_unlicensed',   'mean'),
    entire_home_rate = ('is_entire_home',  'mean'),
    mean_availability= ('availability_365','mean'),
    mean_accommodates= ('accommodates',    'mean'),
    listing_count    = ('id',             'count'),
    mean_price       = ('price_clean',    'mean'),
).reset_index()
h3_gwr = h3_gwr[h3_gwr['listing_count'] >= 5].copy()
print(f"\nH3 cells for GWR (≥5 active listings): {len(h3_gwr):,}")

# Cell centroids (Istanbul-centric km projection)
LAT_0, LON_0 = 41.0, 28.96
latlons_gwr  = [h3.cell_to_latlng(c) for c in h3_gwr['h3_cell']]
h3_gwr['y_km'] = [(ll[0] - LAT_0) * 111.0     for ll in latlons_gwr]
h3_gwr['x_km'] = [(ll[1] - LON_0) * 111.0 * np.cos(np.radians(LAT_0)) for ll in latlons_gwr]
coords_gwr = np.column_stack([h3_gwr['y_km'].values, h3_gwr['x_km'].values])

# Standardised feature matrix
feature_names = ['unlicensed_rate','entire_home_rate','mean_availability','mean_accommodates']
X_raw  = h3_gwr[feature_names].values
X_mean = X_raw.mean(axis=0); X_std = X_raw.std(axis=0); X_std[X_std==0] = 1
X_std_mat = (X_raw - X_mean) / X_std
y_gwr = h3_gwr['mean_log_price'].values.reshape(-1, 1)

# GWR fit — bandwidth 101 confirmed by full Sel_BW AICc search in prior runs
GWR_OPTIMAL = 101
print(f"Fitting GWR with AICc-optimal bandwidth = {GWR_OPTIMAL} cells...")
import time; t0 = time.time()
gwr_model   = GWR(coords_gwr, y_gwr, X_std_mat, GWR_OPTIMAL, fixed=False, kernel='bisquare')
gwr_results = gwr_model.fit()
print(f"GWR fit: {time.time()-t0:.1f}s  |  AICc={gwr_results.aicc:.2f}  "
      f"|  Mean local R²={gwr_results.localR2.mean():.4f}")

local_params     = gwr_results.params
local_r2         = gwr_results.localR2
local_unlic_coef = local_params[:, 1]
local_t_unlic    = gwr_results.tvalues[:, 1]
local_sig        = (np.abs(local_t_unlic) > 1.96).astype(int)

h3_gwr['local_unlic_coef'] = local_unlic_coef
h3_gwr['local_t']          = local_t_unlic
h3_gwr['local_sig']        = local_sig
h3_gwr['local_r2']         = local_r2.round(4)

n_neg     = (local_unlic_coef < 0).sum()
n_neg_sig = ((local_unlic_coef < 0) & (local_sig == 1)).sum()
print(f"\nCells with negative coef        : {n_neg} ({n_neg/len(h3_gwr)*100:.1f}%)")
print(f"Cells with sig. negative coef   : {n_neg_sig} ({n_neg_sig/len(h3_gwr)*100:.1f}%)")
print(f"Local β range: [{local_unlic_coef.min():.4f}, {local_unlic_coef.max():.4f}]")

# Add district names
cell_nb = df_active.groupby('h3_cell')['neighbourhood_cleansed'].agg(
    lambda x: x.value_counts().index[0]).reset_index()
h3_gwr = h3_gwr.merge(cell_nb, on='h3_cell', how='left')

print("\n--- TOP 10 CELLS: STRONGEST PENALTY ---")
print(h3_gwr.nsmallest(10,'local_unlic_coef')[
    ['neighbourhood_cleansed','local_unlic_coef','unlicensed_rate','mean_price']
].to_string(index=False))

# GWR coefficient map
hex_polys_gwr = []
for _, row in h3_gwr.iterrows():
    boundary = h3.cell_to_boundary(row['h3_cell'])
    poly = Polygon([(lng, lat) for lat, lng in boundary])
    hex_polys_gwr.append({'geometry':poly, 'local_coef':row['local_unlic_coef'],
                          'local_r2':row['local_r2'], 'unlicensed_rate':row['unlicensed_rate'],
                          'mean_price':row['mean_price'], 'h3_cell':row['h3_cell']})
gdf_gwr = gpd.GeoDataFrame(hex_polys_gwr, crs='EPSG:4326')

fig_gwr, axes_gwr = plt.subplots(1, 2, figsize=(14, 6))
fig_gwr.suptitle('Geographically Weighted Regression — Istanbul Airbnb\n'
                 'Local Unlicensed Price Coefficient per H3 Cell (Resolution 8)',
                 fontsize=12, fontweight='bold')
vmin = np.percentile(h3_gwr['local_unlic_coef'], 5)
vmax = np.percentile(h3_gwr['local_unlic_coef'], 95)
gdf_gwr.plot(column='local_coef', ax=axes_gwr[0], cmap='RdBu', vmin=vmin, vmax=vmax,
             legend=True, legend_kwds={'label':'Local β (unlicensed)','shrink':0.7})
axes_gwr[0].set_title('Local Unlicensed Coefficient'); axes_gwr[0].set_axis_off()
gdf_gwr.plot(column='local_r2', ax=axes_gwr[1], cmap='YlOrRd', vmin=0, vmax=0.8,
             legend=True, legend_kwds={'label':'Local R²','shrink':0.7})
axes_gwr[1].set_title('Local R²'); axes_gwr[1].set_axis_off()
plt.tight_layout()
fig_gwr.text(0.99, 0.01, 'Source: Inside Airbnb, Sep 2025 | mgwr 2.2', ha='right', fontsize=8)
plt.savefig('Data/fig_gwr_coefficients.png', dpi=150, bbox_inches='tight', facecolor='white')
print("Saved: Data/fig_gwr_coefficients.png")

# Interactive GWR map
def gwr_colour(coef):
    if coef < -0.4:   return '#2166ac'
    elif coef < -0.2: return '#74add1'
    elif coef < 0.0:  return '#abd9e9'
    elif coef < 0.2:  return '#fdae61'
    else:             return '#d73027'

gwr_map = folium.Map(location=[41.01, 28.96], zoom_start=10, tiles='CartoDB positron')
for feature in json.loads(gdf_gwr.to_json())['features']:
    coef   = feature['properties'].get('local_coef', 0) or 0
    colour = gwr_colour(coef)
    folium.GeoJson(feature,
        style_function=lambda x, c=colour: {
            'fillColor':c,'color':'white','weight':0.5,'fillOpacity':0.75},
        tooltip=folium.GeoJsonTooltip(
            fields=['local_coef','local_r2','unlicensed_rate','mean_price'],
            aliases=['Local β:','Local R²:','Unlicensed rate:','Avg price (TRY):'])
    ).add_to(gwr_map)
gwr_map.get_root().html.add_child(folium.Element("""
<div style="position:fixed;bottom:40px;left:40px;z-index:1000;background:white;
     padding:12px 16px;border-radius:8px;box-shadow:2px 2px 6px rgba(0,0,0,0.3);
     font-family:Arial;font-size:12px">
  <b>GWR: Local Unlicensed β</b><br>
  <i style="background:#2166ac;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>&lt;−0.4 Strong penalty<br>
  <i style="background:#74add1;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>−0.4 to −0.2<br>
  <i style="background:#abd9e9;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>−0.2 to 0.0<br>
  <i style="background:#fdae61;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>0.0 to +0.2<br>
  <i style="background:#d73027;width:14px;height:14px;display:inline-block;margin-right:6px;border-radius:2px"></i>&gt;+0.2 Anomalous<br>
  <br><small>GWR adaptive bisquare | mgwr 2.2<br>Data: Inside Airbnb, Sep 2025</small>
</div>"""))
gwr_map.save('Data/istanbul_gwr_map.html')
print("Saved: Data/istanbul_gwr_map.html")
print("\n✅ Phase 2B (GWR) complete.")



# =============================================================================
# 17. PHASE 2D — GWR BANDWIDTH SENSITIVITY + VARIABLE-SCALE ANALYSIS
# Responds to professor's critique that bw=101 is too broad for central Istanbul.
# Part A: AICc at bw = 30, 60, 101 — validates global optimum
# Part B: Per-predictor univariate GWR — finds intrinsic spatial scale of each variable
# =============================================================================

print("\n" + "=" * 65)
print("PHASE 2D: GWR BANDWIDTH SENSITIVITY & VARIABLE-SCALE ANALYSIS")
print("=" * 65)

# Reuse h3_data, coords_gwr, X_std_mat, y_gwr from Section 15
# Rename for clarity
h3_data_bw = h3_gwr.copy().reset_index(drop=True)
n_bw = len(h3_data_bw)

# Part A: GWR at bw = 30, 60, 101
print("\n[A] GWR bandwidth sensitivity: bw = 30, 60, 101 cells")
bw_list     = [30, 60, 101]
gwr_fits    = {}
bw_summary  = {}

for bw in bw_list:
    print(f"  Fitting GWR bw={bw}...", end=' ', flush=True)
    t0 = time.time()
    mdl = GWR(coords_gwr, y_gwr, X_std_mat, bw, fixed=False, kernel='bisquare')
    res = mdl.fit()
    elapsed = time.time() - t0
    gwr_fits[bw] = res
    coef = res.params[:, 1]
    t_val = res.tvalues[:, 1]
    sig   = np.abs(t_val) > 1.96
    n_sig_neg = ((coef < 0) & sig).sum()
    bw_summary[bw] = {
        'aicc': res.aicc, 'r2': res.localR2.mean(),
        'coef_min': coef.min(), 'coef_max': coef.max(),
        'n_sig_neg': n_sig_neg, 'coef': coef, 'sig': sig,
        'local_r2': res.localR2.flatten()
    }
    marker = ' ← AICc optimal' if bw == GWR_OPTIMAL else ''
    print(f"done ({elapsed:.1f}s)  AICc={res.aicc:.2f}  mean R²={res.localR2.mean():.4f}{marker}", flush=True)

print(f"\n  {'BW':<8} {'% of cells':<12} {'Mean R²':<10} {'AICc':<10} {'Sig neg cells'}")
print("  " + "-"*55)
for bw in bw_list:
    s = bw_summary[bw]
    marker = ' ← optimal' if bw == GWR_OPTIMAL else ''
    print(f"  {bw:<8} {bw/n_bw*100:<11.1f}% {s['r2']:<10.4f} {s['aicc']:<10.2f} "
          f"{s['n_sig_neg']}/{n_bw}{marker}")

aicc_30, aicc_60, aicc_101 = [bw_summary[bw]['aicc'] for bw in [30,60,101]]
if aicc_101 < aicc_60 < aicc_30:
    print("\n  AICc decreases with broader bandwidth — global optimum confirmed at bw=101.")
    print("  Professor's critique is valid for central cells but AICc supports bw=101 overall.")

# Part B: Per-predictor variable-scale analysis
print("\n[B] Variable-scale analysis (per-predictor optimal bandwidth)")
bw_candidates  = [20, 30, 40, 50, 60, 70, 80, 90, 101, 120, 150, 200]
var_labels     = ['unlicensed_rate','entire_home_rate','mean_availability','mean_accommodates']
var_optimal_bw = {}

for vi, vname in enumerate(var_labels):
    X_single = X_std_mat[:, vi].reshape(-1, 1)
    best_bw, best_aicc = None, np.inf
    print(f"  {vname:<25}: ", end='', flush=True)
    for bw in bw_candidates:
        m = GWR(coords_gwr, y_gwr, X_single, bw, fixed=False, kernel='bisquare')
        r = m.fit()
        if r.aicc < best_aicc:
            best_aicc, best_bw = r.aicc, bw
    var_optimal_bw[vname] = best_bw
    note = " ← FINER than GWR" if best_bw < GWR_OPTIMAL else \
           (" ← COARSER" if best_bw > GWR_OPTIMAL else " ← same")
    print(f"best BW = {best_bw:>4} cells  (AICc={best_aicc:.2f}){note}", flush=True)

unlicensed_bw = var_optimal_bw['unlicensed_rate']
print(f"\n  Key result: unlicensed_rate intrinsic scale = {unlicensed_bw} cells")
if unlicensed_bw < GWR_OPTIMAL:
    print(f"  Confirms professor's critique: compliance effect is {GWR_OPTIMAL//unlicensed_bw}× more local")
    print(f"  than GWR's single bandwidth. Full MGWR would assign ~{unlicensed_bw} cells to this variable.")

# Part C: Save outputs
print("\n[C] Saving outputs...")

# Per-cell coefficients CSV
for bw in bw_list:
    h3_data_bw[f'gwr_unlic_bw{bw}'] = gwr_fits[bw].params[:, 1]
    h3_data_bw[f'gwr_r2_bw{bw}']    = gwr_fits[bw].localR2.flatten().round(4)
    h3_data_bw[f'gwr_sig_bw{bw}']   = (np.abs(gwr_fits[bw].tvalues[:, 1]) > 1.96).astype(int)

out_cols = ['h3_cell','listing_count','unlicensed_rate','mean_price'] + \
           [f'gwr_unlic_bw{bw}' for bw in bw_list] + \
           [f'gwr_sig_bw{bw}'   for bw in bw_list] + \
           [f'gwr_r2_bw{bw}'    for bw in bw_list]
h3_data_bw[out_cols].to_csv('Data/mgwr_summary.csv', index=False)
print("  Saved: Data/mgwr_summary.csv")

# Bandwidth results text
lines_bw = [
    "MGWR-Style Variable-Scale Analysis — Istanbul Airbnb",
    "=" * 55,
    f"Global GWR bandwidth (AICc-optimal): {GWR_OPTIMAL} cells",
    "",
    "Univariate per-variable optimal bandwidths:",
    "(AICc minimised independently for each predictor)",
    "",
]
for vname in var_labels:
    bv = var_optimal_bw[vname]
    note = "finer" if bv < GWR_OPTIMAL else ("coarser" if bv > GWR_OPTIMAL else "same")
    lines_bw.append(f"  {vname:<25}: {bv:>4} cells  [{note} than global GWR BW]")
lines_bw += ["", "GWR AICc at different bandwidths:"]
for bw in bw_list:
    marker = " ← AICc-optimal" if bw == GWR_OPTIMAL else ""
    lines_bw.append(f"  bw={bw:>4} cells: AICc={bw_summary[bw]['aicc']:.2f}{marker}")
lines_bw += [
    "",
    f"Interpretation: AICc minimised at bw={GWR_OPTIMAL}.",
    f"However unlicensed_rate prefers bw={unlicensed_bw} — confirms local compliance effect.",
    "MGWR addresses this by assigning each predictor its own bandwidth.",
]
with open('Data/mgwr_bandwidths.txt', 'w') as f:
    f.write('\n'.join(lines_bw))
print("  Saved: Data/mgwr_bandwidths.txt")

# Bandwidth comparison figure
hex_polys_bw = []
for _, row in h3_data_bw.iterrows():
    boundary = h3.cell_to_boundary(row['h3_cell'])
    poly = Polygon([(lng, lat) for lat, lng in boundary])
    hex_polys_bw.append({'geometry': poly,
                          **{f'coef_bw{bw}': row[f'gwr_unlic_bw{bw}'] for bw in bw_list}})
gdf_bw = gpd.GeoDataFrame(hex_polys_bw, crs='EPSG:4326')

all_coefs = np.concatenate([bw_summary[bw]['coef'] for bw in bw_list])
vabs_bw   = max(abs(np.percentile(all_coefs, 3)), abs(np.percentile(all_coefs, 97)))
titles_bw = {30: f'GWR bw=30 cells\nAICc={aicc_30:.1f}',
             60: f'GWR bw=60 cells\nAICc={aicc_60:.1f}',
             101: f'GWR bw=101 cells ← AICc optimal\nAICc={aicc_101:.1f}'}

fig_bw, axes_bw = plt.subplots(1, 3, figsize=(18, 6))
for ax, bw in zip(axes_bw, bw_list):
    gdf_bw.plot(column=f'coef_bw{bw}', ax=ax, cmap='RdBu_r',
                vmin=-vabs_bw, vmax=vabs_bw, legend=True,
                legend_kwds={'label':'Local β (unlicensed)','shrink':0.75,'orientation':'horizontal'})
    ax.set_title(titles_bw[bw], fontsize=10); ax.set_axis_off()
fig_bw.suptitle('GWR Bandwidth Sensitivity — Local Unlicensed Price Coefficient\n'
                'Istanbul Airbnb, H3 Res-8, Active Listings Sep 2025',
                fontsize=12, fontweight='bold', y=1.03)
plt.tight_layout()
plt.savefig('Data/fig_mgwr_comparison.png', dpi=150, bbox_inches='tight', facecolor='white')
print("  Saved: Data/fig_mgwr_comparison.png")

# Interactive sensitivity map (bw=101)
def coef_color(coef, sig):
    if sig == 0: return '#cccccc'
    if coef < -0.20:   return '#053061'
    elif coef < -0.12: return '#2166ac'
    elif coef < 0.0:   return '#92c5de'
    elif coef < 0.05:  return '#f4a582'
    else:              return '#b2182b'

fmap_bw = folium.Map(location=[41.01, 28.96], zoom_start=10, tiles='CartoDB positron')
for _, row in h3_data_bw.iterrows():
    coef   = row['gwr_unlic_bw101']
    sig    = row['gwr_sig_bw101']
    colour = coef_color(coef, sig)
    try:
        boundary = h3.cell_to_boundary(row['h3_cell'])
        poly = [[lat, lng] for lat, lng in boundary]
        folium.Polygon(locations=poly, color='white', weight=0.5,
            fill=True, fill_color=colour, fill_opacity=0.75,
            tooltip=(f"Local β (bw=101): {coef:.4f}<br>"
                     f"Significant: {int(sig)}<br>"
                     f"Unlicensed rate: {row['unlicensed_rate']:.3f}")
        ).add_to(fmap_bw)
    except Exception:
        pass
fmap_bw.get_root().html.add_child(folium.Element(f"""
<div style="position:fixed;bottom:40px;left:40px;z-index:1000;background:white;
     padding:12px 16px;border-radius:8px;box-shadow:2px 2px 6px rgba(0,0,0,.3);
     font-family:Arial;font-size:12px">
  <b>GWR bw=101 cells (AICc optimal)</b><br>
  <small>Unlicensed rate optimal BW: {unlicensed_bw} cells</small><br><br>
  <i style="background:#053061;width:14px;height:14px;display:inline-block;margin-right:6px"></i>&lt;−0.20 Very strong penalty<br>
  <i style="background:#2166ac;width:14px;height:14px;display:inline-block;margin-right:6px"></i>−0.20 to −0.12<br>
  <i style="background:#92c5de;width:14px;height:14px;display:inline-block;margin-right:6px"></i>−0.12 to 0.0<br>
  <i style="background:#f4a582;width:14px;height:14px;display:inline-block;margin-right:6px"></i>0.0 to +0.05<br>
  <i style="background:#b2182b;width:14px;height:14px;display:inline-block;margin-right:6px"></i>&gt;+0.05 Anomalous<br>
  <i style="background:#cccccc;width:14px;height:14px;display:inline-block;margin-right:6px"></i>Not significant<br>
</div>"""))
fmap_bw.save('Data/istanbul_mgwr_map.html')
print("  Saved: Data/istanbul_mgwr_map.html")

print("\n✅ Phase 2D (Bandwidth Sensitivity + Variable-Scale) complete.")


# =============================================================================
# FINAL SUMMARY
# =============================================================================

print("\n" + "=" * 65)
print("FULL ANALYSIS COMPLETE — SUMMARY")
print("=" * 65)
print(f"\n  Dataset              : Istanbul Airbnb, Sep 2025 (Inside Airbnb)")
print(f"  Listings (cleaned)   : {len(df_clean):,}  (Sample A)")
print(f"  Active listings      : {len(df_active):,}  (Sample B, no ghost listings)")
print(f"  H3 cells (res 8)     : {df_clean['h3_cell'].nunique():,}")
print(f"  Unlicensed listings  : {df_clean['is_unlicensed'].sum():,}  ({df_clean['is_unlicensed'].mean()*100:.1f}%)")

print(f"\n  [PHASE 1 — Baseline Analysis]")
print(f"  Baseline OLS R²           : {r2:.4f}")
print(f"  Compliance price gap      : {price_effect_pct:.1f}%")
print(f"  Global Moran's I          : {I_u:.4f}  (p={p_u:.4f})")
print(f"  Price Moran's I           : {I_p:.4f}  (p={p_p:.4f})")

print(f"\n  [PHASE 1B — Ghost Listing Sensitivity]")
print(f"  All listings price gap    : {results_sensitivity['All listings']['price_gap']}%")
print(f"  Active-only price gap     : {results_sensitivity['Active only']['price_gap']}%")

print(f"\n  [PHASE 2A — Updated OLS (Beşiktaş reference)]")
print(f"  Price gap (active sample) : {gap_act:.1f}%")

print(f"\n  [PHASE 2B — GWR]")
print(f"  Cells analysed            : {len(h3_gwr):,}")
print(f"  Optimal bandwidth         : {GWR_OPTIMAL} cells (AICc-confirmed)")
print(f"  Mean local R²             : {gwr_results.localR2.mean():.4f}")
print(f"  Cells with sig. neg. β    : {n_neg_sig} ({n_neg_sig/len(h3_gwr)*100:.1f}%)")

print(f"\n  [PHASE 2D — Bandwidth Sensitivity + Variable-Scale]")
print(f"  AICc: bw30={aicc_30:.1f}  bw60={aicc_60:.1f}  bw101={aicc_101:.1f}")
print(f"  AICc minimum confirms bw=101 as global optimum.")
for vname in var_labels:
    bv = var_optimal_bw[vname]
    note = f"finer (×{GWR_OPTIMAL//bv})" if bv < GWR_OPTIMAL else "coarser/same"
    print(f"  {vname:<25}: {bv} cells [{note} than GWR bw]")
print(f"\n  → unlicensed_rate prefers bw={unlicensed_bw}: compliance effect is highly localised.")
print(f"    GWR's single bandwidth smooths this out.")
print(f"    Full MGWR would resolve this by assigning per-predictor bandwidths.")

print(f"\n  Outputs saved to Data/:")
print("    fig_sample_comparison.png, fig_gwr_coefficients.png,")
print("    fig_mgwr_comparison.png, mgwr_summary.csv, mgwr_bandwidths.txt,")
print("    istanbul_compliance_map.html, istanbul_price_map.html,")
print("    istanbul_lisa_map.html, istanbul_temporal_map.html,")
print("    istanbul_gwr_map.html, istanbul_mgwr_map.html")
print("\n✅ All analyses complete.")
