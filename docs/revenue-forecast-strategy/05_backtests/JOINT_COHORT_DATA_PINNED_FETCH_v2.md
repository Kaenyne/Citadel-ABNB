# GE-JOINT-DATA — pinned-source verification attempt

Codex data subagent · 15 September 2026 · additive supplement to `JOINT_COHORT_DATA_v1.md`.

## Verdict

**Blocked by local network socket permissions.** The follow-on raw-source completeness check could not be performed. This is not a source-data failure. The v1 stored-lineage audit remains valid with its explicitly stated qualification.

The parent requested a bounded public fetch of one or two pinned EUROCONTROL files, expanding to 17 quarter vintages only if readily accessible. One request was attempted; zero bytes were received and there were no further requests, downloads or original-output changes.

## Exact command and result

```powershell
@'
import urllib.request, hashlib
u='https://raw.githubusercontent.com/euctrl-pru/daio/c3d58c5cd2f274c51ced8352bf6b770716355411/daio_2026.csv'
try:
    with urllib.request.urlopen(u, timeout=12) as r: b=r.read(2000000)
    print({'ok':True,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'header':b.splitlines()[0].decode()})
except Exception as e:
    print({'ok':False,'error':repr(e)})
'@ | & 'C:/Users/wille/Desktop/Citadel - ABNB/.venv/Scripts/python.exe' -
```

Process exit 0 because the diagnostic catches and prints the exception; request outcome `ok=False`. Error: `URLError(PermissionError(13, 'An attempt was made to access a socket in a way forbidden by its access permissions', None, 10013, None))`. Request completed in under three seconds. A machine-readable receipt is saved at `data/processed/forecast_methods/gbv_joint_cohort_v1/data_audit_v2/pinned_fetch_attempt.json`.

No escalation was requested because the parent explicitly directed stopping promptly if network access was blocked. No original git mirror or checkout was mutated. No forecasts registered and no scorer run required.

## RESUME

Continue the preregistered forecast ablation using the stored PIT rows and v1 qualifications. When the same public pinned files are accessible, compare both current/prior-year75-day sums and full40-state-per-day coverage at each referenced commit, writing a new verification version. Do not substitute a current HEAD file for an original historical vintage or remove the raw-recertification qualification until that check is complete.
