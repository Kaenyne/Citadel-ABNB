# L3 fee-panel independent review v1

Reviewer `adr_hotel` (did not author fee package) · 2026-09-13 · `codex/lane3-full`. Reviewed `fee_panel_v1/run.py`, `test_fee_panel.py`, original preregistration, frozen capture/sample construction and published output. No fee implementation was edited by this reviewer; findings were sent to the lead for repair.

## Verdict

**Four material implementation/provenance findings were found and the lead's initial repairs are verified.** The current 18 tests pass, including five regression checks corresponding to the independent attacks. One follow-on interaction remains for the lead to resolve: applying new metadata to the historical September 11 dry-run diagnostic can block otherwise admissible September 14+ work. Future fee captures and causal pass-through remain unavailable/unidentified independently of implementation status.

## Original findings, preserved

| Finding | Independent counterexample | Required correction | Initial repair status |
|---|---|---|---|
| P1: failed unknown-attribute strata bypassed 40% gate | In synthetic 40-listing panel, set 8 known-residence listings' room type to unknown and remove both post dates. That stratum has 0% retention, but pooled estimator returned `association_precision_pass`, n=64 listing/stay rows. | Only unknown **residence** is excluded from the primary population. Unknown bedroom/room/host-class strata among known residents must still pass their gate. | Verified: revised population-specific overlap marks this stratum primary and returns `blocked_overlap`. |
| P2: unknown-residence descriptive overlap disappeared when waves complete | Mark listing 0 residence unknown. It is correctly excluded from estimation, but output overlap contained no unknown-residence row at all. | Publish all-descriptive overlap separately from known-residence primary gates. | Verified: three descriptive unknown-residence rows retained, never primary. |
| P1: absent listing country silently got standard fee denominator | Remove MX country labels from otherwise valid known-residence synthetic rows. Planted theta 0.7000 became 0.7105394 and still precision-passed because blanks mapped to 15.5%. | Fail on missing/invalid listing-country fee regime for primary candidates; never assume standard for an unknown regime. | Verified: known-residence missing fee-regime rows now raise ValueError. |
| P1: metadata need only precede final as-of, not the actual pre observation | Metadata stamped September 18 was accepted at as-of September 19 for a wave whose pre capture was September 14. | Enforce metadata availability no later than each matched capture, or use a separately fixed baseline metadata vintage. | Verified: per-capture merge checks reject metadata dated after pre capture. Missing metadata dates now fail explicitly rather than through an incidental pandas comparison error. |

The independent probes loaded the source and fixture module with `importlib`, disabled bytecode, and used temporary files only. The unknown-room attack used `listing_id in 0..7`, two fixed stays/listing, and the fixture's exact 0.7 repricing rule. Output before repair was `association_precision_pass`, n=64, unknown-room retention 0, gate false; unknown-residence reporting false; missing-MX-country theta 0.710539403166. The missing-date initial probe failed closed with TypeError, so it was not claimed as a successful provenance bypass. The lead preserved the original output and rebuilt to `fee_panel_v1/reviewed_v2` after repairs.

## Verification command

```powershell
& 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -B -m pytest analysis/src/forecast_methods/fee_panel_v1/test_fee_panel.py -q -p no:cacheprovider
```

Exit 0; 18 tests passed in 7.20 seconds. Read-through verifies `panel_overlaps` separates `all_descriptive` and `known_residence_primary`, primary candidates require an explicit country code, and `load_captures` compares matched metadata dates against actual capture dates. This command and the five new tests directly repeat the initially reported attacks.

## Follow-on interaction requiring closeout

`run()` always reloads the fixed `dryrun_new-orleans_2026-09-11.csv` using the caller's metadata. After the correct per-capture date repair, a legitimate new metadata snapshot dated September 13 (before the September 14 pre observation) is inadmissible for the old September 11 dry run. Thus the archival diagnostic could fail the entire later-wave consumer despite the primary wave using admissible data. The diagnostic must instead use its original frozen sample metadata and record that separate source, or be explicitly skipped/marked unavailable for an incompatible new metadata vintage. It must not weaken the primary metadata date guard. This interaction was sent separately to the lead for repair; a new closeout note should record the result.

## Economic, statistical and scope checks that survived

The logarithmic denominator is `log(0.97/0.845)` for the stated 15.5% new-fee regime and `log(0.97/0.84)` for Mexico/Brazil's 16% regime. It is not the arithmetic neutral repricing percentage. The old 3% host fee is explicitly a conditional mechanics assumption. Country controls the fee regime; host residence determines the deadline arm. The `host_region_guess` source is a coarse parse of self-reported host location, with no listing-country fallback; calling this a validated residence classification would be unsupported.

The response is mean post log listed price minus pre log listed price on the same listing/stay, with stay-window fixed effects and listing-cluster covariance. Two stays for one listing are not two independent clusters. The estimator reports cluster count and at least two clusters per arm; four total clusters is a minimal computational support rule, not a reliable general power guarantee. Very precise synthetic fits do not establish empirical power. Requiring every nonempty stratum can make the live estimate underpowered; this is the locked preregistration, and sparse strata cannot be pooled away after outcomes are seen.

Both waves have exactly one pre observation, so a pre-trend cannot be tested. October non-EEA controls are already treated and rely on an unverified stable-comparator assumption. Early migration, actual switch-date uncertainty, search-rank composition and market-specific time changes remain possible confounders. Fixed listing differences remove fixed levels, not those time-varying confounders. The code keeps `causal_identified=false`, listed prices never become verified guest totals, no missing theta becomes zero, and no precision pass automatically enters an ABNB revenue forecast.

Actual 2026-09-13 output has zero scheduled capture files, both waves unavailable, and W1/W2 n=0. The old dry run has 225 valid rows, 207 listings and only six rows with residence metadata; the sample size of 2,600 does not guarantee observed matched coverage. Current output makes no empirical theta or fee-uplift claim. Future captures are checked by actual timestamps rather than filename dates, currencies cannot change within a listing/stay, duplicate capture keys are refused, and existing output directories are immutable.

## RESUME

The lead should repair the archival-diagnostic metadata interaction, rerun tests and preserve a new closeout note. Then the consumer can be implementation complete while both empirical waves remain pending. The next authorised step is consuming already scheduled captures with dated metadata in a new output version; it is not new collection, job modification, causal labeling or L4 fee adoption. An eventual precision pass remains a conditional listed-price deadline association requiring a separate economic bridge before replacing any fee mechanism.
