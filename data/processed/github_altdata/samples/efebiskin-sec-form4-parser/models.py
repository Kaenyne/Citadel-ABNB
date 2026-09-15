"""Typed dataclasses representing an SEC Form 4 filing.

Form 4 is filed by corporate insiders (officers, directors, 10%+ owners) to
disclose changes in their ownership. This module models the filing in a
strongly-typed, Pythonic way so downstream code can work with attributes
instead of raw XML paths.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import List, Optional


# -----------------------------------------------------------------------------
# Transaction codes (SEC-defined). Full list:
#   https://www.sec.gov/about/forms/form4data.pdf
# -----------------------------------------------------------------------------
class TransactionCode(str, Enum):
    OPEN_MARKET_PURCHASE = "P"      # Open market or private purchase
    OPEN_MARKET_SALE = "S"          # Open market or private sale
    GRANT_AWARD = "A"               # Grant, award, or other acquisition
    DISPOSITION_TO_ISSUER = "D"     # Disposition to the issuer
    EXERCISE_DERIVATIVE = "M"       # Exercise or conversion of derivative
    TAX_WITHHOLDING = "F"           # Payment of exercise price/tax via shares
    GIFT = "G"                      # Bona fide gift
    EARLY_REPORT = "V"              # Voluntary early report
    EXPIRATION_SHORT_DERIV = "E"    # Expiration of short derivative
    EXPIRATION_LONG_DERIV = "H"     # Expiration of long derivative
    EXERCISE_OUT_OF_MONEY = "X"     # Exercise of out-of-the-money derivative
    INHERITANCE = "W"               # Acquisition/disposition via will/laws
    DISCRETIONARY_TRANSACTION = "I" # Discretionary transaction
    OTHER = "J"                     # Other (see footnotes)

    @classmethod
    def from_raw(cls, raw: Optional[str]) -> Optional["TransactionCode"]:
        if not raw:
            return None
        raw = raw.strip().upper()
        try:
            return cls(raw)
        except ValueError:
            return None


class AcquiredDisposed(str, Enum):
    ACQUIRED = "A"
    DISPOSED = "D"


class Ownership(str, Enum):
    DIRECT = "D"
    INDIRECT = "I"


@dataclass(frozen=True)
class Issuer:
    cik: str
    name: str
    trading_symbol: Optional[str] = None


@dataclass(frozen=True)
class Reporter:
    """The insider filing the form."""
    cik: str
    name: str
    is_director: bool = False
    is_officer: bool = False
    is_ten_percent_owner: bool = False
    is_other: bool = False
    officer_title: Optional[str] = None
    other_text: Optional[str] = None

    @property
    def roles(self) -> List[str]:
        out = []
        if self.is_director: out.append("director")
        if self.is_officer: out.append("officer" + (f" ({self.officer_title})" if self.officer_title else ""))
        if self.is_ten_percent_owner: out.append("10%+ owner")
        if self.is_other: out.append("other" + (f" ({self.other_text})" if self.other_text else ""))
        return out


@dataclass(frozen=True)
class Transaction:
    """A single non-derivative or derivative transaction row."""
    security_title: str
    transaction_date: Optional[date]
    transaction_code: Optional[TransactionCode]
    shares: Optional[Decimal]
    price_per_share: Optional[Decimal]
    acquired_disposed: Optional[AcquiredDisposed]
    shares_owned_following: Optional[Decimal]
    ownership: Optional[Ownership]
    is_derivative: bool = False

    @property
    def total_value(self) -> Optional[Decimal]:
        if self.shares is None or self.price_per_share is None:
            return None
        return self.shares * self.price_per_share

    @property
    def is_purchase(self) -> bool:
        return (
            self.transaction_code == TransactionCode.OPEN_MARKET_PURCHASE
            and self.acquired_disposed == AcquiredDisposed.ACQUIRED
        )

    @property
    def is_sale(self) -> bool:
        return (
            self.transaction_code == TransactionCode.OPEN_MARKET_SALE
            and self.acquired_disposed == AcquiredDisposed.DISPOSED
        )


@dataclass(frozen=True)
class Form4Filing:
    """A complete Form 4 filing, after parsing."""
    schema_version: Optional[str]
    document_type: str
    period_of_report: Optional[date]
    issuer: Issuer
    reporters: List[Reporter] = field(default_factory=list)
    non_derivative: List[Transaction] = field(default_factory=list)
    derivative: List[Transaction] = field(default_factory=list)
    not_subject_to_section16: bool = False

    # -- Convenience views --------------------------------------------------
    @property
    def transactions(self) -> List[Transaction]:
        return list(self.non_derivative) + list(self.derivative)

    @property
    def purchases(self) -> List[Transaction]:
        return [t for t in self.transactions if t.is_purchase]

    @property
    def sales(self) -> List[Transaction]:
        return [t for t in self.transactions if t.is_sale]

    @property
    def total_purchase_value(self) -> Decimal:
        return sum((t.total_value for t in self.purchases if t.total_value is not None), Decimal(0))

    @property
    def total_sale_value(self) -> Decimal:
        return sum((t.total_value for t in self.sales if t.total_value is not None), Decimal(0))

    def summary(self) -> str:
        lines = [
            f"Form {self.document_type} — {self.issuer.name} ({self.issuer.trading_symbol or 'n/a'})",
            f"  CIK:    {self.issuer.cik}",
            f"  Period: {self.period_of_report}",
            f"  Reporters ({len(self.reporters)}):",
        ]
        for r in self.reporters:
            roles = ", ".join(r.roles) or "—"
            lines.append(f"    - {r.name} [{roles}]")
        lines.append(f"  Transactions: {len(self.non_derivative)} non-derivative, {len(self.derivative)} derivative")
        if self.purchases:
            lines.append(f"  Purchases:   {len(self.purchases)} (${float(self.total_purchase_value):,.2f})")
        if self.sales:
            lines.append(f"  Sales:       {len(self.sales)} (${float(self.total_sale_value):,.2f})")
        return "\n".join(lines)
