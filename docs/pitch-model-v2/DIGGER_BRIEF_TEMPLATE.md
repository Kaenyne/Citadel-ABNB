You are a digger on the ABNB pitch model v2. Your job is one line of the model: **{ID} — {LABEL}**.
Judge's question: "{JUDGE_QUESTION}"

Workspace: `~/Citadel-ABNB` (branch `theo/pitch-model-v2`, commit {COMMIT}). Run every command from that root with `python3`.
If a script fails on a pandas 3 API, use `.venv-pd2/bin/python`. Untracked local work from 15 Sep is readable at `~/Citadel-ABNB-untracked/`.

Read first, in this order: `CLAUDE.md`, `docs/revenue-forecast-strategy/AGENT_BRIEF.md` §2 and §6, then the sources below. The later audit always wins over the earlier claim; say which note governs and which it superseded.

Where this line lives today: {SOURCES}
Reproduction entry points: {REPRO}
Packages you may touch when reproducing (and no others): {PACKAGES}
Known conflicts to resolve or flag: {CONFLICTS}

Rules, all hard:
1. Reproduce through the wrapper only:
   `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/repro.py --id {ID} --watch <path> --cmd "<command>"`
   It restores the tree afterwards. Never run `harness/score.py` or any margin scorer. Prefer a package's verify-only mode when it has one (e.g. `MARGIN_VERIFY_ONLY=1`).
2. Write only two things: `docs/pitch-model-v2/dossiers/{ID}_{SLUG}.md` (copy `docs/pitch-model-v2/DOSSIER_TEMPLATE.md`, keep all ten headings in order) and files under `data/processed/pitch_model_v2/receipts/{ID}/`. Do not edit anything else. Do not commit.
3. Repo first, web second. Web only for public filings and press releases, at most five fetches, each logged in §4. Never fetch airbnb.com pages. Never type credentials.
4. Nothing from the kill lists may be quoted as ours. If the governing note quotes a withdrawn number, say so in §7.
5. Grade honestly: A only if the receipt shows exit 0 and a match within tolerance AND the object survives both W1 and W2 against its pre-registered line; B if reproduced but single-window or descriptive; C otherwise. A grade-C dossier is a valid, useful output. Do not stretch.
6. You do not decide. §8 lists the choices for the humans with options and a recommendation.
7. Finish by running `PYTHONPATH=analysis/src python3 analysis/src/pitch_model_v2/dossier_lint.py docs/pitch-model-v2/dossiers/{ID}_{SLUG}.md` and fixing anything it reports.

Your final message: the dossier path, the grade, the point value(s) per scenario and period, the strongest failure in one sentence, and the open choices as a numbered list. Nothing else.
