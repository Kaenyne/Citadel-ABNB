# L4 publication source audit v2

14 September 2026 · independent source worker · read-only audit of exact commit
`3da2903e2c78f6beea358819e7c561b07a5f49a3` on `codex/lane4-full`.
The user's explicit request to audit and push supersedes earlier notes that
withheld public-publication authorization. This reviewer did not push, contact
anyone, alter models or run a research fit. Only this new audit note was written.

## Verdict

**PASS for the reviewed publication payload, with two inherited source newline
conventions documented below. No secret, licensed raw export, oversized file or
accidental runtime payload was identified. All new final artifacts and accepted
source-bundle bytes match their committed hash bindings exactly.** The inherited
LF/CRLF differences affect two protected note references, not copied payload
bytes, financial values or substantive source content.

## Exact scope

The audit compares the L1/L2 base
`1c87628cedbc94ab8a0e8552743c94485ef353b8` with the target commit, including all
four intervening L4 commits: `e90ab0d`, `1039252`, `29b2d9a`, `3da2903`.
It includes the earlier L4 v1 artifacts and preserved development/review runs.

| Object | n | Result |
|---|---:|---|
| Added final-tree files | 1,056 | All scanned from committed Git blobs |
| Modified/deleted base files | 0 | Copy-preservation boundary intact |
| Logical final-tree payload size | 71,557,331 bytes | Approximately 68.24 MiB; duplicated audit history included |
| New reachable blob objects across four commits | 531 | Includes deduplicated final-tree content and history |
| Additional history-only blob versions | 11 | Prior workboard, README, hash manifests and test receipts inspected; no secret candidates |
| Generated L4 workbooks | 11 | All named ABNB_L4_review.xlsx outputs/recaptures; 165 ZIP members inspected |
| PDFs | 9 | Extracted text and metadata inspected |
| PNGs | 69 | Generated plots/previews; metadata inspected |
| Files larger than 10 MiB | 0 | Maximum 2,020,842 bytes |
| Credential-pattern candidates | 0 | No matched value was printed |
| Raw/licensed-export path candidates | 0 | No raw stores or licensed source exports added |
| Runtime/credential file candidates | 0 | No node_modules, venv, bytecode, credential store, cookies, databases or executable payload |

The largest file is the accepted cohort/currency recognition-weights CSV,
2,020,842 bytes, present in source and reproduction snapshots. All spreadsheets
are generated L4 models; there are no Bloomberg workbooks, Third Bridge PDFs or
LSEG Workspace raw exports. Public consensus numbers and source references are
retained as reviewed derived inputs. References to unavailable or licensed
sources in notes/manifests are not copied raw exports.

The content scan covered UTF-8 text, workbook XML/text ZIP members, PDF text and
metadata, and PNG metadata. It checked common private-key/token formats,
credential-bearing connection URLs and literal credential assignments. Local
provenance paths, test/build logs, repeated numerical snapshots and model
inspection records are intentional audit artifacts; no bundled interpreter,
dependency directory or accidental raw input was found. No credentials or
secret values were printed in audit output.

## Committed source and QA bindings

All checks read Git object bytes at the exact target commit. The accepted L3
research objects were independently addressed at research commit
`7fb6fe0f248d5492b899672b9b70545da62d63ee`; its relationship to bundle commit
`8821961853e4068febbfe2712f9a4e1036c9e629` was checked again.

| Binding group | n | Result |
|---|---:|---|
| Supplied source-manifest identity | 1 | Exact expected hash |
| Accepted bundle files | 108 | Exact |
| Full source snapshot entries | 124 | Exact |
| Research-output/note lineage | 104 | Exact committed source objects and payload copies |
| Actual research conversion acceptance bindings | 32 | Exact |
| Corresponding canonical bundle acceptance bindings | 27 | Exact |
| Final artifact receipt outputs | 18 | Exact |
| Final review source references | 31 | 29 exact; two inherited CRLF/LF equivalents |
| Final review captured inputs | 31 | All exact |
| Visual QA PDF/workbook bindings | 3 | Exact |
| Export QA source bindings | 5 | Exact |
| Independent final-review bindings | 91 | 89 exact; the same two inherited newline equivalents |
| **Total binding occurrences** | **575** | **571 exact; four newline-only occurrences across two inherited paths** |

The final artifact source ledger retains all 1,187 L3 disposition rows and their
original fields exactly, within 1,767 ledger rows. New workbook/model outputs,
accepted charts, copied support notes, review snapshots and bundle payloads
receive no newline exception.

### Explicit inherited-note newline reconciliation

Both paths below predate L4 and are unchanged by this branch. Their Git objects
use LF; the captured Windows source bytes use CRLF. Converting only LF to CRLF
in the committed text reproduces the recorded captured-source hash exactly.
The captured review copies themselves bind byte-for-byte to their recorded
hashes. No source content normalization or rewrite was performed.

| Inherited source | Git LF SHA256 | Captured CRLF SHA256 |
|---|---|---|
| `LANE2_MEMO_READY_CLAIMS.md` | `2deffd44bd77e9ce30a22bf0b9551b4f6e35146283b672a50a6ca72867dc7c11` | `5b54b1c2e6fdd62f8cc84ff9602b02a364d1df9507886bb132ee45712aa59d3a` |
| `ALPHA_F_RNPL.md` | `1a66fe918eccd76caaaa5f82356e3c77460c35473cedc55f86ce1a2676df0338` | `636850c6c887cd0efecd05322f2a8d2a59ab2146aa5ed13bcca4a115d024b6ee` |

Both paths are under `docs/revenue-forecast-strategy/05_backtests/`. Each appears
once in the final input manifest and once in the independent review's checked
hash table. A strict initial byte comparison stopped at the first inherited
note; the completed audit explicitly classified only these existing-file
newline differences and still required exact bytes for every newly added file.

Final publication anchors:

- Source manifest: `9a8563fff0142d51fd3537699899f032165a69a6c1db9cad6c4b24d450952970`.
- Final memo `deck/drafts/lane4_v2/review_v2/review_memo.pdf`:
  `53e102eeca2dcda418368924cacb9a28486f3274332ba0b06fc804a6b1fe0187`.
- Final workbook `model/lane4_v2/outputs/lane4_model/snapshot_v2/ABNB_L4_review.xlsx`:
  `882b6d7b321d2f791fecc9b1d7ec57265b5e2fdcedd705326ee7bd3ee9ce6f92`.

## Commands and limits

Read-only inventory used `git diff --name-status -z BASE TARGET`,
`git rev-list --objects BASE..TARGET`, `git ls-tree -r TARGET`, and binary
`git cat-file --batch` / `--batch-check`. Python standard-library hashing,
CSV/JSON parsing, regex scanning and ZIP inspection were used, with pypdf/Pillow
for PDF text and image metadata. Final committed-binding verification exited 0
in 3.12 tool-wall seconds; history-only verification exited 0 in 1.30 seconds.
No model runner or fitting procedure was executed in this audit. Parent owns
the separate tests, artifact/numerical checks, remote check and push.

The scan addresses common detectable secret formats and the enumerated payload;
it does not claim a universal proof that arbitrary text can never be sensitive.
The committed package remains unsigned investment research with its existing
source, accounting and forecast limitations.

## RESUME

Parent may complete the separately authorized publication after its tests and
remote/artifact checks pass. Preserve the reviewed commit and its existing
source bytes. Include this new audit note in a documentation-only follow-up if
desired; no model or payload repair is required. The two inherited newline
identities above are resolved audit metadata, not pending permission requests.
