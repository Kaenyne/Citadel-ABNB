# Post-Earnings-Announcement-Drift

This repository contains a quantitative finance research project studying **Post-Earnings-Announcement Drift (PEAD)** and the role of **investor attention** in delayed price reactions after earnings releases.

The project combines a traditional **event study framework** with **alternative attention data (Google Trends)** to test whether limited investor attention and earnings announcement congestion contribute to PEAD.

The analysis is motivated by several key academic papers:

- Bernard & Thomas (1990) – evidence that stock prices do not fully reflect the implications of current earnings for future earnings  
- Hirshleifer, Lim & Teoh (2009) – investor distraction and competing news events  
- Da, Engelberg & Gao (2011) – Google search volume as a proxy for investor attention  

---

# Research Question

This project investigates three related questions:

1. Does **Post-Earnings-Announcement Drift** appear in a sample of U.S. equities?  
2. Does **investor attention** influence the magnitude of the drift?  
3. Does **earnings announcement congestion** (many firms announcing on the same day) amplify delayed price reactions?  

These questions test the hypothesis that **limited attention slows the incorporation of earnings information into prices.**

---

# Methodology

The analysis follows a standard **event study design**.

Event timeline:

```
t = 0        earnings announcement  
t = 0–1      immediate reaction window  
t = 2–21     post-announcement drift window  
```

Key measures:

- **Earnings surprise proxy:** `CAR(0,1)`  
- **Post-earnings drift:** `CAR(2,21)`  

Stocks are sorted based on the sign and magnitude of the earnings surprise, and drift is analyzed conditional on attention measures.

Investor attention is proxied using **Google Trends search volume**, following the approach proposed in Da, Engelberg & Gao (2011).

---

# Project Pipeline

```
Price Data
↓
Daily Returns
↓
Earnings Announcement Events
↓
CAR(0,1) Surprise Proxy
↓
CAR(2,21) Drift Measurement
↓
Google Trends Attention Data
↓
Earnings Congestion Measures
↓
Merged Event Dataset
↓
Drift Analysis and Strategy Backtest
```

---

# Repository Structure

```
Post-Earnings-Announcement-Drift
│
├── Notebooks
│   ├── 01_prices_and_returns.ipynb
│   ├── 02_earnings_events_and_surprise.ipynb
│   ├── 03_google_trends_attention.ipynb
│   ├── 04_merge_and_generate_report_results.ipynb
│   ├── GoogleTrends.ipynb
│   └── Report.ipynb
│
├── Output
│   ├── tables
│   ├── figures
│   ├── final
│   ├── manual
│   └── cache
│
├── Papers
│   ├── PEAD.pdf
│   ├── Driven to Distraction.pdf
│   ├── Evidence That Stock Prices Do Not Fully Reflect the Implications of Current Earnings for Future Earnings.pdf
│   └── In Search of Attention.pdf
│
├── Trading on Limited Attention Around Earnings Announcements
│
└── README.md
```

---

# Output

The `output/` directory contains generated figures, tables, and cached datasets used in the final report.

- **tables** – summary statistics and regression outputs  
- **figures** – drift plots, distributions, and strategy results  
- **final** – finalized outputs used in the report  
- **manual** – manually generated outputs  
- **cache** – intermediate datasets for faster execution  

---

# Results

The analysis finds evidence consistent with the PEAD anomaly:

- Positive earnings surprises are followed by **positive abnormal returns**  
- Negative surprises are followed by **negative drift**

Attention and congestion measures influence the magnitude of the drift, consistent with **limited investor attention**.

A simple long-short strategy based on earnings surprises produces a **positive Sharpe ratio**, with an **annualized Sharpe ratio of approximately 1.5–1.7 depending on specification**.

We also evaluate whether the documented drift can be translated into a simple trading strategy.

## Strategy Performance

We evaluate a simple long–short strategy based on the sign of the earnings surprise.

Strategy construction:

- **Long:** stocks with positive `CAR(0,1)` (positive earnings surprise)
- **Short:** stocks with negative `CAR(0,1)` (negative earnings surprise)

Performance summary:

| Metric | Value |
|------|------|
| Average daily return | ~0.021% |
| Annualized Sharpe Ratio | **~1.76** |

The annualized Sharpe ratio is computed as:

```
Sharpe = sqrt(252) × (mean daily return / daily return standard deviation)
```

The strategy produces a positive risk-adjusted return consistent with the **Post-Earnings-Announcement Drift anomaly**, particularly when conditioning on **low investor attention** and **high earnings announcement congestion**.

---

# Running the Project

Install required packages:

```
pip install pandas numpy matplotlib yfinance pytrends
```

Run notebooks in order:

```
01_prices_and_returns.ipynb  
02_earnings_events_and_surprise.ipynb  
03_google_trends_attention.ipynb  
04_merge_and_generate_report_results.ipynb  
```

---

# References

Bernard, V., & Thomas, J. (1990). *Evidence that stock prices do not fully reflect the implications of current earnings for future earnings.* Journal of Accounting and Economics.

Hirshleifer, D., Lim, S., & Teoh, S. (2009). *Driven to Distraction: Extraneous Events and Underreaction to Earnings News.* Journal of Finance.

Da, Z., Engelberg, J., & Gao, P. (2011). *In Search of Attention.* Journal of Finance.
