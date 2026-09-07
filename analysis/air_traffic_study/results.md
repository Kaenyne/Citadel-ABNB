# Results (run 2026-09-04)

## aggregate_correlation.py
```
Same-quarter Pearson r (n): 2023Q1-2026Q2 | 2024Q1-2026Q2
TSA yoy     vs Nights yoy    : +0.84 (n=14) | +0.16 (n=10)
TSA yoy     vs GBV yoy       : +0.39 (n=14) | -0.17 (n=10)
TSA yoy     vs Rev yoy       : +0.63 (n=14) | +0.20 (n=10)
TSA yoy     vs Stock qtr ret : +0.56 (n=14) | +0.03 (n=10)
BTS yoy     vs Nights yoy    : +0.67 (n=14) | +0.16 (n=10)
BTS yoy     vs GBV yoy       : +0.26 (n=14) | -0.20 (n=10)
BTS yoy     vs Rev yoy       : +0.61 (n=14) | +0.23 (n=10)
BTS yoy     vs Stock qtr ret : +0.35 (n=14) | -0.00 (n=10)
IATA total  vs Nights yoy    : +0.83 (n=14) | +0.04 (n=10)
IATA total  vs GBV yoy       : +0.37 (n=14) | -0.37 (n=10)
IATA total  vs Rev yoy       : +0.61 (n=14) | +0.05 (n=10)
IATA total  vs Stock qtr ret : +0.59 (n=14) | +0.16 (n=10)
IATA intl   vs Nights yoy    : +0.86 (n=14) | +0.05 (n=10)
IATA intl   vs GBV yoy       : +0.38 (n=14) | -0.43 (n=10)
IATA intl   vs Rev yoy       : +0.56 (n=14) | -0.01 (n=10)
IATA intl   vs Stock qtr ret : +0.69 (n=14) | +0.16 (n=10)

Lead/lag: air yoy (t) vs Nights yoy (t+1), 2023-2026
TSA yoy    : +0.51 (n=13)
BTS yoy    : +0.53 (n=13)
IATA total : +0.55 (n=13)
IATA intl  : +0.45 (n=13)

Levels: TSA quarterly screenings vs nights booked: r=-0.09 (n=14)

Quarter, TSA, BTS, IATAtot, IATAintl, Nights, GBV, Rev, StockRet
2023Q1 +20.4 +9.7 +58.3 +87.5 +19.0 +19.0 +20.0 +45.5
2023Q2 +10.9 +8.1 +38.6 +40.9 +11.0 +13.0 +18.0 +3.0
2023Q3 +11.3 +8.2 +28.2 +30.4 +14.0 +17.0 +18.0 +7.1
2023Q4 +10.7 +8.6 +28.7 +26.8 +12.0 +15.0 +17.0 -0.8
2024Q1 +8.0 +6.3 +17.3 +22.0 +9.5 +12.0 +18.0 +21.2
2024Q2 +6.7 +5.9 +10.3 +14.2 +9.0 +11.0 +11.0 -8.1
2024Q3 +4.3 +3.5 +7.9 +10.0 +8.0 +10.0 +10.0 -16.4
2024Q4 +2.5 +1.8 +7.9 +10.6 +12.0 +13.0 +12.0 +3.6
2025Q1 -0.4 -1.7 +5.3 +7.6 +8.0 +7.0 +6.0 -9.1
2025Q2 -0.6 -1.4 +5.2 +6.9 +7.0 +11.0 +13.0 +10.8
2025Q3 +1.0 -0.2 +4.1 +5.7 +9.0 +14.0 +10.0 -8.3
2025Q4 +1.2 -1.3 +6.0 +8.0 +10.0 +16.0 +12.0 +11.8
2026Q1 +1.5 +0.2 +4.0 +3.7 +9.0 +19.0 +18.0 -7.0
2026Q2 -0.7 -0.3 -2.4 -2.6 +10.0 +16.0 +17.0 +13.3
```

## regional_correlation.py
```
Region | quarters | r(air RPK yoy, Airbnb regional revenue yoy) | avg air yoy | avg Airbnb yoy
north_america  | n=10 | r=+0.20 | +2.3% | +7.1%
europe         | n=10 | r=+0.25 | +6.5% | +15.9%
latin_america  | n=10 | r=+0.08 | +7.8% | +20.6%
asia_pacific   | n=10 | r=+0.28 | +11.5% | +17.8%

Quarterly detail (air RPK yoy -> Airbnb revenue yoy):
2024Q1  north +7.1->+9.7  europ +11.8->+23.8  latin +11.3->+30.6  asia_ +31.3->+26.5
2024Q2  north +5.9->+9.7  europ +9.7->+11.4  latin +11.0->+13.5  asia_ +19.0->+10.1
2024Q3  north +3.6->+6.4  europ +7.2->+12.6  latin +7.1->+11.8  asia_ +12.6->+13.0
2024Q4  north +3.1->+6.5  europ +8.2->+16.3  latin +8.3->+12.1  asia_ +14.8->+21.7
2025Q1  north -0.3->+3.8  europ +5.4->+5.3  latin +6.2->+11.7  asia_ +8.9->+9.9
2025Q2  north +0.4->+5.3  europ +4.6->+17.7  latin +9.1->+24.9  asia_ +8.3->+23.2
2025Q3  north +0.8->+3.0  europ +3.3->+14.1  latin +6.7->+18.1  asia_ +5.6->+15.7
2025Q4  north +0.8->+3.2  europ +6.8->+17.1  latin +5.6->+26.3  asia_ +7.4->+18.2
2026Q1  north +2.0->+8.0  europ +6.1->+25.1  latin +8.6->+31.5  asia_ +7.3->+23.0
2026Q2  north -0.7->+15.8  europ +1.4->+15.6  latin +4.2->+26.0  asia_ -0.6->+16.9

Cross-sectional (4 regions, 2024-26 averages): r=+0.81
```

## destination_snapshot.py
```
destination | air yoy | STR yoy (metric)
Hawaii     | +1.2% | +5.5% (DBEDT vacation-rental unit-night demand (official))
Orlando    | -4.8% | +19.3% (AirDNA occupancy)
Las Vegas  | -9.3% | -17.1% (AirDNA RevPAR)
Cancun     | -11.5% | -7.3% (AirROI STR revenue)
Miami      | +0.5% | +14.1% (AirDNA RevPAR)
Athens     | +1.7% | -4.6% (AirROI STR revenue)

Cross-sectional Pearson r across 6 destinations: +0.49
Same sign: 4/6
```
