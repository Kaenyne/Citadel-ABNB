# Citadel-ABNB

Team workspace for the **Harvard FAC x Citadel Intercollegiate Stock Pitch** - our pitch on **Airbnb (NASDAQ: ABNB)**.

> Edit this header if the competition or ticker changes. Everything else in the repo is ticker-agnostic.

## Where things live

| Folder | What goes here | Owner |
|---|---|---|
| `research/` | Thesis, catalysts, risks, notes on filings/transcripts, competitor work | Everyone |
| `model/` | The Excel/Sheets financial model and its written assumptions | Model lead |
| `data/` | Raw downloads (`raw/`) and cleaned datasets (`processed/`) | Data lead |
| `analysis/` | Python notebooks/scripts and the charts they produce | Data lead |
| `deck/` | Slide drafts and the final submitted deck | Deck lead |
| `docs/` | Competition rules/rubric/timeline, meeting notes, team decisions | Everyone |

Start with [`research/thesis.md`](research/thesis.md) - it is the single source of truth for the pitch. Slides and the model should follow it, not the other way around.

## Getting started

```bash
git clone https://github.com/Kaenyne/Citadel-ABNB.git
cd Citadel-ABNB
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## How we work

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) - branch naming, PR flow, and how we handle Excel and large files. Short version:

1. Never commit directly to `main`. Branch, open a PR, get one teammate to look at it.
2. Excel/PowerPoint files are binary and can't be merged. Only one person edits the model or deck at a time - claim it in the group chat first.
3. Big data files (>50 MB) and paid-source PDFs do **not** go in git. Link to them in `research/sources/README.md` instead.

## Key dates

See [`docs/TIMELINE.md`](docs/TIMELINE.md).
