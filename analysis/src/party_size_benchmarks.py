"""Assemble every non-Airbnb party-size series we hold into one long table for comparison with the Airbnb proxies.
Output: data/processed/party_size_benchmarks.csv  (source, segment, geography, freq, period, party_size, share_1, share_2, share_3plus, n)
"""
import pandas as pd, numpy as np
OUT = 'data/processed'
rows = []
# Hawaii DBEDT annual by accommodation (party basis)
h = pd.read_csv(f'{OUT}/hawaii_party_size_annual.csv')
lab = {'hotel': 'Hotel only', 'condo': 'Condo only', 'timeshare': 'Timeshare only', 'rental_house': 'Rental house only (STR)', 'bnb': 'B&B only', 'all_air': 'All air visitors'}
for _, r in h[h.segment.isin(lab)].iterrows():
    rows.append(dict(source='Hawaii DBEDT Annual Visitor Research', segment=lab[r.segment], geography='Hawaii (air visitors)', freq='annual', period=str(int(r.year)),
                     party_size=r.avg_party_size, share_1=r.get('share_parties_1'), share_2=r.get('share_parties_2'), share_3plus=r.get('share_parties_3plus'), n=r.visitors))
# Hawaii monthly all visitors
m = pd.read_csv(f'{OUT}/hawaii_party_size_monthly.csv'); m = m[m.flight.eq('total')]
for _, r in m.iterrows():
    rows.append(dict(source='Hawaii DBEDT Visitor Highlights', segment='All air visitors', geography='Hawaii (air visitors)', freq='monthly', period=r.ym, party_size=r.party_size, n=r.visitors))
# Portugal hotel ledger quarterly
p = pd.read_csv(f'{OUT}/hotel_party_size_portugal_quarterly.csv')
for _, r in p.iterrows():
    rows.append(dict(source='Portugal hotel bookings ledger (Antonio et al. 2019)', segment=f'Hotel bookings - {r.hotel}', geography='Portugal (2 hotels)', freq='quarterly', period=r.q,
                     party_size=r.party_size, share_1=r.share_1, share_3plus=r.share_3plus, n=r.bookings))
# Las Vegas Visitor Profile: mean guests per hotel room (2025 study, Figure 29)
for yr, v in [('2024', 2.2), ('2025', 2.2)]:
    rows.append(dict(source='LVCVA Las Vegas Visitor Profile Study 2025', segment='Hotel room occupants (mean guests per room)', geography='Las Vegas', freq='annual', period=yr, party_size=v,
                     n=np.nan))
# NTTO SIAT inbound composition (people basis): traveled alone share
for yr, geo, alone, spouse, fam in [('2024', 'Overseas visitors to US', .599, .208, .177), ('2025', 'Overseas visitors to US', .586, .214, .183),
                                   ('2024', 'Canadian air visitors to US', .603, .229, .145), ('2025', 'Canadian air visitors to US', .612, .223, .154),
                                   ('2024', 'Mexican air visitors to US', .628, .166, .186), ('2025', 'Mexican air visitors to US', .614, .171, .200)]:
    rows.append(dict(source='NTTO Survey of International Air Travelers', segment='All inbound air travellers (~72% hotel)', geography=geo, freq='annual', period=yr,
                     party_size=np.nan, share_1=alone, share_2=spouse, share_3plus=np.nan, n=np.nan, note=f'with family/relatives {fam:.1%}'))
df = pd.DataFrame(rows)
df.to_csv(f'{OUT}/party_size_benchmarks.csv', index=False)
print(df.groupby(['source', 'segment']).period.agg(['min', 'max', 'count']).to_string())
