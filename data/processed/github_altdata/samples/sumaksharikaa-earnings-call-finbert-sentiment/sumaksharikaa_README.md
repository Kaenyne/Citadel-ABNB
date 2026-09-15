# 📈 Earnings Call NLP Analyzer

FinBERT-powered sentiment analysis on 18,755 earnings call transcripts from major US companies.

## Key Results
- Analyzed **514 transcripts** across **30 companies** and **8 sectors**
- Used **FinBERT** (finance-specific BERT) for domain-accurate sentiment scoring
- Identified **Wells Fargo and Goldman Sachs** as highest risk-language users
- **AMD and Netflix** showed most consistently positive earnings language
- Detected COVID-19 impact: Disney Q3 2020 showed negative sentiment (-0.053) during park closures

## Tech Stack
Python · HuggingFace Transformers · FinBERT · pandas · Streamlit · matplotlib

## Features
- Sentiment score by company and sector
- Quarter-over-quarter sentiment trend
- Risk language ratio analysis
- Interactive filters by sector and company

## Dataset
Motley Fool scraped earnings call transcripts (2017–2022), 18,755 transcripts across 2,876 tickers.

---
*Built by Sumaksharika Nainavarapu | [Portfolio](https://sumaksharika.com)*

## 🌐 Live Demo
**[View Live Dashboard](https://earnings-call-nlp-hpvrwqwv6rrtxknzwt2seb.streamlit.app)**
