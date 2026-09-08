"""Booking.com guest-type composition series (hotel and other-lodging comparators for the Airbnb review proxies).

Two public review datasets, both gitignored under data/raw/booking/:
  1. 515K Hotel Reviews in Europe (Kaggle jiashenliu; HF mirror Dricz/515k-Hotel-Reviews-In-Europe): 1,493 luxury hotels,
     Aug 2015 - Aug 2017, 'Tags' carries the trip type (Leisure/Business), traveller type (Solo traveler / Couple / Group /
     Family with young children / Family with older children / Travelers with friends), room type and nights.
  2. Booking.com accommodation-reviews (HF Booking-com/accommodation-reviews, RecTour 2024; CC BY-SA 4.0, non-commercial):
     ~1.6M English reviews from 2023 with guest_type (Solo/Couple/Group/Family), accommodation_type (hotel, apartment, ...),
     check-in month, country. Licence restricts use to non-commercial - flagged in data/README.md.
Outputs: data/processed/booking_515k_guest_type_monthly.csv, booking_rectour24_guest_type_by_type_month.csv
"""
import os, re, sys, urllib.request
import pandas as pd, numpy as np

RAW = 'data/raw/booking'; OUT = 'data/processed'; os.makedirs(RAW, exist_ok=True)
SRC = {
    '515k_hotel_reviews.csv': 'https://huggingface.co/datasets/Dricz/515k-Hotel-Reviews-In-Europe/resolve/main/Hotel_Reviews.csv',
    'rectour24_train_users.csv': 'https://huggingface.co/datasets/Booking-com/accommodation-reviews/resolve/main/rectour24/train_users.csv',  # one row per reviewing stay: guest_type, accommodation_type, month...
}


def fetch(name):
    p = f'{RAW}/{name}'
    if os.path.exists(p) and os.path.getsize(p) > 1_000_000: return p
    req = urllib.request.Request(SRC[name], headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=120) as r, open(p + '.part', 'wb') as f:
        while True:
            b = r.read(1 << 20)
            if not b: break
            f.write(b)
    os.replace(p + '.part', p); return p


TAG_TYPES = {'Solo traveler': 'solo', 'Couple': 'couple', 'Group': 'group', 'Travelers with friends': 'group',
             'Family with young children': 'family', 'Family with older children': 'family'}
TAG_NUM = {'solo': 1, 'couple': 2, 'family': 3.9, 'group': 4.7}


def s515k():
    p = fetch('515k_hotel_reviews.csv')
    df = pd.read_csv(p, usecols=['Hotel_Address', 'Review_Date', 'Tags', 'Reviewer_Nationality'])
    df['date'] = pd.to_datetime(df.Review_Date, format='%m/%d/%Y', errors='coerce'); df['m'] = df.date.dt.to_period('M').astype(str)
    df['country'] = df.Hotel_Address.str.strip().str.split().str[-1].replace({'Kingdom': 'United Kingdom'})
    tags = df.Tags.fillna('')
    df['gtype'] = pd.Series(np.nan, index=df.index, dtype='object')
    for t, k in TAG_TYPES.items(): df.loc[tags.str.contains(t, regex=False), 'gtype'] = k
    df['business'] = tags.str.contains('Business trip', regex=False)
    df['nights'] = pd.to_numeric(tags.str.extract(r'Stayed (\d+) night')[0], errors='coerce')
    d = df[df.gtype.notna()]
    rows = []
    for (m, c), g in list(d.groupby(['m', 'country'])) + [((m, 'ALL'), g) for m, g in d.groupby('m')]:
        vc = g.gtype.value_counts(normalize=True)
        rows.append(dict(month=m, country=c, reviews=len(g), share_solo=vc.get('solo', 0), share_couple=vc.get('couple', 0), share_family=vc.get('family', 0), share_group=vc.get('group', 0),
                         implied_party_size=sum(vc.get(k, 0) * v for k, v in TAG_NUM.items()), business_share=g.business.mean(), nights_mean=g.nights.mean()))
    out = pd.DataFrame(rows).sort_values(['country', 'month']); out.to_csv(f'{OUT}/booking_515k_guest_type_monthly.csv', index=False)
    print('515k:', len(d), 'tagged reviews', out[out.country.eq('ALL')].month.min(), '-', out[out.country.eq('ALL')].month.max())
    # leisure-only version
    dl = d[~d.business]; vc = dl.groupby(dl.date.dt.to_period('Q').astype(str)).gtype.value_counts(normalize=True).unstack().fillna(0)
    print(vc.round(3).to_string())


def rectour():
    p = fetch('rectour24_train_users.csv')
    use = ['guest_type', 'guest_country', 'room_nights', 'month', 'accommodation_type', 'accommodation_country', 'accommodation_star_rating',
           'location_is_beach', 'location_is_ski', 'location_is_city_center']
    df = pd.read_csv(p, usecols=lambda c: c in use, low_memory=False)
    df['gtype'] = df.guest_type.astype(str).str.lower().str.extract(r'(solo|couple|group|family)')[0]
    d = df[df.gtype.notna()]
    rows = []
    for keys, g in list(d.groupby(['accommodation_type', 'month'])) + [((t, 'ALL'), g) for t, g in d.groupby('accommodation_type')] + [(('ALL', m), g) for m, g in d.groupby('month')]:
        vc = g.gtype.value_counts(normalize=True)
        rows.append(dict(accommodation_type=keys[0], month=keys[1], reviews=len(g), share_solo=vc.get('solo', 0), share_couple=vc.get('couple', 0), share_family=vc.get('family', 0), share_group=vc.get('group', 0),
                         implied_party_size=sum(vc.get(k, 0) * v for k, v in TAG_NUM.items()), nights_mean=pd.to_numeric(g.room_nights, errors='coerce').mean()))
    out = pd.DataFrame(rows); out.to_csv(f'{OUT}/booking_rectour24_guest_type_by_type_month.csv', index=False)
    # by country x type (annual)
    ct = d.groupby(['accommodation_country', 'accommodation_type']).gtype.value_counts(normalize=True).unstack().fillna(0)
    ct['reviews'] = d.groupby(['accommodation_country', 'accommodation_type']).size(); ct = ct[ct.reviews >= 500]
    ct.reset_index().to_csv(f'{OUT}/booking_rectour24_guest_type_by_country_type.csv', index=False)
    print('rectour24:', len(d)); print(out[out.month.eq('ALL')].sort_values('reviews', ascending=False).head(12).round(3).to_string())


if __name__ == '__main__':
    for fn in (s515k, rectour):
        try: fn()
        except Exception as e: print('ERR', fn.__name__, e, flush=True)
