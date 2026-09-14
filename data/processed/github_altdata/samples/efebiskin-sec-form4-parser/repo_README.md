# sec-form4-parser

> A clean, typed Python parser for SEC Form 4 insider-trading XML filings. Zero runtime dependencies. Optional EDGAR fetcher with rate limiting.

![tests](https://img.shields.io/badge/tests-13%2F13_passing-brightgreen)
![python](https://img.shields.io/badge/python-3.9%2B-3776AB?logo=python&logoColor=white)
![license: MIT](https://img.shields.io/badge/license-MIT-green.svg)
![dependencies](https://img.shields.io/badge/runtime_deps-0-brightgreen)

Form 4 is the SEC filing that corporate insiders — officers, directors, and 10%+ owners — must submit when their ownership of company stock changes. It's one of the few *truthful* signals in markets: insiders file because they have to, not because they want to.

The filings are public. The XML is … less friendly than you'd hope. This package makes it easy.

```python
from sec_form4_parser import parse

filing = parse("form4.xml")

print(filing.issuer.name, filing.issuer.trading_symbol)
for t in filing.purchases:
    print(t.transaction_date, t.shares, "@", t.price_per_share)
```

---

## Install

```bash
pip install sec-form4-parser
```

Or from source:

```bash
git clone https://github.com/efebiskin/sec-form4-parser
cd sec-form4-parser
pip install -e .
```

Python 3.9+. No runtime dependencies (`xml.etree` + `urllib` from stdlib).

---

## Features

- **Typed dataclasses** — `Form4Filing`, `Issuer`, `Reporter`, `Transaction` are frozen dataclasses with real types, not dict-of-dicts.
- **Enum-safe transaction codes** — the full SEC code set (`P`, `S`, `A`, `D`, `M`, `F`, `G`, `V`, …) as `TransactionCode`, with an unknown-code pathway that degrades to `None` instead of crashing.
- **Tolerant parsing** — real Form 4 filings omit fields the schema calls required. Every optional path is `Optional[...]` in the type signature; the parser never raises on missing leaves.
- **Convenience aggregates** — `filing.purchases`, `filing.sales`, `filing.total_purchase_value`.
- **EDGAR fetcher** (optional) — rate-limited at 10 req/sec per SEC's fair-use policy, with a mandatory `user_agent` parameter so you don't accidentally get your IP banned.
- **CLI** — `form4 parse file.xml` (human summary) or `form4 parse file.xml --json`.
- **Zero runtime dependencies.**

---

## Usage

### Parse a local file

```python
from sec_form4_parser import parse

filing = parse("primary_doc.xml")   # path, str, bytes, or ElementTree
print(filing.summary())
```

```
Form 4 — Apple Inc. (AAPL)
  CIK:    0000320193
  Period: 2024-03-15
  Reporters (1):
    - JANE DOE [officer (Chief Financial Officer)]
  Transactions: 2 non-derivative, 0 derivative
  Purchases:   1 ($1,724,500.00)
  Sales:       1 ($86,550.00)
```

### Fetch from EDGAR

```python
from sec_form4_parser import fetch, edgar_archive_url

url = edgar_archive_url(cik="0000320193", accession="0001127602-24-010195")
filing = fetch(url, user_agent="Your Name your@email.com")
```

The SEC requires a descriptive `User-Agent` identifying the requester ([reference](https://www.sec.gov/developer)). Without one, you'll be rate-limited or blocked.

### Filter for open-market officer purchases

```python
for filing in filings:
    officer_buys = [
        t for t in filing.purchases
        if any(r.is_officer for r in filing.reporters)
    ]
    for t in officer_buys:
        print(
            filing.issuer.trading_symbol,
            t.transaction_date,
            f"{int(t.shares):,} sh",
            f"@ ${t.price_per_share}",
        )
```

### CLI

```bash
form4 parse primary_doc.xml
form4 parse primary_doc.xml --json | jq '.purchases[].shares'

form4 fetch \
  https://www.sec.gov/Archives/edgar/data/320193/000112760224010195/primary_doc.xml \
  --user-agent "Your Name your@email.com"
```

---

## Data model

```
Form4Filing
├── schema_version        str | None
├── document_type         str            # "4" or "4/A"
├── period_of_report      date | None
├── issuer                Issuer
│   ├── cik               str
│   ├── name              str
│   └── trading_symbol    str | None
├── reporters             list[Reporter]
│   ├── cik, name
│   ├── is_director, is_officer, is_ten_percent_owner, is_other
│   ├── officer_title     str | None
│   └── roles             property -> list[str]
├── non_derivative        list[Transaction]
└── derivative            list[Transaction]
    └── Transaction
        ├── security_title
        ├── transaction_date     date | None
        ├── transaction_code     TransactionCode | None
        ├── shares               Decimal | None
        ├── price_per_share      Decimal | None
        ├── acquired_disposed    AcquiredDisposed | None   (A | D)
        ├── shares_owned_following Decimal | None
        ├── ownership            Ownership | None          (D | I)
        ├── is_derivative        bool
        ├── total_value          property -> Decimal | None
        ├── is_purchase          property -> bool          (code P + acquired A)
        └── is_sale              property -> bool          (code S + disposed D)
```

`Decimal` is used for shares and prices so you never eat a floating-point rounding bug when summing transactions.

---

## Why the `P + A` filter matters

A transaction with code `P` alone is not the same as an open-market **purchase**. Some filings carry code `P` with `acquired_disposed = D` (reversing a prior accidental report), and a code `A` alone just means "grant" (awarded, not purchased). The `is_purchase` property enforces the conjunction academia calls "open-market buy":

```python
transaction.transaction_code == TransactionCode.OPEN_MARKET_PURCHASE
and transaction.acquired_disposed == AcquiredDisposed.ACQUIRED
```

This matches the filter used in Lakonishok & Lee (2001) and Seyhun (1998), the canonical insider-trading edge papers.

---

## Testing

```bash
pip install -e .[dev]
pytest
```

13 tests covering:
- issuer / reporter / transaction extraction
- multi-reporter filings
- derivative-only filings
- parsing from `Path`, `str`, `bytes`
- convenience aggregates (`purchases`, `sales`, `total_purchase_value`)
- malformed XML + wrong root rejection
- unknown transaction code degrades to `None`
- EDGAR archive URL builder

---

## License

MIT — see [LICENSE](LICENSE).

---

## Acknowledgments

- SEC EDGAR for making filings freely available.
- Lakonishok & Lee (2001), *"Are Insider Trades Informative?"* — Review of Financial Studies.
- Seyhun (1998), *Investment Intelligence from Insider Trading*.
