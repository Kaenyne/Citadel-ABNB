# Contributing

## Branches

- `main` is always the current best version of the pitch. Don't push to it directly.
- Branch names: `<name>/<short-topic>` - e.g. `krish/valuation-dcf`, `sam/competitor-bkng`.
- Keep branches small and short-lived. Merge within a few days; long-lived branches rot.

## Pull requests

1. Open a PR against `main` and fill in the template.
2. Tag one teammate for review. Reviewer checks that numbers tie to the model and claims are sourced.
3. Squash-merge, then delete the branch.

## Commits

Write the *why*, not just the *what*: `Add take-rate sensitivity to model (bull case was too aggressive)` beats `update model`.

## Binary files (Excel, PowerPoint, PDF)

Git can't merge these. Rules:

- **One editor at a time.** Post "grabbing the model" / "releasing the model" in the group chat.
- Keep the *live* model at `model/ABNB_model.xlsx`. Don't create `model_v2_FINAL_real.xlsx` - git history is the version control.
- When you change a model assumption, also update `model/assumptions.md` so the change is reviewable in the PR diff.
- Same for the deck: `deck/drafts/` for work-in-progress, `deck/final/` only for the submitted version.

## Data

- `data/raw/` - untouched downloads. Never edit by hand. Add a line to `data/README.md` saying where it came from and when.
- `data/processed/` - outputs of scripts in `analysis/src/`. Should be reproducible from raw.
- Files over 50 MB: don't commit. Put them in the shared Drive and link from `data/README.md`.
- Anything from Bloomberg, CapIQ, FactSet, or another licensed terminal: **do not commit the raw export** to this public repo. Store it in the private shared Drive and commit only derived aggregates/charts.

## Sources

Every number in the deck needs a source. Log them in `research/sources/README.md` as you go, not at the end.

## Python

- Use the repo venv (`.venv/`, gitignored) and `requirements.txt`. If you add a package, add it to `requirements.txt` in the same PR.
- Notebooks: clear outputs before committing (Kernel > Restart & Clear Output) so diffs stay readable.
- Reusable code goes in `analysis/src/`, not copy-pasted between notebooks.
