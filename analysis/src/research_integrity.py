"""Small validation and file-integrity helpers for the churn/hotel research only."""
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import tempfile


def finite_number(value, name, *, minimum=None, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{name} must be a finite number, not a boolean or missing value')
    if minimum is not None and value < minimum or maximum is not None and value > maximum:
        raise ValueError(f'{name} outside allowed range [{minimum}, {maximum}]')
    return value


def observed_count(value, name):
    if value is None or value == '':
        return None
    if isinstance(value, bool):
        raise ValueError(f'{name} cannot be a boolean')
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'{name} must be an observed nonnegative integer') from exc
    if not math.isfinite(number) or number < 0 or not number.is_integer():
        raise ValueError(f'{name} must be an observed nonnegative integer')
    return int(number)


def atomic_write_csv(path, rows, fields=None):
    """Validate/serialize before replacing an output; retain it on validation failure."""
    rows = list(rows)
    if fields is None:
        if not rows:
            raise ValueError(f'Explicit schema required for empty output: {path}')
        fields = list(rows[0])
    buffer = io.StringIO(newline='')
    writer = csv.DictWriter(buffer, fieldnames=fields, extrasaction='raise')
    writer.writeheader()
    writer.writerows(rows)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='',
                                         dir=path.parent, prefix=path.name+'.', suffix='.tmp', delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(buffer.getvalue())
        temporary.replace(path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def verify_sha256(path, expected):
    with Path(path).open('rb') as handle:
        actual = hashlib.file_digest(handle, 'sha256').hexdigest()
    if not expected or actual != expected:
        raise ValueError(f'Capture checksum changed: {path}')
    return actual


def verify_frozen_report(root, script):
    """Dated prose contains fixed claims: changed inputs require a new editorial audit."""
    root = Path(root)
    manifest = json.loads((root / 'analysis/config/churn_hotel_report_inputs.json').read_text(encoding='utf-8'))
    inputs = manifest['reports'][script]
    if not inputs:
        raise ValueError('A dated report must have a frozen input manifest')
    for name, expected in inputs.items():
        # Git normalizes newlines; the guard must work on both Windows and Unix.
        data = (root / name).read_bytes().replace(b'\r\n', b'\n')
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f'Frozen report input changed: {name}; audit the dated narrative before regenerating it')


def validate_selection(rows, selected_dates):
    """Counts alone cannot distinguish a complete acquisition from duplicated rows."""
    keys = [(r['market'], r['snapshot_start']) for r in rows]
    expected = [(r['market'], r['date']) for r in selected_dates]
    if not keys or len(keys) != len(set(keys)) or len(expected) != len(set(expected)) or set(keys) != set(expected):
        raise ValueError('Acquisition has duplicate, missing, or unexpected market/date identities')
