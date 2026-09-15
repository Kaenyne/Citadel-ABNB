"""XML parser for SEC Form 4 `<ownershipDocument>` filings.

The parser is intentionally tolerant of missing fields — real-world filings
omit values more often than the schema suggests. Callers should rely on
Optional typing rather than assuming required fields are populated.
"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional, Union
from xml.etree import ElementTree as ET

from .models import (
    AcquiredDisposed,
    Form4Filing,
    Issuer,
    Ownership,
    Reporter,
    Transaction,
    TransactionCode,
)


XmlInput = Union[str, bytes, Path, ET.Element]


class Form4ParseError(ValueError):
    """Raised when the input is not a well-formed Form 4 document."""


# -----------------------------------------------------------------------------
# Small element-access helpers. Form 4 nests most scalars under <value>.
# -----------------------------------------------------------------------------
def _text(elem: Optional[ET.Element], path: str) -> Optional[str]:
    if elem is None:
        return None
    node = elem.find(path)
    if node is None:
        return None
    if node.text is not None and node.text.strip():
        return node.text.strip()
    value = node.find("value")
    if value is not None and value.text:
        return value.text.strip()
    return None


def _decimal(elem: Optional[ET.Element], path: str) -> Optional[Decimal]:
    raw = _text(elem, path)
    if raw is None:
        return None
    try:
        return Decimal(raw.replace(",", ""))
    except (InvalidOperation, AttributeError):
        return None


def _date(elem: Optional[ET.Element], path: str) -> Optional[date]:
    raw = _text(elem, path)
    if not raw:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _bool(elem: Optional[ET.Element], path: str) -> bool:
    raw = _text(elem, path)
    if raw is None:
        return False
    return raw.strip() in {"1", "true", "True"}


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------
def parse(source: XmlInput) -> Form4Filing:
    """Parse a Form 4 from an XML string, bytes, file path, or ElementTree.

    Raises Form4ParseError if the XML is invalid or missing required root.
    """
    root = _load(source)
    if root.tag != "ownershipDocument":
        raise Form4ParseError(
            f"expected root <ownershipDocument>, got <{root.tag}>"
        )

    return Form4Filing(
        schema_version=_text(root, "schemaVersion"),
        document_type=_text(root, "documentType") or "4",
        period_of_report=_date(root, "periodOfReport"),
        issuer=_parse_issuer(root),
        reporters=[_parse_reporter(r) for r in root.findall("reportingOwner")],
        non_derivative=[
            _parse_transaction(t, derivative=False)
            for t in root.findall("nonDerivativeTable/nonDerivativeTransaction")
        ],
        derivative=[
            _parse_transaction(t, derivative=True)
            for t in root.findall("derivativeTable/derivativeTransaction")
        ],
        not_subject_to_section16=_bool(root, "notSubjectToSection16"),
    )


def _load(source: XmlInput) -> ET.Element:
    if isinstance(source, ET.Element):
        return source
    if isinstance(source, (bytes, bytearray)):
        return _fromstring(source)
    if isinstance(source, Path) or (isinstance(source, str) and len(source) < 4096 and Path(source).exists()):
        return ET.parse(str(source)).getroot()
    if isinstance(source, str):
        return _fromstring(source)
    raise Form4ParseError(f"unsupported source type: {type(source).__name__}")


def _fromstring(data) -> ET.Element:
    try:
        return ET.fromstring(data)
    except ET.ParseError as e:
        raise Form4ParseError(f"malformed XML: {e}") from e


# -----------------------------------------------------------------------------
# Sub-parsers
# -----------------------------------------------------------------------------
def _parse_issuer(root: ET.Element) -> Issuer:
    node = root.find("issuer")
    if node is None:
        raise Form4ParseError("missing <issuer>")
    return Issuer(
        cik=_text(node, "issuerCik") or "",
        name=_text(node, "issuerName") or "",
        trading_symbol=_text(node, "issuerTradingSymbol"),
    )


def _parse_reporter(node: ET.Element) -> Reporter:
    rid = node.find("reportingOwnerId")
    rel = node.find("reportingOwnerRelationship")
    return Reporter(
        cik=_text(rid, "rptOwnerCik") or "",
        name=_text(rid, "rptOwnerName") or "",
        is_director=_bool(rel, "isDirector"),
        is_officer=_bool(rel, "isOfficer"),
        is_ten_percent_owner=_bool(rel, "isTenPercentOwner"),
        is_other=_bool(rel, "isOther"),
        officer_title=_text(rel, "officerTitle"),
        other_text=_text(rel, "otherText"),
    )


def _parse_transaction(node: ET.Element, *, derivative: bool) -> Transaction:
    coding = node.find("transactionCoding")
    amounts = node.find("transactionAmounts")
    post = node.find("postTransactionAmounts")
    nature = node.find("ownershipNature")

    shares_owned = (
        _decimal(post, "sharesOwnedFollowingTransaction")
        if not derivative
        else _decimal(post, "sharesOwnedFollowingTransaction")
    )

    return Transaction(
        security_title=_text(node, "securityTitle") or "",
        transaction_date=_date(node, "transactionDate"),
        transaction_code=TransactionCode.from_raw(_text(coding, "transactionCode")),
        shares=_decimal(amounts, "transactionShares"),
        price_per_share=_decimal(amounts, "transactionPricePerShare"),
        acquired_disposed=_enum_or_none(AcquiredDisposed, _text(amounts, "transactionAcquiredDisposedCode")),
        shares_owned_following=shares_owned,
        ownership=_enum_or_none(Ownership, _text(nature, "directOrIndirectOwnership")),
        is_derivative=derivative,
    )


def _enum_or_none(enum_cls, raw: Optional[str]):
    if not raw:
        return None
    try:
        return enum_cls(raw.strip().upper())
    except ValueError:
        return None
