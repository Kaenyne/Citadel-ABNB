import os
import time
import httpx
import pandas as pd
import numpy as np
import re
import argparse
import warnings
import atexit
import copy
import hashlib
import json
import pickle
import sys
import logging
import traceback
import math
import shutil
from collections import Counter, defaultdict
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from functools import wraps, lru_cache
from io import StringIO, BytesIO
import html as html_lib
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from edgar import Company, set_identity

# Precompiled once at import; used by the HTML table-cleaning helpers below to
# strip hidden (display:none) nodes.  Identical to the inline re.compile(...) it
# replaces, but not rebuilt on each call.
_DISPLAY_NONE_RE = re.compile(r'display:\s*none', re.I)

# BUILD: annual-only foreign private issuer path
ANNUAL_ONLY_BUILD_ID = "annual-only-working-v8"
GLOBAL_CALC_PARENT = {}
# Inversion engine state: where each filing ACTUALLY presents each face
# concept (accumulated across filings), and concepts whose static-map
# placement has been overridden by the company's own linkbase.
_FACE_PRESENTED = {}
# Per-concept face-statement presentation positions captured from XBRL
# presentation trees during a live run.  Used by the final row sorter so all
# three core statements can follow the company's own filing order first.
_FACE_PRESENTATION_POS = {}
_RESOLVE_OVERRIDDEN = set()


class _FastTupleRow:
    """Minimal Series-like view over an ``itertuples`` row.

    ``DataFrame.iterrows()`` constructs a pandas Series for every fact, which
    is expensive on large XBRL fact sets.  This adapter preserves the exact
    ``row["column"]`` / ``row.get(...)`` access pattern used by the extractor
    while reading directly from tuple storage.
    """
    __slots__ = ("_values", "_positions")

    def __init__(self, values, positions):
        self._values = values
        self._positions = positions

    def reset(self, values):
        self._values = values
        return self

    def __getitem__(self, key):
        return self._values[self._positions[key]]

    def get(self, key, default=None):
        pos = self._positions.get(key)
        return default if pos is None else self._values[pos]


def _calc_section_of(concept, max_hops=5):
    """Walk the company's calculation linkbase upward to a recognized
    statement root and return the implied category, or None."""
    # The root sets are unions of module-level constants that are never mutated
    # at runtime, so they are built once and reused.  They are only used for
    # membership tests below, so the cached sets are identical in effect to
    # rebuilding them on every call.
    _roots = _calc_section_of._roots
    if _roots is None:
        _IS_ROOTS = (_OPEX_ROLLUP_PARENTS | _REVENUE_ROLLUP_PARENTS |
                     {'NetIncomeLoss', 'OperatingIncomeLoss', 'GrossProfit',
                      'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest',
                      'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments'})
        _CF_ROOTS = _CF_OPERATING_PARENTS | _CF_INVESTING_PARENTS | _CF_FINANCING_PARENTS
        _BS_ROOTS = {'Assets', 'Liabilities', 'LiabilitiesAndStockholdersEquity',
                     'StockholdersEquity',
                     'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest',
                     'AssetsCurrent', 'LiabilitiesCurrent'}
        _roots = _calc_section_of._roots = (_IS_ROOTS, _CF_ROOTS, _BS_ROOTS)
    _IS_ROOTS, _CF_ROOTS, _BS_ROOTS = _roots
    frontier = {concept}
    for _ in range(max_hops):
        nxt = set()
        for c in sorted(frontier, key=str):
            if c in _CF_ROOTS:
                return '3_Cash_Flow'
            if c in _IS_ROOTS:
                return '1_Income_Statement'
            if c in _BS_ROOTS:
                return '2_Balance_Sheet'
            for p, _w in sorted(
                    GLOBAL_CALC_PARENT.get(c, ()),
                    key=lambda item: (str(item[0]), str(item[1]))):
                nxt.add(p)
        if not nxt:
            return None
        frontier = nxt
    return None


# Cache slot for the immutable statement-root sets, populated on first call.
_calc_section_of._roots = None

# Roll-up roots used to classify lines via the calculation linkbase.
_OPEX_ROLLUP_PARENTS = {
    'OperatingExpenses', 'CostsAndExpenses', 'OperatingCostsAndExpenses',
    'BenefitsLossesAndExpenses', 'NoninterestExpense',
}
_REVENUE_ROLLUP_PARENTS = {
    'Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax',
    'RevenueFromContractWithCustomerIncludingAssessedTax',
    'RevenuesNetOfInterestExpense', 'NoninterestIncome',
    'InterestAndDividendIncomeOperating',
}
_CF_OPERATING_PARENTS = {
    'NetCashProvidedByUsedInOperatingActivities',
    'NetCashProvidedByUsedInOperatingActivitiesContinuingOperations',
}
_CF_INVESTING_PARENTS = {
    'NetCashProvidedByUsedInInvestingActivities',
    'NetCashProvidedByUsedInInvestingActivitiesContinuingOperations',
}
_CF_FINANCING_PARENTS = {
    'NetCashProvidedByUsedInFinancingActivities',
    'NetCashProvidedByUsedInFinancingActivitiesContinuingOperations',
}
_CF_NONOPERATING_PARENTS = {
    'NetCashProvidedByUsedInInvestingActivities',
    'NetCashProvidedByUsedInInvestingActivitiesContinuingOperations',
    'NetCashProvidedByUsedInFinancingActivities',
    'NetCashProvidedByUsedInFinancingActivitiesContinuingOperations',
}

# A filer may migrate between these two standard US-GAAP dividend concepts
# while preserving the same cumulative cash-flow disclosure.  Cross-concept
# subtraction is allowed only after an earlier, nonzero, context-identical
# overlap proves that the two tags carried the same value for that filer.
# Keeping the exception as an exact concept pair avoids weakening the general
# same-concept rule for other cash-flow lines.
_DIVIDEND_CUMULATIVE_TRANSITION_GROUPS = (
    frozenset({'PaymentsOfDividends', 'PaymentsOfOrdinaryDividends'}),
)

# These cash-flow rows are normalized as nonnegative gross outflows.  For one
# exact source family, a materially smaller annual total than its nine-month
# cumulative total is not a valid discrete Q4; it is evidence of a restatement,
# measurement-family collision, or other basis mismatch.  Reject that pair at
# candidate selection instead of deriving a negative value and silently
# deleting it later.
_NONNEGATIVE_CUMULATIVE_RESIDUAL_LABELS = frozenset({
    'Capital Expenditures',
    'Net Purchases of Productive Assets',
    'PPE Purchase Incentives',
    'PPE Sale Proceeds & Purchase Incentives',
    'Dividends Paid',
    'Income Taxes Paid, Net',
    'Interest Paid',
    'Purchases of Investments',
    'Share Repurchases',
    'Taxes Paid on Stock Awards',
    'Total Debt Repaid',
    'Short-term Debt Repaid',
    'Long-term Debt Repaid',
})


_CF_BRIDGE_SPEC = {}
_IBM_STYLE_STATE = {'active': False}  # interest folded into the operating-expense block (no separate operating-income line)
_BRIDGE_USED_LABELS = set()


def _spec_from_contribs(contribs, getrow):
    """Derive per-label weights from realized contributions. Returns
    (spec, complete): complete is False when a materially nonzero
    contribution has no recoverable row weight, in which case the
    residual for that section cannot be faithfully recomputed later."""
    spec, complete = {}, True
    for lbl, c in contribs.items():
        r = pd.to_numeric(getrow(lbl), errors='coerce').fillna(0)
        m = (r != 0)
        if m.any():
            ratio = (c[m] / r[m]).median()
            if pd.notna(ratio) and ratio != 0:
                spec[lbl] = float(ratio)
                continue
        if c.abs().max() > 1e6:
            complete = False
    return spec, complete


def _recompute_cf_residuals(df):
    """Bridge residuals are computed inside calculate_kpis, but later
    repair passes (annual scope fixes, accounting engine, industry KPIs)
    can update component rows afterwards -- leaving stale plugs (GOOGL's
    Wiz acquisition value arrived after the bridge ran, leaving a +$31.6B
    ghost in 'Other Investing Adjustments (Net)'). Recompute the three CF
    residual rows from FINAL displayed values using the recorded spec."""
    if not _CF_BRIDGE_SPEC or df is None or df.empty:
        return df

    _num_row_cache = {}

    def _num_row(idx):
        cached = _num_row_cache.get(idx)
        if cached is not None:
            return cached
        s = pd.to_numeric(df.loc[idx], errors='coerce')
        _num_row_cache[idx] = s
        return s

    changed = []
    for section, total_lbl, res_lbl in (
            ('op', 'Operating Cash Flow', 'Other Operating Adjustments (Net)'),
            ('inv', 'Investing Cash Flow', 'Other Investing Adjustments (Net)'),
            ('fin', 'Financing Cash Flow', 'Other Financing Adjustments (Net)')):
        entry = _CF_BRIDGE_SPEC.get(section)
        if not entry or not entry.get('complete'):
            continue
        spec = entry.get('spec') or {}
        tidx, ridx = ('3_Cash_Flow', total_lbl), ('3_Cash_Flow', res_lbl)
        if not spec or tidx not in df.index or ridx not in df.index:
            continue
        total = _num_row(tidx)
        _missing = [lbl for lbl in spec if ('3_Cash_Flow', lbl) not in df.index]
        if _missing:
            print(f"  [Bridge] NOTE: '{res_lbl}' NOT recomputed -- bridge component "
                  f"row(s) vanished after KPIs: {', '.join(_missing[:6])}"
                  + (" ..." if len(_missing) > 6 else "")
                  + " (keeping KPI-time residual; investigate what dropped them)")
            continue
        ssum = pd.Series(0.0, index=df.columns)
        for lbl, w in spec.items():
            li = ('3_Cash_Flow', lbl)
            if li in df.index:
                values = _num_row(li)
                if section == 'inv' and lbl == 'Purchases of Investments':
                    values, _ = (
                        _bridge_investment_purchases_excluding_acquisition_overlap(
                            df, values))
                ssum = ssum + values.fillna(0) * w
        if section == 'inv' and entry.get('productive_asset_basis'):
            _productive = _productive_asset_bridge_contributions(
                lambda label: (
                    _num_row(('3_Cash_Flow', label))
                    if ('3_Cash_Flow', label) in df.index
                    else pd.Series(np.nan, index=df.columns)),
                df.columns)
            for contribution in _productive.values():
                ssum = ssum + contribution
        res = (total.fillna(0) - ssum).where(total.notna())
        old = _num_row(ridx)
        if ((old.fillna(0) - res.fillna(0)).abs() > 1e6).any():
            changed.append(res_lbl)
        df.loc[ridx, :] = res.values
        _num_row_cache[ridx] = pd.to_numeric(df.loc[ridx], errors='coerce')
    if changed:
        print(f"  [Bridge] Recomputed {', '.join(changed)} after repair passes "
              f"(stale residuals refreshed).")
    return df


_CF_SUPPLEMENTAL_MARKERS = ('paid', 'obtained in exchange', 'incurred',
                            'period increase', 'noncash', 'non-cash')

# Cash proceeds from equity issuance must remain separate from share-count and
# equity-rollforward facts.  These labels are intentionally granular; the
# legacy ``Shares Issued`` row is derived from them later for compatibility.
_EQUITY_ISSUANCE_COMPONENT_LABELS = (
    'Shares Issued - Common Stock',
    'Shares Issued - Preferred Stock',
    'Shares Issued - Mandatory Convertible Preferred Stock',
    'Shares Issued - Combined Common and Preferred Stock',
    'Shares Issued - Other Equity',
)
_EQUITY_ISSUANCE_CASH_LABELS = frozenset(_EQUITY_ISSUANCE_COMPONENT_LABELS)

# Investment purchases/proceeds are separate cash-flow families.  A single
# broad row cannot safely contain both marketable and non-marketable facts:
# when both are filed for one period, ordinary candidate dedup keeps only one
# concept.  These component labels preserve both facts; the legacy parent rows
# are derived later for backwards compatibility.
_INVESTMENT_PURCHASE_COMPONENT_LABELS = (
    'Purchases of Marketable Securities',
    'Purchases of Non-Marketable / Other Investments',
    'Purchases of Alternative Investments',
)
_INVESTMENT_PROCEEDS_COMPONENT_LABELS = (
    'Proceeds from Marketable Securities',
    'Proceeds from Non-Marketable / Other Investments',
    'Proceeds from Alternative Investments',
)
_INVESTMENT_COMPONENT_LABELS = frozenset(
    _INVESTMENT_PURCHASE_COMPONENT_LABELS
    + _INVESTMENT_PROCEEDS_COMPONENT_LABELS)

# Signed net business-combination cash flow is separate from ordinary
# acquisition outflows.  The row uses the same normalized convention as
# acquisition outflows: positive values are investing outflows and negative
# values are investing inflows (for example, acquired cash exceeding cash paid).
_BUSINESS_COMBINATIONS_NET_LABEL = (
    'Business Combinations, Net of Cash Acquired')
_INVESTMENT_FACE_TARGET_LABELS = frozenset({
    *_INVESTMENT_COMPONENT_LABELS,
    'Purchases of Investments', 'Proceeds from Investments',
    'Other Investing Activities', _BUSINESS_COMBINATIONS_NET_LABEL,
})
_INVESTMENT_MIGRATION_PURCHASE_LABELS = frozenset({
    'Purchases of Non-Marketable / Other Investments',
    'Purchases of Alternative Investments',
})
_INVESTMENT_LATE_BASELINE_LABELS = frozenset({
    'Purchases of Non-Marketable / Other Investments',
    'Purchases of Alternative Investments',
    'Proceeds from Alternative Investments',
    _BUSINESS_COMBINATIONS_NET_LABEL,
})
_INVESTMENT_FACE_ALIAS_RULE = 'investing_cash_flow_face_family'
_INVESTMENT_MIGRATION_RULE = 'investing_family_presentation_migration'
_INVESTMENT_EQUIVALENT_PREFIX = 'VerifiedInvestmentCashFlowFamily:'

_INVESTMENT_PURCHASE_AGGREGATE_CONCEPTS = frozenset({
    'PaymentsToAcquireInvestments',
})
_INVESTMENT_PROCEEDS_AGGREGATE_CONCEPTS = frozenset({
    'ProceedsFromSaleAndMaturityOfInvestments',
})
_INVESTMENT_COMPONENT_CONCEPT_LABELS = {
    # Marketable / available-for-sale securities.
    'PaymentsToAcquireMarketableSecurities':
        'Purchases of Marketable Securities',
    'PaymentsToAcquireAvailableForSaleSecurities':
        'Purchases of Marketable Securities',
    'PaymentsToAcquireShortTermInvestments':
        'Purchases of Marketable Securities',
    'PaymentsToAcquireAvailableForSaleSecuritiesDebt':
        'Purchases of Marketable Securities',
    'ProceedsFromSaleAndMaturityOfMarketableSecurities':
        'Proceeds from Marketable Securities',
    'ProceedsFromSaleAndMaturityOfAvailableForSaleSecurities':
        'Proceeds from Marketable Securities',
    'ProceedsFromMaturitiesPrepaymentsAndCallsOfAvailableForSaleSecurities':
        'Proceeds from Marketable Securities',
    'ProceedsFromSaleOfMarketableSecurities':
        'Proceeds from Marketable Securities',
    'ProceedsFromMaturitiesOfMarketableSecurities':
        'Proceeds from Marketable Securities',
    'ProceedsFromSaleAndMaturityOfAvailableForSaleSecuritiesDebt':
        'Proceeds from Marketable Securities',

    # The taxonomy's "Other Investments" concepts are used by filers such as
    # Alphabet for non-marketable securities.  The combined label stays honest
    # for issuers whose presentation is simply "other investments".
    'PaymentsToAcquireOtherInvestments':
        'Purchases of Non-Marketable / Other Investments',
    'PaymentsToAcquireLongTermInvestments':
        'Purchases of Non-Marketable / Other Investments',
    'ProceedsFromSaleAndMaturityOfOtherInvestments':
        'Proceeds from Non-Marketable / Other Investments',
    'ProceedsFromSaleOfInvestments':
        'Proceeds from Non-Marketable / Other Investments',

    # Common extension concepts; the token classifier below covers variants.
    'PurchasesOfAlternativeInvestments':
        'Purchases of Alternative Investments',
    'ProceedsFromSalesOfAlternativeInvestments':
        'Proceeds from Alternative Investments',
}

# This is a net/signed investing line, not an asset-sale proceeds concept.
# Its economic sign is the product of the reported XBRL value and the
# calculation-linkbase weight into Investing Cash Flow.
_SIGNED_OTHER_INVESTING_CONCEPTS = frozenset({
    'PaymentsForProceedsFromOtherInvestingActivities',
})
_INVESTMENT_CASH_FLOW_CONCEPTS = frozenset(
    set(_INVESTMENT_COMPONENT_CONCEPT_LABELS)
    | set(_INVESTMENT_PURCHASE_AGGREGATE_CONCEPTS)
    | set(_INVESTMENT_PROCEEDS_AGGREGATE_CONCEPTS)
    | set(_SIGNED_OTHER_INVESTING_CONCEPTS)
)

# Productive-asset cash flows require basis-aware classification.  The first
# concept is deliberately ambiguous: filers use it for either a gross purchase
# line or a net-of-proceeds/incentives line.  The fact's own human-readable
# label therefore decides its normalized family; missing/conflicting label
# evidence fails closed to the net family rather than inflating gross CapEx.
_PRODUCTIVE_ASSET_NET_CONCEPT = 'PaymentsForProceedsFromProductiveAssets'
_PRODUCTIVE_ASSET_INCENTIVE_CONCEPT = (
    'ProceedsFromRebatesOnPurchasesOfProductiveAssets')
_PRODUCTIVE_ASSET_COMBINED_PROCEEDS_CONCEPT = (
    'ProceedsFromPropertyPlantAndEquipmentSalesAndIncentives')
_PRODUCTIVE_ASSET_AMBIGUOUS_CONCEPTS = frozenset({
    _PRODUCTIVE_ASSET_NET_CONCEPT,
    _PRODUCTIVE_ASSET_INCENTIVE_CONCEPT,
    _PRODUCTIVE_ASSET_COMBINED_PROCEEDS_CONCEPT,
})
_PRODUCTIVE_ASSET_BRIDGE_LABELS = (
    'Capital Expenditures',
    'Net Purchases of Productive Assets',
    'PPE Purchase Incentives',
    'PPE Sale Proceeds & Purchase Incentives',
)
_GENUINE_PRODUCTIVE_ASSET_SALE_CONCEPTS = frozenset({
    'ProceedsFromSaleOfPropertyPlantAndEquipment',
    'ProceedsFromSaleOfIntangibleAssets',
    'ProceedsFromSaleOfOtherAssets',
    'ProceedsFromSaleOfProductiveAssets',
    'ProceedsFromSaleOfOperatingLeaseAssets',
    'ProceedsFromSaleOfRealEstate',
})


def _compact_productive_asset_text(*parts):
    return re.sub(r'[^a-z0-9]+', '', ' '.join(
        str(part or '') for part in parts).casefold())


def _classify_productive_asset_cash_flow_line(concept,
                                               presentation_labels=None):
    """Return a basis-aware productive-asset cash-flow label.

    ``PaymentsForProceedsFromProductiveAssets`` is not intrinsically gross or
    net.  A strong filer label such as "Purchases of property and equipment"
    proves gross CapEx, while "... net of proceeds/incentives" remains a net
    family.  Unknown or conflicting evidence is kept net so the pipeline never
    fabricates gross CapEx from an economically narrower amount.
    """
    local = str(concept or '').split(':')[-1]
    if local in _GENUINE_PRODUCTIVE_ASSET_SALE_CONCEPTS:
        return 'Proceeds from Asset Sales'
    if local == _PRODUCTIVE_ASSET_INCENTIVE_CONCEPT:
        return 'PPE Purchase Incentives'
    if local == _PRODUCTIVE_ASSET_COMBINED_PROCEEDS_CONCEPT:
        return 'PPE Sale Proceeds & Purchase Incentives'
    if local != _PRODUCTIVE_ASSET_NET_CONCEPT:
        return None

    if isinstance(presentation_labels, str) or presentation_labels is None:
        labels = [presentation_labels]
    else:
        labels = list(presentation_labels)

    saw_gross_purchase = False
    saw_net_or_conflict = False
    saw_sale_only = False
    for label in labels:
        text = _compact_productive_asset_text(label)
        if not text:
            continue
        if 'paymentsforproceedsfromproductiveassets' in text:
            # Generic taxonomy wording carries no gross-vs-net evidence.
            continue
        has_purchase = any(token in text for token in (
            'purchaseof', 'purchasesof', 'paymentstoacquire', 'paymentfor',
            'capitalexpenditure', 'capitalspending', 'additionstoproperty',
            'acquisitionofproperty'))
        has_sale = any(token in text for token in (
            'proceedsfromsale', 'saleofproperty', 'salesofproperty',
            'disposalofproperty', 'assetproceeds'))
        has_incentive = any(token in text for token in (
            'incentive', 'rebate', 'reimbursement',
            'tenantimprovementallowance'))
        explicit_net = (
            'netof' in text or text.endswith('net')
            or 'netpurchase' in text)
        if has_purchase and not explicit_net and not has_sale and not has_incentive:
            saw_gross_purchase = True
        elif has_sale and not has_purchase:
            saw_sale_only = True
        elif has_purchase or explicit_net or has_incentive or has_sale:
            saw_net_or_conflict = True

    if saw_net_or_conflict:
        return 'Net Purchases of Productive Assets'
    if saw_gross_purchase and not saw_sale_only:
        return 'Capital Expenditures'
    if saw_sale_only and not saw_gross_purchase:
        return 'Proceeds from Asset Sales'
    return 'Net Purchases of Productive Assets'


def _productive_asset_source_label(labels, target_label):
    """Choose one deterministic source label supporting the classification."""
    if isinstance(labels, str) or labels is None:
        labels = [labels]
    cleaned = [re.sub(r'\s+', ' ', str(label or '')).strip()
               for label in labels]
    cleaned = [label for label in cleaned if label]
    for label in cleaned:
        if (_classify_productive_asset_cash_flow_line(
                _PRODUCTIVE_ASSET_NET_CONCEPT, label) == target_label):
            return label
    return cleaned[0] if cleaned else None


def _collect_productive_asset_face_labels(xbrl):
    """Collect filer-authored cash-flow face labels for fallback evidence."""
    result = defaultdict(list)
    try:
        role_to_cat = _classify_statement_roles(xbrl)
        trees = getattr(xbrl, 'presentation_trees', None) or {}
    except Exception:
        return {}
    for role, category in role_to_cat.items():
        if category != '3_Cash_Flow':
            continue
        tree = trees.get(role)
        nodes = getattr(tree, 'all_nodes', None)
        if not nodes:
            continue
        for elem_id in _presentation_order(tree):
            node = nodes.get(elem_id)
            if node is None or getattr(node, 'is_abstract', False):
                continue
            concept = elem_id.replace('_', ':', 1).split(':')[-1]
            if concept not in _PRODUCTIVE_ASSET_AMBIGUOUS_CONCEPTS:
                continue
            label = (getattr(node, 'standard_label', None)
                     or getattr(node, 'display_label', None) or '')
            label = re.sub(r'\s+', ' ', str(label)).strip().rstrip(':')
            if label and label not in result[concept]:
                result[concept].append(label)
    return {concept: tuple(labels) for concept, labels in result.items()}


def _productive_asset_bridge_contributions(getrow, index):
    """Return mutually exclusive productive-asset bridge contributions.

    Gross purchases plus separately reported incentives/proceeds are preferred.
    When gross purchases are unavailable, a net productive-assets line is used
    once and any separately surfaced incentive/combined row is suppressed from
    bridge arithmetic for that period to prevent double counting.
    """
    def _row(label):
        values = pd.to_numeric(getrow(label), errors='coerce')
        return values.reindex(index)

    gross = _row('Capital Expenditures')
    net = _row('Net Purchases of Productive Assets')
    incentives = _row('PPE Purchase Incentives')
    combined = _row('PPE Sale Proceeds & Purchase Incentives')
    gross_basis = gross.notna()
    net_basis = ~gross_basis & net.notna()
    allow_positive_components = ~net_basis
    # The combined row is an aggregate that already includes purchase
    # incentives.  When both are published for one period (Amazon 2020-2021),
    # count the aggregate once and suppress the narrower incentive component.
    combined_basis = allow_positive_components & combined.notna()
    incentive_basis = allow_positive_components & ~combined_basis
    return {
        'Capital Expenditures': -gross.where(gross_basis, 0.0).fillna(0.0),
        'Net Purchases of Productive Assets':
            -net.where(net_basis, 0.0).fillna(0.0),
        'PPE Purchase Incentives':
            incentives.where(incentive_basis, 0.0).fillna(0.0),
        'PPE Sale Proceeds & Purchase Incentives':
            combined.where(combined_basis, 0.0).fillna(0.0),
    }


# Acquisition cash-flow lines can migrate between standard and issuer-specific
# XBRL concepts while retaining the same filer-authored statement-face meaning.
# Keep measurement families separate so a pure business-acquisition line is
# never quarterized against a broader line that also includes non-marketable
# investments, intangibles, divestitures, or other assets.
_ACQUISITION_EQUIVALENT_PREFIX = 'VerifiedAcquisitionCashFlowFamily:'
_ACQUISITION_ALIAS_RULE = 'acquisition_cash_flow_face_family'


def _compact_acquisition_text(*parts):
    return re.sub(r'[^a-z0-9]+', '', ' '.join(
        str(part or '') for part in parts).casefold())


def _classify_acquisition_cash_flow_family(presentation_label):
    """Return a conservative acquisition cash-flow measurement family.

    The result is used only as a subtraction identity inside one normalized
    ``Acquisitions`` row.  It does not change the displayed label or combine
    economically different acquisition/investment scopes.
    """
    text = _compact_acquisition_text(presentation_label)
    if not text:
        return None
    has_acquisition = any(token in text for token in (
        'acquisition', 'acquirebusiness', 'acquiredbusiness',
        'businesscombination', 'purchaseofbusiness', 'purchaseofcompan',
        'cashpaymentsnetofacquiredcash'))
    if not has_acquisition:
        return None

    # Combined company/intangible/other-asset or divestiture presentations.
    # Test this before the broad ``and other`` family because labels such as
    # Microsoft's explicitly contain both constructions.
    if any(token in text for token in (
            'intangible', 'otherasset', 'intellectualproperty',
            'divestiture', 'divested')):
        return 'acquisitions_and_intangibles_other_assets_net'

    # Broad investment activity, used by Amazon and similar filers.
    if any(token in text for token in (
            'nonmarketableinvestment', 'nonmarketable',
            'otherinvestmentactivity', 'otherinvestment',
            'investmentandother', 'acquisitionandotherinvestment',
            'acquisitionsandother', 'strategicinvestment',
            'convertiblenote', 'andothernet', 'andother')):
        return 'acquisitions_and_other_investment_activity_net'

    if 'gross' in text and 'netofcashacquired' not in text:
        return 'business_acquisitions_gross'

    # A face line explicitly limited to businesses/acquisitions, normally net
    # of acquired cash.  Generic taxonomy labels fall into this family only
    # when they contain acquisition language and no broader-scope tokens above.
    return 'business_acquisitions_net_of_cash_acquired'



def _is_acquisition_cash_outflow_concept(concept):
    """Return True for cash payments to acquire businesses or related assets.

    Taxonomy and issuer-extension names frequently contain ``NetOfCashAcquired``.
    That phrase describes the *measurement basis* of an acquisition payment; it
    does not turn the outflow into cash received.  Directional payment/purchase
    language therefore wins over the embedded words ``cash acquired``.
    """
    text = _compact_acquisition_text(concept)
    if not text:
        return False
    has_business_scope = any(token in text for token in (
        'acquirebusiness', 'acquisition', 'businesscombination',
        'purchaseofbusiness', 'purchaseofcompan'))
    if not has_business_scope:
        return False
    has_outflow_direction = any(token in text for token in (
        'paymentstoacquire', 'paymenttoacquire', 'paymentsforacquisition',
        'paymentforacquisition', 'cashpaymentsfor', 'cashpaymentfor',
        'purchaseofbusiness', 'purchasesofbusiness',
        'acquisitionsnetofcashacquired'))
    return bool(has_outflow_direction)


def _is_cash_acquired_in_business_acquisition_concept(concept):
    """Return True only for genuine cash balances received in acquisitions."""
    if _is_acquisition_cash_outflow_concept(concept):
        return False
    text = _compact_acquisition_text(concept)
    if not text:
        return False
    return bool(
        'cash' in text
        and any(token in text for token in (
            'acquiredinbusinessacquisition',
            'acquiredinbusinesscombination',
            'cashacquiredinacquisition',
            'cashacquiredinbusiness'))
    )


def _repair_misdirected_acquisition_cash_flows(df):
    """Move payment concepts misrouted as acquired-cash disclosures to CF.

    This is deliberately concept-direction based and therefore also repairs
    warm native-extraction caches produced by older mapping logic.  Genuine
    ``CashCashEquivalents...AcquiredInBusinessAcquisitions`` disclosures are
    untouched because they contain no payment/purchase direction.
    """
    required = {'Category', 'Label', 'Concept', 'Value'}
    if df is None or df.empty or not required.issubset(df.columns):
        return df
    out = df.copy()
    concept_text = out['Concept'].fillna('').astype(str).map(
        lambda value: value.split(':')[-1])
    wrong = (
        out['Label'].eq('Cash Acquired in Business Acquisitions')
        & concept_text.map(_is_acquisition_cash_outflow_concept)
    )
    if not wrong.any():
        return out
    _ensure_object_column(out, 'SourceCanonicalizedFrom')
    marker = 'cash_acquired_disclosure_to_acquisition_outflow'
    for idx in out.index[wrong]:
        concept = concept_text.at[idx]
        value = pd.to_numeric(pd.Series([out.at[idx, 'Value']]),
                              errors='coerce').iloc[0]
        family = _classify_acquisition_cash_flow_family(concept)
        if family is None:
            family = 'business_acquisitions_net_of_cash_acquired'
        source_label = str(out.at[idx, 'SourceLabel'] or '').strip() \
            if 'SourceLabel' in out.columns and pd.notna(out.at[idx, 'SourceLabel']) else ''
        if not source_label:
            source_label = concept
        out.at[idx, 'Category'] = '3_Cash_Flow'
        out.at[idx, 'Label'] = 'Acquisitions'
        if pd.notna(value):
            out.at[idx, 'Value'] = abs(float(value))
        if 'TagRank' in out.columns:
            tags = CONCEPT_MAP.get('Acquisitions', {}).get('tags', [])
            try:
                out.at[idx, 'TagRank'] = tags.index(concept)
            except ValueError:
                out.at[idx, 'TagRank'] = 999
        metadata = {
            'SourceKind': 'xbrl',
            'SourceAdmissionRule': 'acquisition_payment_direction_repair',
            'SourceSemanticType': 'Acquisitions',
            'SourceAnalyticalBasis': 'consolidated_statement',
            'SourceTableRole': 'xbrl_statement_fact',
            'SourceLabel': source_label,
            'SourceRawLabel': source_label,
            'SourceLabelOrigin': 'concept_name_repair',
            'SourceEquivalentConcept': _ACQUISITION_EQUIVALENT_PREFIX + family,
            'SourceAliasVerified': True,
            'SourceAliasRule': _ACQUISITION_ALIAS_RULE,
            'SourceMetricFamily': 'acquisitions.' + family,
            'SourceMetricIdentity': family,
        }
        for column, metadata_value in metadata.items():
            if isinstance(metadata_value, (str, bool)):
                _ensure_object_column(out, column)
            elif column not in out.columns:
                out[column] = np.nan
            out.at[idx, column] = metadata_value
        prior = str(out.at[idx, 'SourceCanonicalizedFrom'] or '').strip()
        out.at[idx, 'SourceCanonicalizedFrom'] = (
            marker if not prior or prior == 'nan' else prior + ';' + marker)
    print(f"  [Acquisition Direction] Reclassified {int(wrong.sum())} payment "
          "fact(s) from acquired-cash disclosure to Acquisitions.")
    return out



def _acquisition_nonmarketable_overlap_periods(frame):
    """Return periods where Acquisitions already includes non-marketable buys.

    The selected-fact audit is the only safe evidence here.  The acquisition
    row must carry the verified broad acquisition/investment family and its
    filer-authored label or concept must explicitly mention non-marketable
    investments.  A directly filed ``Purchases of Investments`` aggregate
    blocks suppression because its composition may differ from the granular
    component sum.
    """
    if frame is None or getattr(frame, 'empty', True):
        return set()
    audit = getattr(frame, 'attrs', {}).get('fact_audit')
    if not isinstance(audit, pd.DataFrame) or audit.empty:
        return set()
    required = {'Category', 'Label', 'Period'}
    if not required.issubset(audit.columns):
        return set()
    cash = audit['Category'].astype(str).eq('3_Cash_Flow')
    acquisitions = audit.loc[
        cash & audit['Label'].astype(str).eq('Acquisitions')].copy()
    if acquisitions.empty:
        return set()
    family = acquisitions.get(
        'SourceMetricFamily', pd.Series('', index=acquisitions.index)
    ).fillna('').astype(str)
    broad = family.eq(
        'acquisitions.acquisitions_and_other_investment_activity_net')
    source_text = pd.Series('', index=acquisitions.index, dtype=object)
    for column in ('SourceRawLabel', 'SourceLabel', 'Concept'):
        if column in acquisitions.columns:
            source_text = source_text + ' ' + acquisitions[column].fillna('').astype(str)
    explicit_nonmarketable = source_text.map(
        lambda value: 'nonmarketable' in _compact_acquisition_text(value))
    periods = set(acquisitions.loc[
        broad & explicit_nonmarketable, 'Period'].dropna().astype(str))
    if not periods:
        return set()
    # A source-backed aggregate is not interchangeable with the component sum.
    direct_parent_periods = set(audit.loc[
        cash & audit['Label'].astype(str).eq('Purchases of Investments'),
        'Period'].dropna().astype(str))
    return periods - direct_parent_periods


def _bridge_investment_purchases_excluding_acquisition_overlap(
        frame, purchases_series):
    """Remove separately displayed non-marketable buys already in Acquisitions.

    The displayed detailed row remains intact.  Only the bridge contribution is
    adjusted, analogous to aggregate/component arbitration elsewhere in the
    cash-flow engine.  Returns ``(adjusted_series, suppressed_mask)``.
    """
    purchases = pd.to_numeric(purchases_series, errors='coerce').copy()
    purchases = purchases.reindex(frame.columns)
    periods = _acquisition_nonmarketable_overlap_periods(frame)
    mask = pd.Series(False, index=frame.columns)
    if not periods:
        return purchases, mask
    component_idx = (
        '3_Cash_Flow', 'Purchases of Non-Marketable / Other Investments')
    if component_idx not in frame.index:
        return purchases, mask
    component = pd.to_numeric(frame.loc[component_idx], errors='coerce').reindex(
        frame.columns)
    mask = pd.Series(frame.columns.astype(str).isin(periods), index=frame.columns)
    mask &= purchases.notna() & component.notna()
    candidate = purchases - component.fillna(0.0)
    tolerance = pd.concat(
        [purchases.abs(), component.abs()], axis=1).max(axis=1).mul(0.001).add(1.0)
    mask &= candidate >= -tolerance
    adjusted = purchases.copy()
    adjusted.loc[mask] = candidate.loc[mask].clip(lower=0.0)
    return adjusted, mask


def _collect_acquisition_face_labels(xbrl):
    """Collect acquisition-family labels from cash-flow presentation trees.

    This includes issuer-extension concepts learned at runtime.  Concepts whose
    labels do not prove an acquisition measurement family are ignored.
    """
    result = defaultdict(list)
    try:
        role_to_cat = _classify_statement_roles(xbrl)
        trees = getattr(xbrl, 'presentation_trees', None) or {}
    except Exception:
        return {}
    for role, category in role_to_cat.items():
        if category != '3_Cash_Flow':
            continue
        tree = trees.get(role)
        nodes = getattr(tree, 'all_nodes', None)
        if not nodes:
            continue
        for elem_id in _presentation_order(tree):
            node = nodes.get(elem_id)
            if node is None or getattr(node, 'is_abstract', False):
                continue
            label = (getattr(node, 'standard_label', None)
                     or getattr(node, 'display_label', None) or '')
            label = re.sub(r'\s+', ' ', str(label)).strip().rstrip(':')
            family = _classify_acquisition_cash_flow_family(label)
            if family is None:
                continue
            concept = elem_id.replace('_', ':', 1).split(':')[-1]
            if label not in result[concept]:
                result[concept].append(label)
    return {concept: tuple(labels) for concept, labels in result.items()}


def _acquisition_source_label(labels):
    if isinstance(labels, str) or labels is None:
        labels = [labels]
    cleaned = [re.sub(r'\s+', ' ', str(label or '')).strip()
               for label in labels]
    for label in cleaned:
        if label and _classify_acquisition_cash_flow_family(label):
            return label
    return None


def _classify_investment_face_label(presentation_label):
    """Classify one filer-authored investing-statement face label.

    This deliberately requires directional and instrument-specific wording.
    Generic note captions and balance-sheet investment labels return ``None``.
    The function is used before concept-name heuristics because issuer
    extensions often have opaque names while the cash-flow face label is clear.
    """
    text = re.sub(r'[^a-z0-9]+', '', str(
        presentation_label or '').casefold())
    if not text:
        return None

    if ('businesscombination' in text and 'netofcashacquired' in text):
        return _BUSINESS_COMBINATIONS_NET_LABEL

    # A combined acquisition/investment line (Amazon and similar filers) is not
    # a pure investment-purchase family.  Let the acquisition classifier retain
    # the complete filed scope instead of carving the same fact into a second
    # non-marketable-investment row.
    if (any(token in text for token in (
            'acquisition', 'businesscombination', 'acquiredbusiness',
            'cashacquired'))
            and any(token in text for token in (
                'investment', 'securit', 'convertiblenote'))):
        return None

    # The broad signed residual family must be exact enough that footnote prose
    # such as "other investments" is not swept into the cash-flow line.
    if text in {
            'otherinvestingactivities', 'otherinvestingactivity',
            'otherinvestingactivitiesnet', 'otherinvestingactivitynet'}:
        return 'Other Investing Activities'

    purchase = any(token in text for token in (
        'purchaseof', 'purchasesof', 'paymentstoacquire',
        'paymentforacquisition', 'acquisitionof'))
    proceeds = any(token in text for token in (
        'proceedsfrom', 'salesandredemptionof', 'saleandredemptionof',
        'proceedsfromsales', 'proceedsfromsale', 'redemptionof'))
    if purchase == proceeds:
        return None

    prefix = 'Purchases of ' if purchase else 'Proceeds from '
    if 'alternativeinvestment' in text:
        return prefix + 'Alternative Investments'
    if any(token in text for token in (
            'privatelyheldsecurit', 'privateheldsecurit',
            'privatelyheldinvestment', 'nonmarketableinvestment',
            'nonmarketablesecurit', 'privateinvestment')):
        return prefix + 'Non-Marketable / Other Investments'
    if any(token in text for token in (
            'marketablesecurit', 'availableforsale',
            'shortterminvestment')):
        return prefix + 'Marketable Securities'
    if 'investment' in text or 'securit' in text:
        return 'Purchases of Investments' if purchase else 'Proceeds from Investments'
    return None



_STANDARD_INVESTMENT_CONCEPT_TARGETS = {
    **_INVESTMENT_COMPONENT_CONCEPT_LABELS,
    **{concept: 'Purchases of Investments'
       for concept in _INVESTMENT_PURCHASE_AGGREGATE_CONCEPTS},
    **{concept: 'Proceeds from Investments'
       for concept in _INVESTMENT_PROCEEDS_AGGREGATE_CONCEPTS},
    **{concept: 'Other Investing Activities'
       for concept in _SIGNED_OTHER_INVESTING_CONCEPTS},
}


def _investment_face_override_is_safe(concept, existing_labels, face_target,
                                      source_label=None):
    """Allow face-label overrides only for opaque or genuinely broad concepts.

    Standard US-GAAP purchase/proceeds concepts keep exact-concept arithmetic.
    Giving every standard concept one shared family identity lets zero
    subcomponents replace valid cumulative totals during quarterization.
    """
    local = str(concept or '').split(':')[-1]
    existing = {
        str(label).strip() for label in (existing_labels or ())
        if str(label).strip()
    }
    label_text = _compact_investing_text(source_label)
    concept_text = _compact_investing_text(local)
    combined_text = label_text or concept_text
    if (any(token in combined_text for token in (
            'acquisition', 'businesscombination', 'acquiredbusiness',
            'cashacquired'))
            and any(token in combined_text for token in (
                'investment', 'securit', 'convertiblenote'))
            and face_target != _BUSINESS_COMBINATIONS_NET_LABEL):
        return False

    standard_target = _STANDARD_INVESTMENT_CONCEPT_TARGETS.get(local)
    if standard_target is not None:
        # Preserve the source label for audit, but never replace or alias a
        # standard exact concept merely because its face wording is familiar.
        return False

    if 'Acquisitions' in existing:
        return face_target == _BUSINESS_COMBINATIONS_NET_LABEL

    broad = {
        'Other Investing Activities',
        'Purchases of Investments',
        'Proceeds from Investments',
        'Proceeds from Asset Sales',
    }
    if not existing:
        return True
    if face_target in existing:
        # Opaque extensions already routed to the right row still need a
        # verified family identity for safe within-family subtraction.
        return True
    return existing.issubset(broad)


def _clear_standard_investment_face_aliases(frame):
    """Undo v3-style aliases on standard concepts while retaining raw labels."""
    if frame is None or frame.empty or 'Concept' not in frame.columns:
        return frame
    out = frame
    local = out['Concept'].fillna('').astype(str).str.split(':').str[-1]
    rule = out.get(
        'SourceAliasRule', pd.Series('', index=out.index)
    ).fillna('').astype(str)
    mask = (
        local.isin(_STANDARD_INVESTMENT_CONCEPT_TARGETS)
        & rule.eq(_INVESTMENT_FACE_ALIAS_RULE)
    )
    if not mask.any():
        return out
    if 'SourceAliasVerified' in out.columns:
        out.loc[mask, 'SourceAliasVerified'] = False
    for column in (
            'SourceAliasRule', 'SourceEquivalentConcept',
            'SourceMetricFamily', 'SourceMetricIdentity'):
        if column in out.columns:
            out.loc[mask, column] = np.nan
    return out


def _dedupe_overlapping_investing_cash_flow_facts(df):
    """Remove exact source facts duplicated across mutually exclusive rows.

    Runtime/fuzzy mappings can emit one filed fact under both Acquisitions and
    an investment component, or under both a specific investment family and
    broad Other.  Only exact same-context, same-value duplicates are removed.
    """
    required = {'Category', 'Label', 'Concept', 'Value', 'FY', 'Q'}
    if df is None or df.empty or not required.issubset(df.columns):
        return df
    out = df.copy()
    cash = out['Category'].eq('3_Cash_Flow')
    if not cash.any():
        return out

    key_columns = [
        column for column in (
            'Concept', 'FY', 'Q', 'Start', 'End', 'Duration', 'Filed',
            'Accession', 'DimCount')
        if column in out.columns
    ]
    work = out.loc[cash].copy()
    work['_ExactInvestingValue'] = pd.to_numeric(
        work['Value'], errors='coerce').round(6)
    group_columns = key_columns + ['_ExactInvestingValue']
    drop_indices = set()

    specific = set(_INVESTMENT_COMPONENT_LABELS) | {
        _BUSINESS_COMBINATIONS_NET_LABEL}
    broad = {
        'Purchases of Investments', 'Proceeds from Investments',
        'Other Investing Activities', 'Proceeds from Asset Sales'}
    investment_like = specific | broad

    for _, group in work.groupby(group_columns, dropna=False, sort=False):
        labels = set(group['Label'].astype(str))
        if len(labels) < 2:
            continue

        if _BUSINESS_COMBINATIONS_NET_LABEL in labels:
            keep = group[group['Label'].eq(
                _BUSINESS_COMBINATIONS_NET_LABEL)].index
            drop_indices.update(
                idx for idx in group.index if idx not in set(keep)
                and str(group.at[idx, 'Label']) in (
                    investment_like | {'Acquisitions'}))
            continue

        if 'Acquisitions' in labels and labels.intersection(investment_like):
            acquisition_evidence = False
            for _, row in group[group['Label'].eq('Acquisitions')].iterrows():
                candidates = (
                    row.get('SourceLabel'), row.get('SourceRawLabel'),
                    row.get('Concept'))
                if any(_classify_acquisition_cash_flow_family(value)
                       for value in candidates if value is not None):
                    acquisition_evidence = True
                    break
                if str(row.get('SourceMetricFamily') or '').startswith(
                        'acquisitions.'):
                    acquisition_evidence = True
                    break
            if acquisition_evidence:
                drop_indices.update(
                    idx for idx in group.index
                    if str(group.at[idx, 'Label']) in investment_like)
                continue

        detailed = labels.intersection(specific)
        if len(detailed) == 1:
            detail = next(iter(detailed))
            # Keep one detailed rendering and discard only broad duplicates of
            # the same exact fact.  Different concepts or values are untouched.
            drop_indices.update(
                idx for idx in group.index
                if str(group.at[idx, 'Label']) in broad
                and str(group.at[idx, 'Label']) != detail)

    if not drop_indices:
        return out
    out = out.drop(index=sorted(drop_indices)).copy()
    print(
        f"  [Investing Dedup] Removed {len(drop_indices)} exact cross-family "
        "duplicate fact(s).")
    return out



_MARKETABLE_PROCEEDS_SCOPE_RANK = {
    # Complete marketable-security proceeds totals.
    'ProceedsFromSaleAndMaturityOfMarketableSecurities': 0,
    'ProceedsFromSaleAndMaturityOfAvailableForSaleSecurities': 0,
    'ProceedsFromSaleAndMaturityOfAvailableForSaleSecuritiesDebt': 0,
    # Partial maturity or sale components.
    'ProceedsFromMaturitiesPrepaymentsAndCallsOfAvailableForSaleSecurities': 2,
    'ProceedsFromSaleOfMarketableSecurities': 2,
    'ProceedsFromMaturitiesOfMarketableSecurities': 2,
    'ProceedsFromSaleOfAvailableForSaleSecuritiesDebt': 3,
}


def _arbitrate_standard_investment_scope_facts(df):
    """Remove proven subcomponent facts from a broader normalized row.

    Some filers expose both a complete marketable-security proceeds total and
    a narrower sale-only component under concepts that resolve to the same
    normalized label.  Latest-filing-first candidate selection can otherwise
    let a later comparative zero component replace the complete cumulative
    total.  Suppression is allowed only within one fiscal year when:

    * a recognized complete-total concept and a lower-scope concept coexist;
    * they overlap in at least two cumulative contexts;
    * the total is never smaller than the component; and
    * at least one overlap proves the total is materially broader.

    The source facts remain in the raw native cache; only the normalized
    quarterization cohort is narrowed.
    """
    required = {'Category', 'Label', 'Concept', 'Value', 'FY', 'Q', 'Duration'}
    if df is None or df.empty or not required.issubset(df.columns):
        return df
    out = df.copy()
    mask = (
        out['Category'].eq('3_Cash_Flow')
        & out['Label'].eq('Proceeds from Marketable Securities')
        & pd.to_numeric(out.get('DimCount', 0), errors='coerce').fillna(0).eq(0)
    )
    if not mask.any():
        return out

    qrank = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}

    def _is_cumulative(row):
        q = str(row.get('Q') or '')
        dur = pd.to_numeric(pd.Series([row.get('Duration')]), errors='coerce').iloc[0]
        if pd.isna(dur):
            return False
        bounds = {'Q1': (45, 125), 'Q2': (140, 230),
                  'Q3': (220, 320), 'Q4': (300, 400)}
        lo_hi = bounds.get(q)
        return bool(lo_hi and lo_hi[0] <= float(dur) <= lo_hi[1])

    drop = set()
    work = out.loc[mask].copy()
    work['_LocalConcept'] = work['Concept'].fillna('').astype(str).str.split(':').str[-1]
    work['_ScopeRank'] = work['_LocalConcept'].map(
        _MARKETABLE_PROCEEDS_SCOPE_RANK).fillna(99).astype(int)
    work['_QRank'] = work['Q'].astype(str).map(qrank).fillna(0).astype(int)
    work['_Cumulative'] = work.apply(_is_cumulative, axis=1)
    work['_NumericValue'] = pd.to_numeric(work['Value'], errors='coerce')

    for fiscal_year, year in work.groupby(
            pd.to_numeric(work['FY'], errors='coerce'), dropna=True, sort=False):
        cumulative = year[year['_Cumulative'] & year['_NumericValue'].notna()].copy()
        if cumulative.empty:
            continue
        complete_concepts = sorted(set(cumulative.loc[
            cumulative['_ScopeRank'].eq(0), '_LocalConcept']))
        if not complete_concepts:
            continue

        # Pick the complete concept with the broadest quarter coverage, then
        # latest filing as a deterministic tie-breaker.
        def _complete_score(concept):
            rows = cumulative[cumulative['_LocalConcept'].eq(concept)]
            coverage = rows['_QRank'].nunique()
            filed = pd.to_datetime(rows.get(
                'Filed', pd.Series(pd.NaT, index=rows.index)), errors='coerce').max()
            filed_score = int(filed.value) if pd.notna(filed) else -1
            return (coverage, filed_score, concept)

        preferred = max(complete_concepts, key=_complete_score)
        preferred_rows = cumulative[cumulative['_LocalConcept'].eq(preferred)]
        if preferred_rows['_QRank'].nunique() < 2:
            continue

        for component in sorted(set(cumulative.loc[
                cumulative['_ScopeRank'].gt(0) & cumulative['_ScopeRank'].lt(99),
                '_LocalConcept'])):
            component_rows = cumulative[cumulative['_LocalConcept'].eq(component)]
            overlaps = []
            for rank in sorted(set(preferred_rows['_QRank']) & set(component_rows['_QRank'])):
                p_rows = preferred_rows[preferred_rows['_QRank'].eq(rank)]
                c_rows = component_rows[component_rows['_QRank'].eq(rank)]
                if p_rows.empty or c_rows.empty:
                    continue
                p_val = float(p_rows.sort_values(
                    ['Duration', 'Filed'], ascending=[False, False]).iloc[0]['_NumericValue'])
                c_val = float(c_rows.sort_values(
                    ['Duration', 'Filed'], ascending=[False, False]).iloc[0]['_NumericValue'])
                overlaps.append((p_val, c_val))
            if len(overlaps) < 2:
                continue
            never_smaller = True
            materially_broader = False
            for p_val, c_val in overlaps:
                tolerance = max(abs(p_val), abs(c_val), 1.0) * 0.001 + 1.0
                if abs(p_val) + tolerance < abs(c_val):
                    never_smaller = False
                    break
                if abs(p_val) > abs(c_val) + tolerance:
                    materially_broader = True
            if not (never_smaller and materially_broader):
                continue
            component_idx = year[year['_LocalConcept'].eq(component)].index
            drop.update(component_idx.tolist())

    if not drop:
        return out
    out = out.drop(index=sorted(drop)).copy()
    print(
        f"  [Investing Scope] Suppressed {len(drop)} proven marketable-"
        "proceeds subcomponent fact(s) from normalized quarterization.")
    return out


def _collect_investment_face_labels(xbrl):
    """Collect strong investing-family labels from cash-flow presentation trees."""
    result = defaultdict(list)
    try:
        role_to_cat = _classify_statement_roles(xbrl)
        trees = getattr(xbrl, 'presentation_trees', None) or {}
    except Exception:
        return {}
    for role, category in role_to_cat.items():
        if category != '3_Cash_Flow':
            continue
        tree = trees.get(role)
        nodes = getattr(tree, 'all_nodes', None)
        if not nodes:
            continue
        for elem_id in _presentation_order(tree):
            node = nodes.get(elem_id)
            if node is None or getattr(node, 'is_abstract', False):
                continue
            label = (getattr(node, 'standard_label', None)
                     or getattr(node, 'display_label', None) or '')
            label = re.sub(r'\s+', ' ', str(label)).strip().rstrip(':')
            if _classify_investment_face_label(label) is None:
                continue
            concept = elem_id.replace('_', ':', 1).split(':')[-1]
            if label not in result[concept]:
                result[concept].append(label)
    return {concept: tuple(labels) for concept, labels in result.items()}


def _investment_source_label(labels):
    if isinstance(labels, str) or labels is None:
        labels = [labels]
    cleaned = [re.sub(r'\s+', ' ', str(label or '')).strip()
               for label in labels]
    for label in cleaned:
        if label and _classify_investment_face_label(label):
            return label
    return None


def _investment_row_source_label(row):
    for field in ('SourceLabel', 'SourceRawLabel', 'label', 'label_text',
                  'standard_label', 'concept_label', 'name'):
        try:
            value = row.get(field)
        except Exception:
            value = None
        if value is not None and not pd.isna(value) and str(value).strip():
            label = re.sub(r'\s+', ' ', str(value)).strip()
            if _classify_investment_face_label(label):
                return label
    return None


def _ensure_object_column(frame, column):
    """Ensure provenance/metadata columns can safely receive text values.

    Pandas 3.x raises ``TypeError`` when text is assigned to a float64 column.
    A column created from all-missing values is otherwise inferred as float64,
    which is exactly what occurs for companies such as MSFT whose native cache
    has no pre-existing ``SourceCanonicalizedFrom`` field.  Preserve existing
    values while making the storage type explicit and forward-compatible.
    """
    if column not in frame.columns:
        frame[column] = pd.Series(None, index=frame.index, dtype=object)
    elif not pd.api.types.is_object_dtype(frame[column].dtype):
        frame[column] = frame[column].astype(object)


def _stamp_investment_family_metadata(out, idx, target, source_label,
                                      origin='fact_or_cache'):
    family_key = re.sub(r'[^a-z0-9]+', '_', target.casefold()).strip('_')
    metadata = {
        'SourceLabel': source_label,
        'SourceRawLabel': source_label,
        'SourceLabelOrigin': origin,
        'SourceAliasVerified': True,
        'SourceAliasRule': _INVESTMENT_FACE_ALIAS_RULE,
        'SourceEquivalentConcept': (
            _INVESTMENT_EQUIVALENT_PREFIX + family_key),
        'SourceMetricFamily': 'investing.' + family_key,
        'SourceMetricIdentity': family_key,
        'SourceSemanticType': target,
    }
    for column, value in metadata.items():
        _ensure_object_column(out, column)
        out.at[idx, column] = value


def _append_source_marker(out, mask, marker):
    _ensure_object_column(out, 'SourceCanonicalizedFrom')
    prior = out.loc[mask, 'SourceCanonicalizedFrom'].fillna('').astype(str)
    updated = pd.Series(
        np.where(prior.eq(''), marker, prior + ';' + marker),
        index=prior.index,
        dtype=object,
    )
    out.loc[mask, 'SourceCanonicalizedFrom'] = updated


def _compact_investing_text(*parts):
    return re.sub(r'[^a-z0-9]+', '', ' '.join(
        str(part or '') for part in parts).casefold())


def _classify_investment_cash_flow_concept(concept):
    """Return a granular investment cash-flow label for one concept.

    Exact standard concepts win.  Extension concepts are classified only when
    their names contain both a cash-flow direction and investment/security
    language; ambiguous net investment concepts remain signed other investing
    activities rather than being forced into purchases or proceeds.
    """
    concept = str(concept or '').split(':')[-1]
    if concept in _INVESTMENT_COMPONENT_CONCEPT_LABELS:
        return _INVESTMENT_COMPONENT_CONCEPT_LABELS[concept]
    if concept in _INVESTMENT_PURCHASE_AGGREGATE_CONCEPTS:
        return 'Purchases of Investments'
    if concept in _INVESTMENT_PROCEEDS_AGGREGATE_CONCEPTS:
        return 'Proceeds from Investments'
    if concept in _SIGNED_OTHER_INVESTING_CONCEPTS:
        return 'Other Investing Activities'

    text = _compact_investing_text(concept)
    if not any(token in text for token in ('investment', 'securit')):
        return None
    if (any(token in text for token in (
            'acquisition', 'businesscombination', 'acquiredbusiness',
            'cashacquired'))
            and any(token in text for token in (
                'investment', 'securit', 'convertiblenote'))):
        return None
    purchase = any(token in text for token in (
        'paymentstoacquire', 'paymentforacquisition', 'purchaseof',
        'purchasesof', 'acquireinvestment'))
    proceeds = any(token in text for token in (
        'proceedsfrom', 'saleof', 'salesof', 'maturit', 'redemption',
        'distributionfrom'))
    if purchase == proceeds:
        return None
    prefix = 'Purchases of ' if purchase else 'Proceeds from '
    if 'alternativeinvestment' in text:
        return prefix + 'Alternative Investments'
    if any(token in text for token in (
            'marketablesecurit', 'availableforsale', 'shortterminvestment')):
        return prefix + 'Marketable Securities'
    if any(token in text for token in (
            'nonmarketable', 'otherinvestment', 'privateinvestment',
            'longterminvestment')):
        return prefix + 'Non-Marketable / Other Investments'
    # A directional extension with no subtype is a component, not proof that it
    # is the issuer's all-investments aggregate.  Keep it in the broad
    # non-marketable/other component so it can be summed safely with marketable
    # securities without overwriting either fact.
    return prefix + 'Non-Marketable / Other Investments'


def _investing_calc_weight(concept, max_hops=5):
    """Return the effective calculation weight into Investing Cash Flow."""
    frontier = {(str(concept or '').split(':')[-1], 1.0)}
    seen = set()
    blockers = _CF_OPERATING_PARENTS | _CF_FINANCING_PARENTS
    for _ in range(max_hops):
        nxt = set()
        for child, weight in sorted(frontier, key=lambda item: str(item[0])):
            if child in seen:
                continue
            seen.add(child)
            for parent, parent_weight in sorted(
                    GLOBAL_CALC_PARENT.get(child, ()),
                    key=lambda item: (str(item[0]), str(item[1]))):
                try:
                    effective = weight * float(parent_weight)
                except (TypeError, ValueError):
                    effective = weight
                if parent in _CF_INVESTING_PARENTS:
                    return effective
                if parent in blockers:
                    return None
                nxt.add((parent, effective))
        frontier = nxt
        if not frontier:
            break
    return None


def _prepare_investing_cash_flow_facts(df):
    """Split, sign, and provenance-stamp investing cash-flow families.

    Filer-authored statement-face labels take precedence over concept-name
    heuristics for opaque issuer extensions.  The older concept classifier then
    repairs caches that lack face-label provenance.  Finally, acquisition rows
    receive a conservative semantic family identity so verified concept
    migrations can quarterize without weakening exact-concept rules elsewhere.
    """
    required = {'Category', 'Label', 'Concept', 'Value'}
    if df is None or df.empty or not required.issubset(df.columns):
        return df
    out = df.copy()
    _ensure_object_column(out, 'SourceCanonicalizedFrom')
    out = _repair_misdirected_acquisition_cash_flows(out)
    out = _clear_standard_investment_face_aliases(out)

    cash_mask = out['Category'].eq('3_Cash_Flow')
    face_changed = 0
    face_signed = 0

    # First pass: exact filer face labels.  This is the path needed for PLTR's
    # opaque extension concepts (private securities, alternative investments,
    # and net business-combination cash flow).
    for idx, row in out.loc[cash_mask].iterrows():
        source_label = _investment_row_source_label(row)
        if not source_label:
            continue
        target = _classify_investment_face_label(source_label)
        if target is None:
            continue
        concept = str(row.get('Concept') or '').split(':')[-1]
        if not _investment_face_override_is_safe(
                concept, (row.get('Label'),), target, source_label):
            continue
        value = pd.to_numeric(pd.Series([row.get('Value')]),
                              errors='coerce').iloc[0]
        if pd.isna(value):
            continue
        weight = _investing_calc_weight(concept)

        # A signed business-combination line cannot be normalized safely
        # without its calculation-linkbase polarity.  Fall back to the existing
        # Acquisitions mapping when the filing does not provide that evidence.
        if target == _BUSINESS_COMBINATIONS_NET_LABEL:
            if weight is None:
                continue
            normalized = -abs(float(value)) * (1.0 if float(weight) > 0 else -1.0)
        elif target == 'Other Investing Activities':
            marker = 'investment_face_calc_weight_signed'
            prior_markers = str(row.get('SourceCanonicalizedFrom') or '').split(';')
            if marker in prior_markers:
                normalized = float(value)
            elif weight is not None:
                normalized = abs(float(value)) * (1.0 if float(weight) > 0 else -1.0)
                face_signed += 1
            else:
                # Preserve an already signed cached value.  Do not guess a sign
                # from a label alone when calculation ancestry is unavailable.
                normalized = float(value)
        else:
            normalized = abs(float(value))

        if str(row.get('Label')) != target:
            face_changed += 1
        out.at[idx, 'Label'] = target
        out.at[idx, 'Value'] = normalized
        _stamp_investment_family_metadata(
            out, idx, target, source_label,
            origin=str(row.get('SourceLabelOrigin') or 'fact_or_cache'))
        _append_source_marker(
            out, pd.Series(out.index == idx, index=out.index),
            'investment_face_family_classification')
        if target == 'Other Investing Activities' and weight is not None:
            _append_source_marker(
                out, pd.Series(out.index == idx, index=out.index),
                'investment_face_calc_weight_signed')

    # Cached/native rows can lack a usable face label even when the concept
    # itself explicitly says business combinations net of cash acquired.
    # Recover only that exact semantic construction and require investing
    # calculation ancestry for the economic sign.
    business_candidate = (
        out['Category'].eq('3_Cash_Flow')
        & out['Label'].isin({'Other Investing Activities', 'Acquisitions'})
    )
    for idx, row in out.loc[business_candidate].iterrows():
        concept = str(row.get('Concept') or '').split(':')[-1]
        compact = _compact_acquisition_text(concept)
        if not ('businesscombination' in compact
                and 'netofcashacquired' in compact):
            continue
        weight = _investing_calc_weight(concept)
        if weight is None:
            continue
        value = pd.to_numeric(
            pd.Series([row.get('Value')]), errors='coerce').iloc[0]
        if pd.isna(value):
            continue
        out.at[idx, 'Label'] = _BUSINESS_COMBINATIONS_NET_LABEL
        out.at[idx, 'Value'] = -abs(float(value)) * (
            1.0 if float(weight) > 0 else -1.0)
        _stamp_investment_family_metadata(
            out, idx, _BUSINESS_COMBINATIONS_NET_LABEL,
            concept, origin='concept_name')

    # Second pass: exact/semantic concept classification for rows without a
    # verified face-family override.  This preserves the previous behavior for
    # standard concepts and repairs older native-extraction caches.
    candidate = (
        out['Category'].eq('3_Cash_Flow')
        & out['Label'].isin({
            'Purchases of Investments', 'Proceeds from Investments',
            'Proceeds from Asset Sales', 'Other Investing Activities',
            *_INVESTMENT_COMPONENT_LABELS,
        })
    )
    changed = 0
    signed = 0
    face_verified = out.get(
        'SourceAliasRule', pd.Series('', index=out.index)
    ).fillna('').astype(str).eq(_INVESTMENT_FACE_ALIAS_RULE)
    for concept in out.loc[candidate, 'Concept'].dropna().astype(str).unique():
        short = concept.split(':')[-1]
        concept_mask = (
            candidate & out['Concept'].astype(str).eq(concept)
            & ~face_verified)
        if not concept_mask.any():
            continue
        target = _classify_investment_cash_flow_concept(short)
        weight = _investing_calc_weight(short)
        current_labels = set(out.loc[concept_mask, 'Label'].astype(str))
        if (target is None
                and current_labels.intersection({
                    'Purchases of Investments', 'Proceeds from Investments'})
                and weight is not None):
            target = 'Other Investing Activities'

        if target is not None and any(
                label != target for label in current_labels):
            out.loc[concept_mask, 'Label'] = target
            if 'TagRank' in out.columns:
                target_info = CONCEPT_MAP.get(target, {})
                target_tags = (target_info.get('tags') or []
                               if isinstance(target_info, dict) else [])
                try:
                    target_rank = target_tags.index(short)
                except ValueError:
                    target_rank = 999
                out.loc[concept_mask, 'TagRank'] = target_rank
            changed += int(concept_mask.sum())

        if target == 'Other Investing Activities' and weight is not None:
            marker = 'investing_calc_weight_signed'
            already_signed = (
                out['SourceCanonicalizedFrom'].fillna('').astype(str)
                .str.split(';').map(lambda parts: marker in parts)
            )
            sign_mask = concept_mask & ~already_signed
            numeric = pd.to_numeric(
                out.loc[sign_mask, 'Value'], errors='coerce')
            out.loc[sign_mask, 'Value'] = numeric.abs() * (
                1.0 if float(weight) > 0 else -1.0)
            signed += int(numeric.notna().sum())
            if sign_mask.any():
                _append_source_marker(out, sign_mask, marker)

    # Repair acquisition-family provenance even when the live extractor did not
    # expose a usable presentation-tree label.  Strong issuer concept names are
    # sufficient semantic evidence, but the origin is recorded truthfully.
    acquisition_mask = (
        out['Category'].eq('3_Cash_Flow')
        & out['Label'].eq('Acquisitions'))
    for idx, row in out.loc[acquisition_mask].iterrows():
        source_label = str(row.get('SourceLabel') or '').strip()
        family = _classify_acquisition_cash_flow_family(source_label)
        origin = str(row.get('SourceLabelOrigin') or '').strip()
        if family is None:
            concept = str(row.get('Concept') or '').split(':')[-1]
            family = _classify_acquisition_cash_flow_family(concept)
            if family:
                source_label = concept
                origin = 'concept_name'
        if not family:
            continue
        equivalent = _ACQUISITION_EQUIVALENT_PREFIX + family
        out.at[idx, 'SourceLabel'] = source_label
        out.at[idx, 'SourceRawLabel'] = source_label
        out.at[idx, 'SourceLabelOrigin'] = origin or 'fact_or_cache'
        out.at[idx, 'SourceEquivalentConcept'] = equivalent
        out.at[idx, 'SourceAliasVerified'] = True
        out.at[idx, 'SourceAliasRule'] = _ACQUISITION_ALIAS_RULE
        out.at[idx, 'SourceMetricFamily'] = 'acquisitions.' + family
        out.at[idx, 'SourceMetricIdentity'] = family

    if face_changed or face_signed or changed or signed:
        print(
            f"  [Investing Granularity] Face-classified {face_changed} fact(s), "
            f"signed {face_signed}; concept-reclassified {changed}, signed "
            f"{signed}.")
    return out



def _repair_broad_other_granular_overlaps(df):
    """Remove stale broad-Other facts proven to duplicate granular rows.

    Comparative filings sometimes restate a prior broad ``Other investing
    activities`` amount after the activity has already been separated into a
    granular investment or business-combination line.  The latest broad fact
    can then double count the granular row.  This repair requires an exact
    same-context decomposition or a zero-before/zero-after continuity proof.
    """
    required = {'Category', 'Label', 'Concept', 'Value', 'FY', 'Q',
                'Start', 'End', 'Duration'}
    if df is None or df.empty or not required.issubset(df.columns):
        return df
    out = df.copy()
    cash = out['Category'].eq('3_Cash_Flow')
    granular_labels = {
        'Purchases of Non-Marketable / Other Investments',
        'Purchases of Alternative Investments',
        'Proceeds from Non-Marketable / Other Investments',
        'Proceeds from Alternative Investments',
        _BUSINESS_COMBINATIONS_NET_LABEL,
    }
    relevant = cash & out['Label'].isin(
        granular_labels | {'Other Investing Activities'})
    if not relevant.any():
        return out

    work = out.loc[relevant].copy()
    work['_Num'] = pd.to_numeric(work['Value'], errors='coerce')
    work = work[work['_Num'].notna()]
    context_cols = ['FY', 'Q', 'Start', 'End', 'Duration']
    drop = set()

    # Stage 1: same-context decomposition.  Keep the smallest broad amount
    # when the difference to a larger comparative broad amount is exactly
    # explained by one or more granular rows in that same context.
    for _, group in work.groupby(context_cols, dropna=False, sort=False):
        broad = group[group['Label'].eq('Other Investing Activities')].copy()
        granular = group[group['Label'].isin(granular_labels)].copy()
        if broad.empty or granular.empty:
            continue
        broad_values = sorted(set(float(v) for v in broad['_Num']))
        if len(broad_values) < 2:
            continue
        genuine = min(broad_values, key=abs)
        granular_by_label = []
        for _, label_rows in granular.groupby('Label', sort=False):
            # One normalized family contribution per context.
            vals = sorted(set(abs(float(v)) for v in label_rows['_Num']))
            if vals:
                granular_by_label.append(max(vals))
        possible = set(granular_by_label)
        if granular_by_label:
            possible.add(sum(granular_by_label))
        for larger in broad_values:
            if larger == genuine:
                continue
            delta = abs(abs(larger) - abs(genuine))
            tolerance = max(abs(larger), abs(genuine), delta, 1.0) * 0.001 + 1.0
            if not any(abs(delta - amount) <= tolerance for amount in possible):
                continue
            rows = broad[broad['_Num'].sub(larger).abs().le(tolerance)]
            drop.update(rows.index.tolist())

    if drop:
        out = out.drop(index=sorted(drop)).copy()

    # Stage 2: a lone broad amount equal to a granular amount is a duplicate
    # only when the same broad concept is zero in both an earlier and later
    # cumulative period while the granular family persists.
    cash = out['Category'].eq('3_Cash_Flow')
    work = out.loc[cash & out['Label'].isin(
        granular_labels | {'Other Investing Activities'})].copy()
    work['_Num'] = pd.to_numeric(work['Value'], errors='coerce')
    qrank = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}
    work['_QRank'] = work['Q'].astype(str).map(qrank).fillna(0).astype(int)
    stage2_drop = set()
    for fiscal_year, year in work.groupby(
            pd.to_numeric(work['FY'], errors='coerce'), dropna=True, sort=False):
        broad = year[year['Label'].eq('Other Investing Activities')].copy()
        granular = year[year['Label'].isin(granular_labels)].copy()
        if broad.empty or granular.empty:
            continue
        for idx, row in broad.iterrows():
            value = float(row['_Num'])
            if abs(value) <= 1.0:
                continue
            rank = int(row['_QRank'])
            same = granular[granular['_QRank'].eq(rank)]
            if same.empty:
                continue
            tolerance = max(abs(value), 1.0) * 0.001 + 1.0
            matching = same[same['_Num'].abs().sub(abs(value)).abs().le(tolerance)]
            if matching.empty:
                continue
            concept = str(row.get('Concept') or '')
            peers = broad[broad['Concept'].fillna('').astype(str).eq(concept)]
            prior_zero = peers[peers['_QRank'].lt(rank) & peers['_Num'].abs().le(1.0)]
            later_zero = peers[peers['_QRank'].gt(rank) & peers['_Num'].abs().le(1.0)]
            target_labels = set(matching['Label'].astype(str))
            later_granular = granular[
                granular['_QRank'].gt(rank)
                & granular['Label'].astype(str).isin(target_labels)]
            if (not prior_zero.empty and not later_zero.empty
                    and not later_granular.empty):
                stage2_drop.add(idx)

    if stage2_drop:
        out = out.drop(index=sorted(stage2_drop)).copy()
    removed = len(drop) + len(stage2_drop)
    if removed:
        print(
            f"  [Investing Overlap] Removed {removed} stale broad-Other "
            "comparative duplicate fact(s).")
    return out


def _repair_standard_investment_zero_baselines(df):
    """Repair late granular investment families without inventing quarters.

    A newly visible granular row does not by itself prove that all earlier
    activity was zero.  Three cases are handled separately:

    * If the same exact concept already has a discrete quarterly fact, a zero
      baseline is forbidden.  When an annual total exactly equals the sum of
      the available nonnegative direct quarters, a synthetic YTD9 baseline is
      created from that proven sum so Q4 can be derived correctly.
    * If an annual-only marketable component exactly equals a broader
      purchases/proceeds aggregate for the same year, the matching aggregate
      concept's YTD9 value is used as the component baseline.  Because these
      are nonnegative gross cash-flow families, exact annual equality proves
      that the aggregate contains no other component for that year.
    * Only when neither source of prior activity exists may the original
      exact-concept zero baseline be added.

    This preserves PLTR's genuinely late granular families while preventing
    annual cumulative facts from being published as discrete AMZN quarters.
    """
    required = {'Category', 'Label', 'Concept', 'Value', 'FY', 'Q',
                'Start', 'End', 'Duration'}
    if df is None or df.empty or not required.issubset(df.columns):
        return df
    out = df.copy()
    cash = out['Category'].eq('3_Cash_Flow')
    targets = set(_INVESTMENT_COMPONENT_LABELS) | {
        _BUSINESS_COMBINATIONS_NET_LABEL,
        'Other Investing Activities'}
    qrank = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}

    def _cumulative(frame):
        d = pd.to_numeric(frame['Duration'], errors='coerce')
        q = frame['Q'].astype(str)
        return (
            q.eq('Q1') & d.between(45, 125)
            | q.eq('Q2') & d.between(140, 230)
            | q.eq('Q3') & d.between(220, 320)
            | q.eq('Q4') & d.between(300, 400))

    def _discrete_quarter(frame):
        d = pd.to_numeric(frame['Duration'], errors='coerce')
        q = frame['Q'].astype(str)
        # Q1 is both discrete and YTD, and never needs a prior baseline.
        return q.isin({'Q2', 'Q3', 'Q4'}) & d.between(20, 125)

    def _best(rows):
        if rows.empty:
            return None
        work = rows.copy()
        work['_FiledSort'] = pd.to_datetime(
            work.get('Filed', pd.Series(pd.NaT, index=work.index)),
            errors='coerce')
        work['_CalcSort'] = work.get(
            'IsCalculated', pd.Series(False, index=work.index)
        ).fillna(False).astype(bool)
        work['_TagSort'] = pd.to_numeric(
            work.get('TagRank', pd.Series(999, index=work.index)),
            errors='coerce').fillna(999)
        return work.sort_values(
            ['_FiledSort', '_CalcSort', '_TagSort'],
            ascending=[False, True, True]).iloc[0]

    def _same_amount(left, right):
        try:
            left = float(left); right = float(right)
        except (TypeError, ValueError):
            return False
        tolerance = max(abs(left), abs(right), 1.0) * 0.001 + 1.0
        return abs(left - right) <= tolerance

    def _clean_baseline(anchor, target, concept, value, first_source,
                        derivation, marker):
        baseline = anchor.copy()
        baseline['Label'] = target
        baseline['Value'] = float(value)
        baseline['Concept'] = concept
        baseline['IsCalculated'] = True
        baseline['TagRank'] = -1
        baseline['SourceAliasVerified'] = False
        baseline['SourceAliasRule'] = np.nan
        baseline['SourceEquivalentConcept'] = np.nan
        baseline['SourceMetricFamily'] = np.nan
        baseline['SourceMetricIdentity'] = np.nan
        baseline['SourceSemanticType'] = target
        baseline['SourceLabel'] = first_source.get('SourceLabel')
        baseline['SourceRawLabel'] = first_source.get('SourceRawLabel')
        baseline['SourceLabelOrigin'] = (
            first_source.get('SourceLabelOrigin')
            or 'verified_investment_quarterization')
        baseline['SourceDerivation'] = derivation
        baseline['SourcePeriodRole'] = 'derived_reclassification'
        baseline['SourceCanonicalizedFrom'] = marker
        return baseline.drop(
            labels=['_QRank', '_Cumulative', '_DiscreteQuarter',
                    '_FiledSort', '_CalcSort', '_TagSort'],
            errors='ignore')

    def _aggregate_parent(target):
        if target in _INVESTMENT_PURCHASE_COMPONENT_LABELS:
            return 'Purchases of Investments'
        if target in _INVESTMENT_PROCEEDS_COMPONENT_LABELS:
            return 'Proceeds from Investments'
        return None

    additions = []
    repaired = []
    fiscal_years = pd.to_numeric(
        out.loc[cash, 'FY'], errors='coerce').dropna().astype(int).unique()
    for fiscal_year in sorted(fiscal_years):
        year = out.loc[
            cash & pd.to_numeric(out['FY'], errors='coerce').eq(fiscal_year)
        ].copy()
        if year.empty:
            continue
        year['_QRank'] = year['Q'].astype(str).map(qrank).fillna(0).astype(int)
        year['_Cumulative'] = _cumulative(year)
        year['_DiscreteQuarter'] = _discrete_quarter(year)
        totals = year[
            year['Label'].eq('Investing Cash Flow') & year['_Cumulative']]
        broad_other = year[
            year['Label'].eq('Other Investing Activities')
            & year['_Cumulative']]

        for target in sorted(targets):
            target_rows = year[
                year['Label'].eq(target) & year['_Cumulative']].copy()
            if target_rows.empty:
                continue
            for concept, concept_rows in target_rows.groupby(
                    target_rows['Concept'].fillna('').astype(str),
                    sort=False):
                if not concept:
                    continue
                first_rank = int(concept_rows['_QRank'].min())
                if first_rank <= 1:
                    continue
                prior_rank = first_rank - 1
                if not totals['_QRank'].eq(prior_rank).any():
                    continue
                if target_rows['_QRank'].lt(first_rank).any():
                    continue

                first_source = _best(concept_rows[
                    concept_rows['_QRank'].eq(first_rank)])
                if first_source is None:
                    continue
                first_value = pd.to_numeric(
                    pd.Series([first_source.get('Value')]),
                    errors='coerce').iloc[0]
                if pd.isna(first_value):
                    continue
                first_value = float(first_value)

                all_concept_rows = year[
                    year['Label'].eq(target)
                    & year['Concept'].fillna('').astype(str).eq(concept)
                ].copy()
                direct_rows = all_concept_rows[
                    all_concept_rows['_DiscreteQuarter']
                    & all_concept_rows['_QRank'].le(first_rank)]

                # A direct fact proves the family was not absent before the
                # first cumulative rendering.  Never manufacture a zero.  For
                # an annual-only cumulative fact, derive a YTD9 baseline only
                # when the annual total exactly equals the nonnegative direct
                # quarterly facts already reported through Q3.
                if not direct_rows.empty:
                    if (first_rank == 4
                            and target in _INVESTMENT_COMPONENT_LABELS
                            and first_value >= 0):
                        quarter_values = []
                        conflict = False
                        for rank in (1, 2, 3):
                            rows_at_rank = direct_rows[
                                direct_rows['_QRank'].eq(rank)].copy()
                            if rows_at_rank.empty:
                                continue
                            numeric = pd.to_numeric(
                                rows_at_rank['Value'], errors='coerce').dropna()
                            distinct = []
                            for value in numeric:
                                value = float(value)
                                if not any(_same_amount(value, prior)
                                           for prior in distinct):
                                    distinct.append(value)
                            if len(distinct) != 1 or distinct[0] < 0:
                                conflict = True
                                break
                            quarter_values.append(distinct[0])
                        direct_sum = float(sum(quarter_values))
                        if (not conflict and quarter_values
                                and _same_amount(first_value, direct_sum)):
                            anchor = _best(totals[
                                totals['_QRank'].eq(3)])
                            if anchor is not None:
                                additions.append(_clean_baseline(
                                    anchor, target, concept, direct_sum,
                                    first_source,
                                    'reported_direct_quarters_sum_to_annual_'
                                    'investment_family_ytd9_baseline',
                                    _INVESTMENT_MIGRATION_RULE
                                    + ':direct_quarters_equal_annual'))

                                # A mathematically proven zero Q4 can be lost by
                                # generic publication cleanup when represented
                                # only as annual minus YTD.  Preserve it as an
                                # explicit derived discrete-quarter fact.
                                q4_zero = first_source.copy()
                                q3_end = pd.to_datetime(
                                    anchor.get('End'), errors='coerce')
                                annual_end = pd.to_datetime(
                                    first_source.get('End'), errors='coerce')
                                if pd.notna(q3_end) and pd.notna(annual_end):
                                    q4_start = q3_end + pd.Timedelta(days=1)
                                    q4_zero['Start'] = q4_start.strftime('%Y-%m-%d')
                                    q4_zero['End'] = annual_end.strftime('%Y-%m-%d')
                                    q4_zero['Duration'] = int(
                                        (annual_end - q4_start).days)
                                    q4_zero['Q'] = 'Q4'
                                    q4_zero['Value'] = 0.0
                                    q4_zero['Concept'] = concept
                                    q4_zero['IsCalculated'] = True
                                    q4_zero['TagRank'] = -2
                                    q4_zero['SourceAliasVerified'] = False
                                    q4_zero['SourceAliasRule'] = np.nan
                                    q4_zero['SourceEquivalentConcept'] = np.nan
                                    q4_zero['SourceMetricFamily'] = np.nan
                                    q4_zero['SourceMetricIdentity'] = np.nan
                                    q4_zero['SourceSemanticType'] = target
                                    q4_zero['SourceDerivation'] = (
                                        'annual_equals_reported_direct_quarters_'
                                        'derived_zero_q4')
                                    q4_zero['SourcePeriodRole'] = (
                                        'derived_discrete_quarter')
                                    q4_zero['SourceCanonicalizedFrom'] = (
                                        _INVESTMENT_MIGRATION_RULE
                                        + ':direct_quarters_equal_annual_zero_q4')
                                    additions.append(q4_zero.drop(
                                        labels=['_QRank', '_Cumulative',
                                                '_DiscreteQuarter', '_FiledSort',
                                                '_CalcSort', '_TagSort'],
                                        errors='ignore'))
                                repaired.append(
                                    f'FY{fiscal_year}:{target}:{concept}:'
                                    'direct-sum-ytd9-zero-q4')
                    continue

                # A later standard component can be a taxonomy refinement of a
                # broader parent.  Exact annual equality plus the same parent
                # concept's YTD9 fact proves a safe baseline for nonnegative
                # purchase/proceeds families.  Use the matching parent concept,
                # not another aggregate component in the same normalized row.
                parent_label = _aggregate_parent(target)
                if (first_rank == 4 and parent_label
                        and first_value > 1.0):
                    parent_annual = year[
                        year['Label'].eq(parent_label)
                        & year['_Cumulative']
                        & year['_QRank'].eq(4)].copy()
                    parent_annual['_Num'] = pd.to_numeric(
                        parent_annual['Value'], errors='coerce')
                    matching_annual = parent_annual[
                        parent_annual['_Num'].map(
                            lambda value: pd.notna(value)
                            and _same_amount(value, first_value))]
                    parent_match = _best(matching_annual)
                    if parent_match is not None:
                        parent_concept = str(
                            parent_match.get('Concept') or '').strip()
                        parent_prior = year[
                            year['Label'].eq(parent_label)
                            & year['_Cumulative']
                            & year['_QRank'].eq(3)]
                        if parent_concept:
                            parent_prior = parent_prior[
                                parent_prior['Concept'].fillna('').astype(str)
                                .eq(parent_concept)]
                        prior_source = _best(parent_prior)
                        if prior_source is not None:
                            prior_value = pd.to_numeric(
                                pd.Series([prior_source.get('Value')]),
                                errors='coerce').iloc[0]
                            if (pd.notna(prior_value)
                                    and 0 <= float(prior_value)
                                    <= first_value + max(
                                        first_value * 0.001, 1.0)):
                                additions.append(_clean_baseline(
                                    prior_source, target, concept,
                                    float(prior_value), first_source,
                                    'broader_investment_parent_annual_equals_'
                                    'component_annual_ytd9_baseline',
                                    _INVESTMENT_MIGRATION_RULE
                                    + ':aggregate_annual_equals_component'))
                                repaired.append(
                                    f'FY{fiscal_year}:{target}:{concept}:'
                                    'aggregate-equality-ytd9')
                                continue

                prior_broad = broad_other[
                    broad_other['_QRank'].eq(prior_rank)]
                if not prior_broad.empty:
                    prior_abs = float(pd.to_numeric(
                        prior_broad['Value'], errors='coerce').abs().max())
                    tolerance = max(abs(first_value), prior_abs, 1.0) * 0.001 + 1.0
                    # A comparable prior broad amount is a migration candidate,
                    # not proof of zero history.
                    if (prior_abs > 1_000_000.0
                            and abs(prior_abs - abs(first_value)) <= max(
                                tolerance, abs(first_value) * 0.25)):
                        continue

                anchor = _best(totals[totals['_QRank'].eq(prior_rank)])
                if anchor is None:
                    continue
                baseline = _clean_baseline(
                    anchor, target, concept, 0.0, first_source,
                    'prior_cumulative_statement_zero_baseline_for_late_'
                    'investment_family',
                    _INVESTMENT_MIGRATION_RULE + ':exact_zero_prior_period')
                if bool(first_source.get('SourceAliasVerified', False)):
                    baseline['SourceAliasVerified'] = True
                    for metadata_column in (
                            'SourceAliasRule', 'SourceEquivalentConcept',
                            'SourceMetricFamily', 'SourceMetricIdentity'):
                        baseline[metadata_column] = first_source.get(
                            metadata_column)
                additions.append(baseline)
                repaired.append(
                    f'FY{fiscal_year}:{target}:{concept}:zero')

    if additions:
        out = pd.concat([out, pd.DataFrame(additions)],
                        ignore_index=True, sort=False)
        print('  [Investing Baseline] Added verified prior baseline(s): ' +
              ', '.join(repaired))
    return out

def _repair_investment_family_migrations(df):
    """Transfer a proven broad-Other baseline into a later granular family.

    Some filers initially present a purchase in ``Other investing activities``
    and later separate the same year-to-date cash flow as private/non-marketable
    or alternative-investment purchases.  Ordinary cumulative subtraction then
    creates a false reversal in Other.  This repair changes classification only,
    never total investing cash flow, and requires a narrow within-year pattern:

    * the granular family first appears in a later cumulative period;
    * an earlier nonzero broad-Other outflow exists with no granular peer;
    * the later granular cumulative amount contains that earlier baseline; and
    * broad Other disappears or becomes immaterial after the transition.

    Ambiguous years or multiple matching granular families fail closed.
    """
    required = {'Category', 'Label', 'Value', 'FY', 'Q', 'Duration'}
    if df is None or df.empty or not required.issubset(df.columns):
        return df
    out = df.copy()
    cash = out['Category'].eq('3_Cash_Flow')
    if not cash.any():
        return out

    qrank = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}

    def _rank_series(frame):
        return frame['Q'].astype(str).map(qrank).fillna(0).astype(int)

    def _is_cumulative_row(row):
        quarter = str(row.get('Q') or '')
        duration = pd.to_numeric(
            pd.Series([row.get('Duration')]), errors='coerce').iloc[0]
        if pd.isna(duration):
            return False
        if quarter == 'Q1':
            return 45 <= float(duration) <= 125
        lower = {'Q2': 140, 'Q3': 220, 'Q4': 300}.get(quarter)
        upper = {'Q2': 230, 'Q3': 320, 'Q4': 400}.get(quarter)
        return lower is not None and lower <= float(duration) <= upper

    def _best_period_row(rows):
        if rows.empty:
            return None
        work = rows.copy()
        work['_FiledSort'] = pd.to_datetime(
            work.get('Filed', pd.Series(pd.NaT, index=work.index)),
            errors='coerce')
        work['_CalcSort'] = work.get(
            'IsCalculated', pd.Series(False, index=work.index)
        ).fillna(False).astype(bool)
        work['_RankSort'] = pd.to_numeric(
            work.get('TagRank', pd.Series(999, index=work.index)),
            errors='coerce').fillna(999)
        return work.sort_values(
            ['_FiledSort', '_CalcSort', '_RankSort'],
            ascending=[False, True, True]).iloc[0]

    migrated = []
    fiscal_years = pd.to_numeric(
        out.loc[cash, 'FY'], errors='coerce').dropna().astype(int).unique()
    for fiscal_year in sorted(fiscal_years):
        year = out.loc[
            cash & pd.to_numeric(out['FY'], errors='coerce').eq(fiscal_year)
        ].copy()
        if year.empty:
            continue
        year['_QRank'] = _rank_series(year)
        year['_Cumulative'] = year.apply(_is_cumulative_row, axis=1)
        broad = year[
            year['Label'].eq('Other Investing Activities')
            & year['_Cumulative']].copy()
        if broad.empty:
            continue

        candidates = []
        for target in sorted(_INVESTMENT_MIGRATION_PURCHASE_LABELS):
            specific = year[
                year['Label'].eq(target) & year['_Cumulative']
                & pd.to_numeric(year['Value'], errors='coerce').gt(0)
            ].copy()
            if specific.empty:
                continue
            first_rank = int(specific['_QRank'].min())
            if first_rank <= 1:
                continue
            prior_specific = specific[specific['_QRank'] < first_rank]
            if not prior_specific.empty:
                continue
            prior_broad = broad[
                (broad['_QRank'] < first_rank)
                & pd.to_numeric(broad['Value'], errors='coerce').lt(0)
            ].copy()
            if prior_broad.empty:
                continue
            prior_rank = int(prior_broad['_QRank'].max())
            prior_row = _best_period_row(
                prior_broad[prior_broad['_QRank'].eq(prior_rank)])
            first_row = _best_period_row(
                specific[specific['_QRank'].eq(first_rank)])
            if prior_row is None or first_row is None:
                continue
            baseline = abs(float(prior_row['Value']))
            first_total = abs(float(first_row['Value']))
            tolerance = max(1.0, 0.001 * max(baseline, first_total, 1.0))
            if baseline <= tolerance or first_total + tolerance < baseline:
                continue

            later_broad = broad[broad['_QRank'] >= first_rank].copy()
            # A later comparative filing can repeat the newly separated
            # granular cumulative amount under the old broad-Other concept.
            # Treat that row as a stale presentation duplicate only when a
            # subsequent granular period persists and broad Other then
            # disappears or becomes immaterial.  This is the PLTR 2025 pattern:
            # Q2 broad Other == Q2 private purchases, followed by Q3 private
            # purchases plus only a $1M genuine Other outflow.
            immaterial_limit = max(1_000_000.0, 0.10 * baseline)
            duplicate_later_indices = set()
            if not later_broad.empty:
                for duplicate_rank in sorted(set(
                        later_broad['_QRank']) & set(specific['_QRank'])):
                    broad_at_rank = later_broad[
                        later_broad['_QRank'].eq(duplicate_rank)]
                    specific_at_rank = specific[
                        specific['_QRank'].eq(duplicate_rank)]
                    broad_row = _best_period_row(broad_at_rank)
                    specific_row = _best_period_row(specific_at_rank)
                    if broad_row is None or specific_row is None:
                        continue
                    broad_value = abs(float(broad_row['Value']))
                    specific_value = abs(float(specific_row['Value']))
                    equal_tolerance = max(
                        1.0, 0.001 * max(broad_value, specific_value, 1.0))
                    if abs(broad_value - specific_value) > equal_tolerance:
                        continue
                    future_specific = specific[
                        specific['_QRank'].gt(duplicate_rank)]
                    if future_specific.empty:
                        continue
                    future_broad = broad[
                        broad['_QRank'].gt(duplicate_rank)]
                    future_material = 0.0
                    if not future_broad.empty:
                        future_material = float(pd.to_numeric(
                            future_broad['Value'], errors='coerce').abs().max())
                    if future_material > immaterial_limit + equal_tolerance:
                        continue
                    matching = broad_at_rank[
                        pd.to_numeric(broad_at_rank['Value'], errors='coerce')
                        .abs().sub(specific_value).abs().le(equal_tolerance)
                    ]
                    duplicate_later_indices.update(matching.index.tolist())

            later_for_materiality = later_broad.drop(
                index=list(duplicate_later_indices), errors='ignore')
            later_material = 0.0
            if not later_for_materiality.empty:
                later_material = float(pd.to_numeric(
                    later_for_materiality['Value'], errors='coerce').abs().max())
            # A surviving broad amount must be immaterial relative to the
            # transferred baseline; otherwise it may represent a genuine other
            # activity rather than a scope reset.
            if later_material > immaterial_limit + tolerance:
                continue

            latest_rank = int(specific['_QRank'].max())
            latest_row = _best_period_row(
                specific[specific['_QRank'].eq(latest_rank)])
            if latest_row is None:
                continue
            latest_total = abs(float(latest_row['Value']))
            if latest_total + tolerance < baseline:
                continue
            # A single late annual disclosure is accepted only when it exactly
            # identifies the prior broad baseline.  Otherwise require persistence
            # across at least two cumulative filings.
            distinct_specific_periods = specific['_QRank'].nunique()
            if (distinct_specific_periods < 2
                    and abs(latest_total - baseline) > tolerance):
                continue
            target_concepts = {
                str(value).strip() for value in specific['Concept'].dropna()
                if str(value).strip()
            } if 'Concept' in specific.columns else set()
            target_concept = (
                next(iter(target_concepts)) if len(target_concepts) == 1
                else None)
            broad_concept_rows = pd.concat(
                [prior_broad, later_for_materiality], ignore_index=False,
                sort=False)
            broad_concepts = {
                str(value).strip()
                for value in broad_concept_rows.get(
                    'Concept', pd.Series(dtype=object)).dropna()
                if str(value).strip()
            }
            broad_concept = (
                next(iter(broad_concepts)) if len(broad_concepts) == 1
                else None)
            candidates.append((
                target, first_rank, baseline,
                tuple(sorted(duplicate_later_indices)),
                target_concept, broad_concept))

        if len(candidates) != 1:
            continue
        (target, first_rank, baseline, duplicate_later_indices,
         target_concept, broad_concept) = candidates[0]

        # Standard concepts normally keep exact-concept identity, but a proven
        # broad-Other -> granular migration also needs the reported later
        # cumulative rows and the reclassified earlier baseline to share one
        # publication identity.  Restore the strong filer-face identity only
        # for this exact concept, fiscal year, and target row.  This does not
        # alias different standard concepts and therefore cannot recreate the
        # marketable-security scope collision that the global scrub prevents.
        if target_concept:
            target_year_mask = (
                cash
                & pd.to_numeric(out['FY'], errors='coerce').eq(fiscal_year)
                & out['Label'].eq(target)
                & out.get('Concept', pd.Series('', index=out.index))
                    .fillna('').astype(str).eq(target_concept)
                & out.apply(_is_cumulative_row, axis=1)
            )
            for target_idx in out.index[target_year_mask]:
                source_label = _investment_row_source_label(
                    out.loc[target_idx])
                if (_classify_investment_face_label(source_label)
                        == target):
                    _stamp_investment_family_metadata(
                        out, target_idx, target, source_label,
                        origin='verified_migration_target_face')

        migration_mask = (
            cash & pd.to_numeric(out['FY'], errors='coerce').eq(fiscal_year)
            & out['Label'].eq('Other Investing Activities')
            & out.apply(_is_cumulative_row, axis=1)
            & out['Q'].astype(str).map(qrank).fillna(0).lt(first_rank)
            & pd.to_numeric(out['Value'], errors='coerce').lt(0)
            & pd.to_numeric(out['Value'], errors='coerce').abs().le(
                baseline * 1.001 + 1.0)
        )
        if not migration_mask.any():
            continue

        # This repair writes provenance text/boolean metadata into columns
        # that may be completely absent (or all-null float64) in a cold native
        # cache.  Pandas 3.x no longer silently upcasts those columns.  Make
        # every metadata destination used by this migration text-safe before
        # the first assignment.  This is storage-only and cannot change the
        # financial Value/Label/Concept decisions made above.
        for _migration_metadata_column in (
                'SourceOriginalConcept', 'SourceAliasVerified',
                'SourceAliasRule', 'SourceEquivalentConcept',
                'SourceMetricFamily', 'SourceMetricIdentity',
                'SourceSemanticType', 'SourceDerivation',
                'SourcePeriodRole', 'SourceCanonicalizedFrom'):
            _ensure_object_column(out, _migration_metadata_column)

        # Neutralize stale broad-Other comparative duplicates that equal the
        # newly separated granular family.  Keep the rows as explicit derived
        # zero baselines so later quarter selection cannot resurrect them.
        if duplicate_later_indices:
            duplicate_mask = out.index.isin(duplicate_later_indices)
            out.loc[duplicate_mask, 'Value'] = 0.0
            # Preserve the original broad concept so later genuine Other
            # cumulative facts remain exact-concept compatible.
            out.loc[duplicate_mask, 'IsCalculated'] = True
            out.loc[duplicate_mask, 'TagRank'] = -1
            out.loc[duplicate_mask, 'SourceAliasVerified'] = True
            out.loc[duplicate_mask, 'SourceAliasRule'] = (
                _INVESTMENT_MIGRATION_RULE)
            out.loc[duplicate_mask, 'SourceEquivalentConcept'] = (
                _INVESTMENT_EQUIVALENT_PREFIX
                + 'other_investing_activities')
            out.loc[duplicate_mask, 'SourceMetricFamily'] = (
                'investing.other_investing_activities')
            out.loc[duplicate_mask, 'SourceMetricIdentity'] = (
                'other_investing_activities')
            out.loc[duplicate_mask, 'SourceSemanticType'] = (
                'Other Investing Activities')
            out.loc[duplicate_mask, 'SourceDerivation'] = (
                'stale_broad_other_duplicate_of_granular_family')
            out.loc[duplicate_mask, 'SourcePeriodRole'] = (
                'derived_reclassification')
            _append_source_marker(
                out, pd.Series(duplicate_mask, index=out.index),
                _INVESTMENT_MIGRATION_RULE
                + ':stale_broad_other_duplicate')
            if broad_concept:
                # The reclassified baseline now carries the same concrete
                # concept as the later cumulative family.  Exact-concept
                # arithmetic must win over the synthetic alias identity.
                out.loc[duplicate_mask, 'SourceAliasVerified'] = False
                out.loc[duplicate_mask, 'SourceAliasRule'] = np.nan
                out.loc[duplicate_mask, 'SourceEquivalentConcept'] = np.nan

        source_rows = out.loc[migration_mask].copy()
        if target_concept:
            out.loc[migration_mask, 'SourceOriginalConcept'] = (
                out.loc[migration_mask, 'Concept'].astype(object))
            out.loc[migration_mask, 'Concept'] = target_concept
        out.loc[migration_mask, 'Label'] = target
        out.loc[migration_mask, 'Value'] = pd.to_numeric(
            out.loc[migration_mask, 'Value'], errors='coerce').abs()
        out.loc[migration_mask, 'IsCalculated'] = True
        out.loc[migration_mask, 'SourceAliasVerified'] = True
        out.loc[migration_mask, 'SourceAliasRule'] = _INVESTMENT_MIGRATION_RULE
        _target_identity = re.sub(
            r'[^a-z0-9]+', '_', target.casefold()).strip('_')
        out.loc[migration_mask, 'SourceEquivalentConcept'] = (
            _INVESTMENT_EQUIVALENT_PREFIX + _target_identity)
        out.loc[migration_mask, 'SourceMetricFamily'] = (
            'investing.' + _target_identity)
        out.loc[migration_mask, 'SourceMetricIdentity'] = _target_identity
        out.loc[migration_mask, 'SourceSemanticType'] = target
        out.loc[migration_mask, 'SourceDerivation'] = (
            'broad_other_reclassified_to_later_granular_family')
        out.loc[migration_mask, 'SourcePeriodRole'] = 'derived_reclassification'
        _append_source_marker(
            out, migration_mask,
            _INVESTMENT_MIGRATION_RULE + ':' + target)
        # The reclassified row is derived from a verified within-year face-line
        # migration.  Retain that narrow family proof even when the later
        # granular concept is concrete; otherwise publication gates can discard
        # the reported Q1 baseline before cumulative quarterization.  This alias
        # is confined to the migration-derived row and does not make unrelated
        # standard investment concepts interchangeable.

        # Preserve a zero broad-family baseline for the same periods so the
        # quarterizer cannot subtract the pre-reclassification amount from a
        # later genuine Other line.
        zeros = source_rows.copy()
        zeros['Label'] = 'Other Investing Activities'
        zeros['Value'] = 0.0
        zeros['Concept'] = (
            broad_concept or 'DerivedInvestmentFamilyMigrationOtherBaseline')
        zeros['IsCalculated'] = True
        zeros['TagRank'] = -1
        zeros['SourceAliasVerified'] = True
        zeros['SourceAliasRule'] = _INVESTMENT_MIGRATION_RULE
        zeros['SourceEquivalentConcept'] = (
            _INVESTMENT_EQUIVALENT_PREFIX
            + 'other_investing_activities')
        zeros['SourceMetricFamily'] = 'investing.other_investing_activities'
        zeros['SourceMetricIdentity'] = 'other_investing_activities'
        zeros['SourceSemanticType'] = 'Other Investing Activities'
        zeros['SourceDerivation'] = (
            'broad_other_baseline_reset_after_granular_reclassification')
        zeros['SourcePeriodRole'] = 'derived_reclassification'
        zeros['SourceCanonicalizedFrom'] = (
            _INVESTMENT_MIGRATION_RULE + ':zero_other_baseline')
        if broad_concept:
            zeros['SourceAliasVerified'] = False
            zeros['SourceAliasRule'] = np.nan
            zeros['SourceEquivalentConcept'] = np.nan

        # Also create a zero broad-Other cumulative baseline for each granular
        # filing period where the filer no longer presents an Other line.  The
        # transition quarter is essential: without a Q2 zero in PLTR 2025, the
        # later nine-month $1M Other outflow cannot be isolated as Q3.
        specific_period_rows = out.loc[
            cash & pd.to_numeric(out['FY'], errors='coerce').eq(fiscal_year)
            & out['Label'].eq(target)
            & out.apply(_is_cumulative_row, axis=1)
        ].copy()
        existing_broad_ranks = set(
            _rank_series(out.loc[
                cash & pd.to_numeric(out['FY'], errors='coerce').eq(fiscal_year)
                & out['Label'].eq('Other Investing Activities')
                & out.apply(_is_cumulative_row, axis=1)
            ]).tolist())
        existing_broad_ranks.update(_rank_series(zeros).tolist())
        synthetic_period_zeros = []
        if not specific_period_rows.empty:
            specific_period_rows['_QRank'] = _rank_series(
                specific_period_rows)
            for period_rank, period_rows in specific_period_rows.groupby(
                    '_QRank', sort=True):
                if int(period_rank) in existing_broad_ranks:
                    continue
                period_row = _best_period_row(period_rows)
                if period_row is None:
                    continue
                zero = period_row.copy()
                zero['Label'] = 'Other Investing Activities'
                zero['Value'] = 0.0
                zero['Concept'] = (
                    broad_concept
                    or 'DerivedInvestmentFamilyMigrationOtherBaseline')
                zero['IsCalculated'] = True
                zero['TagRank'] = -1
                zero['SourceAliasVerified'] = True
                zero['SourceAliasRule'] = _INVESTMENT_MIGRATION_RULE
                zero['SourceEquivalentConcept'] = (
                    _INVESTMENT_EQUIVALENT_PREFIX
                    + 'other_investing_activities')
                zero['SourceMetricFamily'] = (
                    'investing.other_investing_activities')
                zero['SourceMetricIdentity'] = (
                    'other_investing_activities')
                zero['SourceSemanticType'] = (
                    'Other Investing Activities')
                zero['SourceDerivation'] = (
                    'missing_broad_other_period_reset_after_granular_'
                    'reclassification')
                zero['SourcePeriodRole'] = 'derived_reclassification'
                zero['SourceCanonicalizedFrom'] = (
                    _INVESTMENT_MIGRATION_RULE
                    + ':zero_other_transition_period')
                if broad_concept:
                    zero['SourceAliasVerified'] = False
                    zero['SourceAliasRule'] = np.nan
                    zero['SourceEquivalentConcept'] = np.nan
                synthetic_period_zeros.append(zero.drop(
                    labels=['_QRank', '_Cumulative', '_FiledSort',
                            '_CalcSort', '_RankSort'], errors='ignore'))

        # When the transferred broad baseline first appears after Q1, a
        # directly extracted prior-quarter Investing Cash Flow context proves
        # that the earlier filing exists and omitted both the broad and granular
        # family.  Add a zero granular cumulative baseline so the transferred
        # amount is assigned to the correct discrete quarter rather than left
        # in the bridge residual (PLTR 2024 H1 -> Q2).
        synthetic_target_baselines = []
        synthetic_prior_other_baselines = []
        migrated_ranks = sorted(set(
            out.loc[migration_mask, 'Q'].astype(str)
            .map(qrank).fillna(0).astype(int).tolist()))
        if migrated_ranks and migrated_ranks[0] > 1:
            prior_rank = migrated_ranks[0] - 1
            prior_total = year[
                year['Label'].eq('Investing Cash Flow')
                & year['_Cumulative']
                & year['_QRank'].eq(prior_rank)
            ]
            prior_target = year[
                year['Label'].eq(target)
                & year['_Cumulative']
                & year['_QRank'].eq(prior_rank)
            ]
            prior_broad_existing = broad[broad['_QRank'].eq(prior_rank)]
            if (not prior_total.empty and prior_target.empty
                    and prior_broad_existing.empty):
                anchor = _best_period_row(prior_total)
                if anchor is not None:
                    zero_target = anchor.copy()
                    zero_target['Label'] = target
                    zero_target['Value'] = 0.0
                    zero_target['Concept'] = (
                        target_concept
                        or 'DerivedInvestmentFamilyMigrationTargetBaseline')
                    zero_target['IsCalculated'] = True
                    zero_target['TagRank'] = -1
                    zero_target['SourceAliasVerified'] = True
                    zero_target['SourceAliasRule'] = (
                        _INVESTMENT_MIGRATION_RULE)
                    zero_target['SourceEquivalentConcept'] = (
                        _INVESTMENT_EQUIVALENT_PREFIX + _target_identity)
                    zero_target['SourceMetricFamily'] = (
                        'investing.' + _target_identity)
                    zero_target['SourceMetricIdentity'] = _target_identity
                    zero_target['SourceSemanticType'] = target
                    zero_target['SourceDerivation'] = (
                        'prior_filing_zero_baseline_for_migrated_'
                        'granular_family')
                    zero_target['SourcePeriodRole'] = (
                        'derived_reclassification')
                    zero_target['SourceCanonicalizedFrom'] = (
                        _INVESTMENT_MIGRATION_RULE
                        + ':zero_target_prior_period')
                    # This zero exists only because the same verified
                    # migration proves that the later granular family was absent
                    # in the prior filing.  Retain the migration-family identity
                    # so the zero and the reclassified cumulative amount remain
                    # quarterizable even when the later concept is concrete.
                    synthetic_target_baselines.append(zero_target.drop(
                        labels=['_QRank', '_Cumulative', '_FiledSort',
                                '_CalcSort', '_RankSort'], errors='ignore'))

                    zero_other_prior = anchor.copy()
                    zero_other_prior['Label'] = (
                        'Other Investing Activities')
                    zero_other_prior['Value'] = 0.0
                    zero_other_prior['Concept'] = (
                        broad_concept
                        or 'DerivedInvestmentFamilyMigrationOtherBaseline')
                    zero_other_prior['IsCalculated'] = True
                    zero_other_prior['TagRank'] = -1
                    zero_other_prior['SourceAliasVerified'] = True
                    zero_other_prior['SourceAliasRule'] = (
                        _INVESTMENT_MIGRATION_RULE)
                    zero_other_prior['SourceEquivalentConcept'] = (
                        _INVESTMENT_EQUIVALENT_PREFIX
                        + 'other_investing_activities')
                    zero_other_prior['SourceMetricFamily'] = (
                        'investing.other_investing_activities')
                    zero_other_prior['SourceMetricIdentity'] = (
                        'other_investing_activities')
                    zero_other_prior['SourceSemanticType'] = (
                        'Other Investing Activities')
                    zero_other_prior['SourceDerivation'] = (
                        'prior_filing_zero_baseline_for_migrated_other_'
                        'family')
                    zero_other_prior['SourcePeriodRole'] = (
                        'derived_reclassification')
                    zero_other_prior['SourceCanonicalizedFrom'] = (
                        _INVESTMENT_MIGRATION_RULE
                        + ':zero_other_prior_period')
                    if broad_concept:
                        zero_other_prior['SourceAliasVerified'] = False
                        zero_other_prior['SourceAliasRule'] = np.nan
                        zero_other_prior['SourceEquivalentConcept'] = np.nan
                    synthetic_prior_other_baselines.append(
                        zero_other_prior.drop(
                            labels=['_QRank', '_Cumulative', '_FiledSort',
                                    '_CalcSort', '_RankSort'],
                            errors='ignore'))

        pieces = [out, zeros]
        if synthetic_period_zeros:
            pieces.append(pd.DataFrame(synthetic_period_zeros))
        if synthetic_target_baselines:
            pieces.append(pd.DataFrame(synthetic_target_baselines))
        if synthetic_prior_other_baselines:
            pieces.append(pd.DataFrame(synthetic_prior_other_baselines))
        out = pd.concat(pieces, ignore_index=True, sort=False)
        migrated.append(f'FY{fiscal_year}:{target}')

    if migrated:
        print('  [Investing Migration] Reclassified broad Other baseline(s): '
              + ', '.join(migrated))
    return out



def _repair_late_new_investment_family_baselines(df):
    """Add a zero YTD9 baseline for a proven annual-only granular family.

    A filer may introduce a granular investing line in the 10-K after reporting
    zero activity through nine months.  Without a YTD9 zero, the quarterizer
    cannot assign the annual amount to Q4 and leaves it in the bridge residual.
    This repair is deliberately narrow: it applies only to strong face-verified
    granular families first appearing in Q4, requires an extracted Q3 investing
    statement, and requires the broad Other line to continue from Q3 to Q4 with
    only an immaterial movement.  A material broad-line reset is handled by the
    separate presentation-migration repair and is not treated as zero history.
    """
    required = {'Category', 'Label', 'Value', 'FY', 'Q', 'Duration'}
    if df is None or df.empty or not required.issubset(df.columns):
        return df
    out = df.copy()
    cash = out['Category'].eq('3_Cash_Flow')
    if not cash.any():
        return out

    qrank = {'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4}

    def _cumulative(frame):
        durations = pd.to_numeric(frame['Duration'], errors='coerce')
        quarters = frame['Q'].astype(str)
        return (
            quarters.eq('Q1') & durations.between(45, 125)
            | quarters.eq('Q2') & durations.between(140, 230)
            | quarters.eq('Q3') & durations.between(220, 320)
            | quarters.eq('Q4') & durations.between(300, 400)
        )

    def _best(rows):
        if rows.empty:
            return None
        work = rows.copy()
        work['_FiledSort'] = pd.to_datetime(
            work.get('Filed', pd.Series(pd.NaT, index=work.index)),
            errors='coerce')
        work['_CalcSort'] = work.get(
            'IsCalculated', pd.Series(False, index=work.index)
        ).fillna(False).astype(bool)
        work['_TagSort'] = pd.to_numeric(
            work.get('TagRank', pd.Series(999, index=work.index)),
            errors='coerce').fillna(999)
        return work.sort_values(
            ['_FiledSort', '_CalcSort', '_TagSort'],
            ascending=[False, True, True]).iloc[0]

    additions = []
    repaired = []
    fiscal_years = pd.to_numeric(
        out.loc[cash, 'FY'], errors='coerce').dropna().astype(int).unique()
    for fiscal_year in sorted(fiscal_years):
        year_mask = (
            cash & pd.to_numeric(out['FY'], errors='coerce').eq(fiscal_year))
        year = out.loc[year_mask].copy()
        if year.empty:
            continue
        year['_QRank'] = year['Q'].astype(str).map(qrank).fillna(0).astype(int)
        year['_Cumulative'] = _cumulative(year)

        q3_total = _best(year[
            year['Label'].eq('Investing Cash Flow')
            & year['_Cumulative'] & year['_QRank'].eq(3)])
        if q3_total is None:
            continue
        other_q3 = _best(year[
            year['Label'].eq('Other Investing Activities')
            & year['_Cumulative'] & year['_QRank'].eq(3)])
        other_q4 = _best(year[
            year['Label'].eq('Other Investing Activities')
            & year['_Cumulative'] & year['_QRank'].eq(4)])
        if other_q4 is None:
            continue
        other_q3_missing = other_q3 is None
        other_prior = (
            0.0 if other_q3_missing else pd.to_numeric(
                pd.Series([other_q3.get('Value')]),
                errors='coerce').iloc[0])
        other_annual = pd.to_numeric(
            pd.Series([other_q4.get('Value')]), errors='coerce').iloc[0]
        if pd.isna(other_prior) or pd.isna(other_annual):
            continue
        other_delta = float(other_annual) - float(other_prior)
        other_zero_added = False

        for target in sorted(_INVESTMENT_LATE_BASELINE_LABELS):
            # Missing prior broad Other is accepted only for the explicitly
            # signed business-combination family.  For purchase/proceeds
            # families, the Q3-to-annual broad continuity must be observable.
            if other_q3_missing and target != _BUSINESS_COMBINATIONS_NET_LABEL:
                continue
            target_rows = year[
                year['Label'].eq(target) & year['_Cumulative']].copy()
            if target_rows.empty:
                continue
            target_rows['_QRank'] = target_rows['Q'].astype(str).map(
                qrank).fillna(0).astype(int)
            if int(target_rows['_QRank'].min()) != 4:
                continue
            annual_rows = target_rows[target_rows['_QRank'].eq(4)]
            annual = _best(annual_rows)
            if annual is None:
                continue
            # Only a strong filer face identity can prove the annual family.
            if (not bool(annual.get('SourceAliasVerified', False))
                    or str(annual.get('SourceAliasRule') or '').strip()
                    != _INVESTMENT_FACE_ALIAS_RULE):
                continue
            source_label = str(annual.get('SourceLabel') or '').strip()
            if _classify_investment_face_label(source_label) != target:
                continue
            annual_value = pd.to_numeric(
                pd.Series([annual.get('Value')]), errors='coerce').iloc[0]
            if pd.isna(annual_value) or abs(float(annual_value)) <= 1.0:
                continue
            scale = abs(float(annual_value))
            tolerance = max(1_000_000.0, scale * 0.25)
            if abs(other_delta) > tolerance:
                continue
            # If the prior broad line is itself approximately the annual family,
            # this is a presentation transfer, not zero prior activity.
            if abs(abs(float(other_prior)) - scale) <= max(
                    1_000_000.0, scale * 0.10):
                continue

            identity = re.sub(
                r'[^a-z0-9]+', '_', target.casefold()).strip('_')
            zero = q3_total.copy()
            zero['Label'] = target
            zero['Value'] = 0.0
            zero['Concept'] = 'DerivedLateInvestmentFamilyZeroBaseline'
            zero['IsCalculated'] = True
            zero['TagRank'] = -1
            zero['SourceAliasVerified'] = True
            zero['SourceAliasRule'] = _INVESTMENT_MIGRATION_RULE
            zero['SourceEquivalentConcept'] = (
                _INVESTMENT_EQUIVALENT_PREFIX + identity)
            zero['SourceMetricFamily'] = 'investing.' + identity
            zero['SourceMetricIdentity'] = identity
            zero['SourceSemanticType'] = target
            zero['SourceDerivation'] = (
                'annual_only_granular_family_zero_ytd9_baseline')
            zero['SourcePeriodRole'] = 'derived_reclassification'
            zero['SourceCanonicalizedFrom'] = (
                _INVESTMENT_MIGRATION_RULE + ':late_family_zero_ytd9')
            additions.append(zero.drop(
                labels=['_QRank', '_Cumulative', '_FiledSort',
                        '_CalcSort', '_TagSort'], errors='ignore'))

            if (other_q3_missing
                    and target == _BUSINESS_COMBINATIONS_NET_LABEL
                    and not other_zero_added):
                zero_other = q3_total.copy()
                zero_other['Label'] = 'Other Investing Activities'
                zero_other['Value'] = 0.0
                zero_other['Concept'] = (
                    'DerivedLateInvestmentFamilyOtherZeroBaseline')
                zero_other['IsCalculated'] = True
                zero_other['TagRank'] = -1
                zero_other['SourceAliasVerified'] = True
                zero_other['SourceAliasRule'] = (
                    _INVESTMENT_MIGRATION_RULE)
                zero_other['SourceEquivalentConcept'] = (
                    _INVESTMENT_EQUIVALENT_PREFIX
                    + 'other_investing_activities')
                zero_other['SourceMetricFamily'] = (
                    'investing.other_investing_activities')
                zero_other['SourceMetricIdentity'] = (
                    'other_investing_activities')
                zero_other['SourceSemanticType'] = (
                    'Other Investing Activities')
                zero_other['SourceDerivation'] = (
                    'annual_other_line_zero_ytd9_baseline_for_'
                    'business_combination_split')
                zero_other['SourcePeriodRole'] = (
                    'derived_reclassification')
                zero_other['SourceCanonicalizedFrom'] = (
                    _INVESTMENT_MIGRATION_RULE
                    + ':late_other_zero_ytd9')
                additions.append(zero_other.drop(
                    labels=['_QRank', '_Cumulative', '_FiledSort',
                            '_CalcSort', '_TagSort'], errors='ignore'))
                other_zero_added = True

            repaired.append(f'FY{fiscal_year}:{target}')

    if additions:
        out = pd.concat([out, pd.DataFrame(additions)],
                        ignore_index=True, sort=False)
        print('  [Investing Baseline] Added verified zero YTD9 baseline(s): '
              + ', '.join(repaired))
    return out

def _compact_equity_issuance_text(*parts):
    return re.sub(r'[^a-z0-9]+', '', ' '.join(
        str(part or '') for part in parts).casefold())


def _classify_equity_issuance_line(concept, presentation_label=None):
    """Classify cash proceeds from issuing equity, conservatively.

    The classifier deliberately requires cash/proceeds language.  It therefore
    rejects similarly named share-count facts (``...SharesNewIssues``), APIC
    rollforward values, stock compensation, repurchases, and debt issuance.
    It is used for custom extension concepts on the financing statement.
    """
    text = _compact_equity_issuance_text(concept, presentation_label)
    if not text:
        return None
    has_cash_proceeds = any(token in text for token in (
        'proceedsfrom', 'netproceeds', 'cashproceeds', 'cashreceivedfrom'))
    has_issuance = any(token in text for token in (
        'issuance', 'issued', 'issueof', 'saleof', 'offering'))
    has_equity = any(token in text for token in (
        'commonstock', 'preferredstock', 'preferencestock', 'capitalstock',
        'equity', 'shares'))
    if not (has_cash_proceeds and has_issuance and has_equity):
        return None

    # These are distinct financing activities and must not be swept into the
    # stock-issuance parent merely because they contain words such as
    # "convertible", "capital", or "shares".
    if any(token in text for token in (
            'repurchase', 'buyback', 'redemption', 'treasurystock',
            'debt', 'notes', 'bonds', 'borrowings', 'commercialpaper',
            'loan', 'warrant', 'noncontrollinginterest')):
        # Convertible *preferred stock* is equity, while convertible debt is not.
        if 'preferredstock' not in text and 'preferencestock' not in text:
            return None
    if any(token in text for token in (
            'stockoption', 'employee', 'sharebased', 'stockbased',
            'incentiveplan', 'purchaseplan', 'compensationplan', 'espp')):
        return None

    is_preferred = ('preferredstock' in text or 'preferencestock' in text)
    is_common = 'commonstock' in text
    is_mandatory_convertible = (is_preferred and 'mandatory' in text
                                and 'convertible' in text)
    if is_mandatory_convertible:
        return 'Shares Issued - Mandatory Convertible Preferred Stock'
    if is_common and is_preferred:
        return 'Shares Issued - Combined Common and Preferred Stock'
    if is_preferred:
        return 'Shares Issued - Preferred Stock'
    if is_common:
        return 'Shares Issued - Common Stock'
    return 'Shares Issued - Other Equity'


def _debt_cash_flow_calc_sections(concept, max_hops=7):
    """Return cash-flow sections reached by one concept's calc ancestry.

    A concept can appear in several calculation trees.  Debt classification is
    safe only when it does not reach operating/investing roots; persistent
    learned aliases require an unambiguous financing root.
    """
    start = str(concept or '').split(':')[-1]
    if not start:
        return frozenset()
    roots = {
        'operating': _CF_OPERATING_PARENTS,
        'investing': _CF_INVESTING_PARENTS,
        'financing': _CF_FINANCING_PARENTS,
    }
    found = {name for name, values in roots.items() if start in values}
    frontier = {start}
    seen = set()
    for _ in range(max_hops):
        nxt = set()
        for child in frontier:
            if child in seen:
                continue
            seen.add(child)
            for parent, _weight in GLOBAL_CALC_PARENT.get(child, ()):
                parent = str(parent or '').split(':')[-1]
                for name, values in roots.items():
                    if parent in values:
                        found.add(name)
                if parent and parent not in seen:
                    nxt.add(parent)
        if not nxt:
            break
        frontier = nxt
    return frozenset(found)


def _debt_cash_flow_calc_section(concept):
    sections = _debt_cash_flow_calc_sections(concept)
    if len(sections) == 1:
        return next(iter(sections))
    if len(sections) > 1:
        return 'conflict'
    return None


def _is_investment_asset_cash_flow_concept(concept, presentation_label=None):
    """Reject asset-security purchases/sales from liability-debt metrics."""
    local = str(concept or '').split(':')[-1]
    text = re.sub(r'[^a-z0-9]+', '', ' '.join(
        str(part or '') for part in (local, presentation_label)).casefold())
    if not text:
        return False
    if (local in _INVESTMENT_CASH_FLOW_CONCEPTS
            or local in _PRODUCTIVE_ASSET_AMBIGUOUS_CONCEPTS
            or local in _GENUINE_PRODUCTIVE_ASSET_SALE_CONCEPTS):
        return True
    security_asset = any(token in text for token in (
        'marketablesecurit', 'marketabledebtsecurit', 'availableforsale', 'heldtomaturity',
        'investmentsecurit', 'nonmarketablesecurit',
        'shortterminvestment', 'longterminvestment'))
    asset_transaction = any(token in text for token in (
        'saleandmaturity', 'salesandmaturit', 'saleofsecurit',
        'maturitiesofsecurit', 'maturityofsecurit',
        'paymentstoacquire', 'purchasesof', 'purchaseof',
        'proceedsfromsale', 'proceedsfrommaturit'))
    receivable_asset = any(token in text for token in (
        'notesreceivable', 'loansreceivable', 'creditreceivable'))
    return bool((security_asset and asset_transaction) or receivable_asset)


def _is_normalized_debt_cash_flow_label(label):
    return str(label) in {
        'Reported Short-term Debt Issued', 'Reported Short-term Debt Repaid',
        'Commercial Paper Issued', 'Commercial Paper Repaid',
        'Other Short-term Borrowings Issued',
        'Other Short-term Borrowings Repaid',
        'Lines of Credit Issued', 'Lines of Credit Repaid',
        'Short-term Debt Issued', 'Short-term Debt Repaid',
        'Net Change in Short-term Debt',
        'Net Short-Term Debt Issued (Repaid)',
        'Reported Long-term Debt Issued', 'Reported Long-term Debt Repaid',
        'Senior Notes and Bonds Issued', 'Senior Notes and Bonds Repaid',
        'Term Loans Issued', 'Term Loans Repaid',
        'Convertible Debt Issued', 'Convertible Debt Repaid',
        'Acquisition / Seller Notes Issued',
        'Acquisition / Seller Notes Repaid',
        'Finance Lease Principal Repaid',
        'Other Long-term Debt Issued', 'Other Long-term Debt Repaid',
        'Long-term Debt Issued', 'Long-term Debt Repaid',
        'Net Long-Term Debt Issued (Repaid)',
        'Total Debt Issued', 'Total Debt Repaid',
        'Total Net Debt Issued (Repaid)',
    }


def _classify_debt_cash_flow_line(concept, presentation_label=None,
                                  source_section=None):
    """Classify custom liability-debt cash flows by instrument family."""
    text = re.sub(r'[^a-z0-9]+', '', ' '.join(
        str(part or '') for part in (concept, presentation_label)).casefold())
    if not text:
        return None
    if source_section is None:
        source_section = _debt_cash_flow_calc_section(concept)
    if source_section in {'operating', 'investing', 'conflict'}:
        return None
    if _is_investment_asset_cash_flow_concept(concept, presentation_label):
        return None

    has_debt = any(token in text for token in (
        'debt', 'borrowing', 'loan', 'note', 'bond', 'commercialpaper',
        'lineofcredit', 'creditfacility', 'revolvingcredit', 'termfacility',
        'financelease', 'capitallease'))
    if not has_debt:
        return None
    if any(token in text for token in (
            'noncash', 'interest', 'amortization', 'accretion',
            'extinguishmentgain', 'extinguishmentloss', 'modificationgain',
            'modificationloss', 'carryingamount', 'fairvalue',
            'principalamountoutstanding', 'debtoutstanding', 'balance',
            'maturityschedule', 'maturitiesschedule', 'weightedaverage',
            'covenant', 'commitmentfee', 'unusedcommitment')):
        return None

    combined_direction = (
        ('proceedsfromrepayment' in text
         or ('proceeds' in text and 'repayment' in text))
        and any(token in text for token in (
            'shortterm', 'commercialpaper', 'lineofcredit',
            'creditfacility', 'revolvingcredit')))
    if combined_direction:
        return 'Net Change in Short-term Debt'

    issued = any(token in text for token in (
        'proceedsfrom', 'netproceedsfrom', 'cashproceedsfrom',
        'borrowingsunder', 'issuanceof', 'issueddebt', 'debtissued'))
    repaid = any(token in text for token in (
        'repayment', 'repayments', 'principalpayment', 'principalrepayment',
        'paymentsofprincipal', 'redemptionof', 'retirementofdebt',
        'debtprepayment', 'prepaymentofdebt'))
    if issued == repaid:
        return None
    suffix = 'Issued' if issued else 'Repaid'

    if 'financelease' in text or 'capitallease' in text:
        # Lease inception is normally noncash; only cash principal repayment is
        # included in debt cash-flow totals.
        return None if issued else 'Finance Lease Principal Repaid'
    if any(token in text for token in (
            'commercialpaper', 'shorttermnote', 'shorttermborrowing')):
        return f'Commercial Paper {suffix}' if 'commercialpaper' in text             else f'Other Short-term Borrowings {suffix}'
    if any(token in text for token in (
            'lineofcredit', 'creditfacility', 'revolvingcredit')):
        return f'Lines of Credit {suffix}'
    if any(token in text for token in (
            'careem', 'acquisitionnote', 'sellernote', 'vendornote',
            'purchasemoneynote', 'promissorynote')):
        return f'Acquisition / Seller Notes {suffix}'
    if 'convertible' in text:
        return f'Convertible Debt {suffix}'
    if any(token in text for token in (
            'termloan', 'termfacility', 'securedterm', 'unsecuredterm')):
        return f'Term Loans {suffix}'
    if any(token in text for token in (
            'seniornote', 'seniorlongtermdebt', 'mediumtermnote',
            'subordinatednote', 'debenture', 'bond')):
        return f'Senior Notes and Bonds {suffix}'
    if 'shortterm' in text:
        return f'Other Short-term Borrowings {suffix}'
    if any(token in text for token in (
            'longterm', 'secureddebt', 'unsecureddebt',
            'subordinateddebt')):
        return f'Other Long-term Debt {suffix}'
    # A generic debt concept is an aggregate, not an instrument component.
    return f'Total Debt {suffix}'


def _register_debt_cash_flow_alias(concept, target_label,
                                   require_financing=False):
    """Register an alias only when it cannot overwrite another metric family."""
    if not concept or not _is_normalized_debt_cash_flow_label(target_label):
        return False
    section = _debt_cash_flow_calc_section(concept)
    if section in {'operating', 'investing', 'conflict'}:
        return False
    if require_financing and section != 'financing':
        return False
    if _is_investment_asset_cash_flow_concept(concept):
        return False

    mapped_labels = {
        label for label, mapped in CONCEPT_MAP.items()
        if isinstance(mapped, dict) and concept in (mapped.get('tags') or ())
    }
    existing = _CONCEPT_TAG_TO_LABEL.get(concept)
    if existing:
        mapped_labels.add(existing)
    # A learned alias may fill an unmapped extension, but it must never change
    # an existing exact concept's normalized meaning—even to another debt row.
    if existing and existing != target_label:
        return False
    if any(label != target_label for label in mapped_labels):
        return False

    info = CONCEPT_MAP.get(target_label)
    if not isinstance(info, dict):
        return False
    tags = info.setdefault('tags', [])
    if concept not in tags:
        tags.append(concept)
    _CONCEPT_TAG_TO_LABEL[concept] = target_label
    _FUZZY_CACHE[concept] = target_label
    return True


def _fact_has_share_count_unit(row):
    """Return True only when available unit metadata explicitly says shares.

    edgartools versions have used several unit-column names.  Unknown/missing
    metadata is allowed so older environments retain their previous behavior;
    an explicit share or per-share unit is rejected from cash-proceeds rows.
    """
    for key in ('unit', 'units', 'unit_ref', 'unitRef', 'unit_id',
                'unit_measure', 'unitMeasure'):
        try:
            value = row.get(key, None)
        except Exception:
            value = None
        if value is None:
            continue
        try:
            if pd.isna(value):
                continue
        except Exception:
            pass
        unit_text = str(value).casefold()
        if 'share' in unit_text or 'stock' in unit_text:
            return True
    return False


def _register_equity_issuance_alias(concept, target_label):
    """Register a strict financing-face extension concept as an exact alias."""
    if not concept or target_label not in _EQUITY_ISSUANCE_CASH_LABELS:
        return False
    info = CONCEPT_MAP.get(target_label)
    if not isinstance(info, dict):
        return False
    tags = info.setdefault('tags', [])
    if concept not in tags:
        tags.append(concept)
    _CONCEPT_TAG_TO_LABEL[concept] = target_label
    _FUZZY_CACHE[concept] = target_label
    return True


def _classify_cf_label_fallback(label, section):
    """
    Semantic fallback when the calculation linkbase has no arc for a learned
    CF concept (common for custom tags). Returns a weight or None. Cash-paid
    and noncash supplemental disclosures are never bridge components.
    """
    ll = str(label).lower()
    if any(m in ll for m in _CF_SUPPLEMENTAL_MARKERS) and 'repaid' not in ll:
        return None
    if section == 'fin':
        if any(k in ll for k in ('repayment', 'repurchase', 'buyback',
                                 'tax receivable agreement', 'tax withholding',
                                 'redemption', 'debt restructuring cost',
                                 'dividends')):
            return -1.0
        if any(k in ll for k in ('proceeds from issuance', 'treasury stock',
                                 'proceeds from stock', 'borrowings under',
                                 'collateral held under securities lending',
                                 'excess tax benefit')):
            return 1.0
    elif section == 'inv':
        is_invest = any(k in ll for k in ('investment', 'securities', 'acquisition',
                                          'business combination', 'intangible',
                                          'credit card receivable', 'loans receivable'))
        if is_invest and any(k in ll for k in ('purchase', 'payments to acquire',
                                               'net of cash acquired', 'loans originated')):
            return -1.0
        if is_invest and any(k in ll for k in ('sale', 'maturit', 'distribution',
                                               'proceeds', 'redemption')):
            return 1.0
        if 'capital expenditure' in ll:
            return -1.0
    elif section == 'op':
        if any(k in ll for k in ('collateral', 'securities lending', 'restricted cash')):
            return None
        if ('increase decrease in' in ll or ll.startswith('change in')
                or 'changes in' in ll or ll.startswith('increase (decrease)')
                or ll.startswith('decrease (increase)')):
            # liabilities first: 'securities loaned' is a liability even
            # though 'securities' alone reads as an asset
            if any(k in ll for k in ('payable', 'loaned', 'borrowed', 'accrued',
                                     'deposits received', 'owed to')):
                return 1.0
            is_asset = any(k in ll for k in ('receivable', 'asset', 'inventor',
                                             'prepaid', 'deposit', 'securities',
                                             'financial instruments', 'segregated',
                                             'owned', 'restricted'))
            return -1.0 if is_asset else 1.0
        if any(k in ll for k in ('amortization', 'depreciation', 'impairment',
                                 'provision', 'write-off', 'write off')):
            return 1.0
    return None


def _bridge_sign_self_check(total_n, sum_s, contribs, section_name):
    """
    A component summed with the wrong polarity leaves a residual of exactly
    -2x its value in every period. Test flipping each component's sign; adopt
    a flip only when it collapses the median residual by >60%. Catches both
    bad fallback heuristics and miswired calculation weights, self-healing
    per company instead of relying on label keywords.
    """
    mask = total_n.notna()
    if not mask.any() or not contribs:
        return sum_s
    flips = 0
    while flips < 3:
        resid = total_n.fillna(0) - sum_s
        best_lbl, best_score = None, 0.0
        for lbl, contrib in contribs.items():
            # quarters where this component is material
            material = mask & (contrib.abs() > np.maximum(0.05 * total_n.abs().fillna(0), 1e7))
            n_mat = int(material.sum())
            if n_mat < 3:
                continue
            # wrong-polarity signature: residual == -2x the contribution
            # wherever the component is material. Magnitude-weighted so the
            # quarters that matter dominate the verdict and baseline noise
            # in small quarters cannot veto an obvious correction.
            hit = (resid[material] + 2 * contrib[material]).abs() < 0.25 * (2 * contrib[material].abs())
            w_mat = float(contrib[material].abs().sum())
            w_hit = float(contrib[material].abs()[hit].sum())
            if w_mat > 0 and (w_hit / w_mat) >= 0.8:
                if w_mat > best_score:
                    best_lbl, best_score = lbl, w_mat
        if best_lbl is None:
            break
        sum_s = sum_s - 2 * contribs[best_lbl]
        contribs[best_lbl] = -contribs[best_lbl]
        print(f"  [Bridge] Sign-corrected '{best_lbl}' in the {section_name} bridge "
              f"(residual matched -2x its value in material quarters).")
        flips += 1

    # Stage 2 -- hill climb for multiple simultaneous polarity errors
    # (broker reconciliations): when several components are wrong at once,
    # no single flip matches the -2x signature. Greedily adopt the flip
    # that most reduces total |residual|, and revert everything unless the
    # final residual is at least 60% smaller than where stage 2 started.
    resid = total_n.fillna(0) - sum_s
    start_abs = float(resid[mask].abs().sum())
    tot_abs = float(total_n[mask].abs().sum())
    if start_abs > 0.10 * max(tot_abs, 1e9):
        cur_sum = sum_s.copy()
        cur_abs = start_abs
        flipped = []
        for _ in range(5):
            best_lbl2, best_abs2 = None, cur_abs
            cur_resid = total_n.fillna(0) - cur_sum
            for lbl, contrib in contribs.items():
                test = float((cur_resid + 2 * contrib)[mask].abs().sum())
                if test < 0.80 * cur_abs and test < best_abs2:
                    best_lbl2, best_abs2 = lbl, test
            if best_lbl2 is None:
                break
            cur_sum = cur_sum - 2 * contribs[best_lbl2]
            contribs[best_lbl2] = -contribs[best_lbl2]
            flipped.append(best_lbl2)
            cur_abs = best_abs2
        if flipped and cur_abs < 0.40 * start_abs:
            for lbl in flipped:
                print(f"  [Bridge] Sign-corrected '{lbl}' in the {section_name} bridge "
                      f"(multi-component polarity solve).")
            return cur_sum
        # revert contribs mutations from the failed climb
        for lbl in flipped:
            contribs[lbl] = -contribs[lbl]
    return sum_s


def _classify_calc_lineage(concepts, counted_concepts, targets, blockers, max_hops=4):
    """
    Walk the SEC calculation linkbase upward from any of `concepts`,
    carrying the product of arc weights.  Returns:
      ('target', weight)  -- first mapped ancestor is in `targets`
      ('counted', w) / ('blocked', w) -- hit an already-counted concept or a
                                          blocker root first (do not add)
      (None, 0.0)         -- no classification possible
    Used to wire dynamically learned face lines into the bridge math so
    'Other Adjustments' plugs stay true residuals.
    """
    frontier = {(c, 1.0) for c in (concepts or []) if c}
    seen = set()
    for _ in range(max_hops):
        nxt = set()
        for c, w in sorted(frontier, key=lambda item: (str(item[0]), float(item[1]))):
            if c in seen:
                continue
            seen.add(c)
            for p, pw in sorted(
                    GLOBAL_CALC_PARENT.get(c, ()),
                    key=lambda item: (str(item[0]), str(item[1]))):
                try:
                    eff = w * (float(pw) if pw is not None else 1.0)
                except (TypeError, ValueError):
                    eff = w
                if p in targets:
                    return ('target', eff)
                if p in blockers:
                    return ('blocked', eff)
                if p in counted_concepts:
                    return ('counted', eff)
                nxt.add((p, eff))
        frontier = nxt
        if not frontier:
            break
    return (None, 0.0)

import threading
import concurrent.futures
from collections import deque
import itertools


class PipelineProgress:
    """One end-to-end progress bar for the complete extraction pipeline.

    The old implementation measured only completed SEC filing futures, so it
    could report 100% while statement assembly, reconciliation, KPI creation,
    cleanup, and output writing were still running.  This tracker reserves
    progress ranges for those downstream stages and can also be updated from
    the isolated foreign-filer pipeline.
    """

    def __init__(self, enabled=True, description="SEC extraction"):
        self.enabled = bool(enabled)
        self.current = 0.0
        self._bar = None
        self._last_stage = ""
        self._ticker, initial_stage = self._split_description(description)
        self._stage_plain = self._stage_text(initial_stage)
        self._last_desc = ""
        self._stream = sys.stdout
        self._color = _stream_supports_color(self._stream)
        self._spinner_frames = self._spinner_frames_for_stream(self._stream)
        self._spinner_index = 0
        self._outline_width = _terminal_ui_width(self._stream)
        self._box_chars = _box_chars_for_stream(self._stream)
        self._attached_outline = False
        self._bottom_bar = None
        self._tqdm_cls = None
        self._result_footer = None
        self._stats_done = 0
        self._stats_total = 0
        self._stats_latest = self._stage_plain
        self._last_stats_text = ""
        self._warn_count = 0
        self._retry_count = 0
        self._fail_count = 0
        self._last_warn_text = ""
        self._spinner_stop = threading.Event()
        self._display_lock = threading.RLock()
        self._spinner_thread = None
        self._pulse_stop = threading.Event()
        self._pulse_thread = None
        if not self.enabled:
            return
        try:
            from tqdm.auto import tqdm
            self._tqdm_cls = tqdm
            left_border = (
                _ansi(self._box_chars["v"], "border")
                if self._color else self._box_chars["v"]
            )
            right_border = left_border
            bar_kwargs = dict(
                total=100.0,
                desc=self._decorated_stage(),
                file=self._stream,
                ascii=self._bar_charset_for_stream(self._stream),
                ncols=self._outline_width,
                dynamic_ncols=False,
                position=0,
                mininterval=0.5 if _PROGRESS_LIGHT_ENABLED else 0.15,
                smoothing=0.05,
                bar_format=(
                    f"{left_border} "
                    "{desc} {bar} {percentage:3.0f}% | {elapsed}"
                    f" {right_border}"
                ),
            )
            if self._color:
                bar_kwargs["colour"] = "white"
            try:
                self._bar = tqdm(**bar_kwargs)
            except TypeError:
                bar_kwargs.pop("colour", None)
                self._bar = tqdm(**bar_kwargs)
            self._last_desc = self._decorated_stage()
            if not _PROGRESS_LIGHT_ENABLED:
                self._spinner_thread = threading.Thread(
                    target=self._spin,
                    name="PipelineProgressSpinner",
                    daemon=True,
                )
                self._spinner_thread.start()
        except Exception:
            # Progress is a UI aid only; extraction must still work when tqdm
            # is unavailable or the output stream cannot render a dynamic bar.
            self.enabled = False
            self._bar = None

    @staticmethod
    def _spinner_frames_for_stream(stream):
        frames = (
            "\u280b", "\u2819", "\u2839", "\u2838", "\u283c",
            "\u2834", "\u2826", "\u2827", "\u2807", "\u280f",
        )
        encoding = getattr(stream, "encoding", None) or "utf-8"
        try:
            "".join(frames).encode(encoding)
            return frames
        except Exception:
            return ("|", "/", "-", "\\")

    @staticmethod
    def _bar_charset_for_stream(stream):
        charset = "\u00b7\u2501"
        encoding = getattr(stream, "encoding", None) or "utf-8"
        try:
            charset.encode(encoding)
            return charset
        except Exception:
            return True

    @staticmethod
    def _split_description(description):
        text = re.sub(r"\s+", " ", str(description or "")).strip()
        if ":" in text:
            prefix, rest = text.split(":", 1)
            prefix = prefix.strip()
            if prefix and len(prefix) <= 12:
                return prefix.upper(), rest.strip() or "starting"
        return "", text or "starting"

    @staticmethod
    def _stage_text(stage):
        text = re.sub(r"\s+", " ", str(stage or "")).strip()
        return text[:39] + "..." if len(text) > 42 else text

    @staticmethod
    def _phase_text(value):
        try:
            pct = float(value)
        except Exception:
            pct = 0.0
        if pct < 8.0:
            return "Phase 1/4 Setup"
        if pct < 70.0:
            return "Phase 2/4 SEC retrieval"
        if pct < 98.0:
            return "Phase 3/4 Build/reconcile"
        return "Phase 4/4 Write"

    def _decorated_stage(self, value=None):
        prefix = f"{self._ticker} | " if self._ticker else ""
        phase = self._phase_text(self.current if value is None else value)
        spinner = self._spinner_frames[self._spinner_index]
        body = f"{prefix}{phase} | {self._stage_plain}"
        text = f"{spinner} {body}"
        if len(text) > 60:
            body = body[:max(0, 56)] + "..."
        if not self._color:
            return f"{spinner} {body}"
        return f"{_ansi(spinner, 'orange')}{_ansi(' ' + body, 'bright')}"

    def attach_outline(self):
        """Attach the live progress row to the run-card outline."""
        with self._display_lock:
            self._attached_outline = self._bar is not None
            self._last_warn_text = self.warn_text()
            self._last_stats_text = self.stats_text()
            if (
                not self._attached_outline
                or self._bottom_bar is not None
                or self._tqdm_cls is None
            ):
                return
            bottom = _format_box_bottom(self._stream, self._outline_width)
            self._bottom_bar = self._tqdm_cls(
                total=1,
                desc=bottom,
                file=self._stream,
                ncols=self._outline_width,
                dynamic_ncols=False,
                position=1,
                leave=True,
                bar_format="{desc}",
            )
            self._bar.refresh()

    def set_result_footer(self, text):
        self._result_footer = str(text or "").strip() or None

    def sync_terminal_width(self):
        with self._display_lock:
            if self._attached_outline:
                return self._outline_width
            self._outline_width = _terminal_ui_width(self._stream)
            if self._bar is not None:
                self._bar.ncols = self._outline_width
            return self._outline_width

    def set_stats(self, done=None, total=None, latest=None):
        if done is not None:
            try:
                self._stats_done = max(0, int(done))
            except Exception:
                pass
        if total is not None:
            try:
                self._stats_total = max(0, int(total))
            except Exception:
                pass
        if latest:
            self._stats_latest = _clean_log_text(latest)
        return self.stats_text()

    def note_log(self, *args, **kwargs):
        sep = kwargs.pop("sep", " ")
        kwargs.pop("end", "\n")
        kwargs.pop("file", None)
        kwargs.pop("flush", False)
        text = sep.join(str(a) for a in args)
        text = _clean_log_text(text)
        if not text:
            return
        with self._display_lock:
            self._stats_latest = text
            self._update_warn_counts_from_log(text)
            self._rewrite_warn_row_if_changed()
            self._rewrite_stats_row_if_changed()

    def warn_text(self):
        return _format_warn_text(
            self._warn_count,
            self._retry_count,
            self._fail_count,
        )

    def stats_text(self):
        return _format_stats_text(
            self._stats_done,
            self._stats_total,
            self._stats_latest,
        )

    def _spin(self):
        while not self._spinner_stop.wait(0.12):
            with self._display_lock:
                if self._bar is None:
                    return
                self._spinner_index = (
                    self._spinner_index + 1
                ) % len(self._spinner_frames)
                desc = self._decorated_stage()
                self._bar.set_description_str(desc, refresh=True)
                self._last_desc = desc

    def start_pulse(self, end, stage=None, expected_seconds=45.0):
        """Smoothly advance inside a long synchronous stage.

        Heavy pandas/accounting passes do not report internal progress.  This
        keeps the UI honest enough for humans: it moves quickly at first, then
        slows and leaves a small reserve until the stage explicitly completes.
        """
        if self._bar is None:
            return
        self.stop_pulse()
        self.set(self.current, stage)
        try:
            end = max(self.current, min(100.0, float(end)))
            expected_seconds = max(1.0, float(expected_seconds))
        except Exception:
            return
        if end <= self.current:
            return
        self._pulse_stop = threading.Event()

        def _pulse():
            start = self.current
            span = end - start
            started = time.monotonic()
            while not self._pulse_stop.wait(0.45):
                elapsed = time.monotonic() - started
                # Asymptotic curve: never consumes the final 4% of this stage.
                frac = min(0.96, elapsed / (expected_seconds + elapsed))
                target = start + span * frac
                if target > self.current:
                    self.set(target)

        self._pulse_thread = threading.Thread(
            target=_pulse,
            name="PipelineProgressPulse",
            daemon=True,
        )
        self._pulse_thread.start()

    def stop_pulse(self):
        pulse = self._pulse_thread
        if pulse is None:
            return
        self._pulse_stop.set()
        if pulse is not threading.current_thread():
            pulse.join(timeout=0.8)
        self._pulse_thread = None

    def set(self, value, stage=None):
        """Advance monotonically to an absolute percentage."""
        if self._bar is None:
            return
        with self._display_lock:
            target = max(self.current, min(100.0, float(value)))
            if stage:
                stage_text = self._stage_text(stage)
                if stage_text != self._last_stage:
                    self._stage_plain = stage_text
                    self._last_stage = stage_text
                self._update_stats_from_stage(stage_text)
            desc = self._decorated_stage(target)
            if desc != self._last_desc:
                self._bar.set_description_str(desc, refresh=False)
                self._last_desc = desc
            delta = target - self.current
            if delta > 0:
                self._bar.update(delta)
                self.current = target
            else:
                self._bar.refresh()
            self._rewrite_stats_row_if_changed()

    def write(self, *args, **kwargs):
        text = kwargs.pop("sep", " ").join(str(a) for a in args)
        end = kwargs.pop("end", "\n")
        file = kwargs.pop("file", None)
        flush = kwargs.pop("flush", False)
        if kwargs:
            text = f"{text} {' '.join(f'{k}={v}' for k, v in kwargs.items())}"
        with self._display_lock:
            if self._bar is not None:
                self._bar.write(text, file=(file or self._stream), end=end)
            else:
                print(text, end=end, file=file, flush=flush)

    def finish(self, stage="Complete", footer=None):
        self.stop_pulse()
        self._spinner_stop.set()
        footer = footer or self._result_footer
        with self._display_lock:
            if self._bar is not None:
                self.set(100.0, stage)
                if footer and self._rewrite_status_row(footer):
                    footer = None
                self._bar.close()
                self._bar = None
            self._write_outline_bottom(footer)

    def close(self):
        """Close without falsely forcing the bar to 100% after an error."""
        self.stop_pulse()
        self._spinner_stop.set()
        with self._display_lock:
            if self._bar is not None:
                self._bar.close()
                self._bar = None
            self._write_outline_bottom()

    def _update_stats_from_stage(self, stage_text):
        text = str(stage_text or "").strip()
        match = re.search(r"(\d+)\s*/\s*(\d+)", text)
        if match:
            self._stats_done = int(match.group(1))
            self._stats_total = int(match.group(2))
        else:
            queued = re.search(r"Queued\s+(\d+)\s+SEC\s+filings", text, re.I)
            if queued:
                self._stats_done = 0
                self._stats_total = int(queued.group(1))

    def _update_warn_counts_from_log(self, text):
        lower = str(text or "").lower()
        if not lower:
            return
        if "retry" in lower or "rate-limited" in lower or "throttled" in lower:
            self._retry_count += 1
        if (
            "warning" in lower
            or "[warn]" in lower
            or " warn]" in lower
            or "throttled" in lower
            or "rate-limited" in lower
        ):
            self._warn_count += 1
        if (
            " failed" in lower
            or "[error]" in lower
            or " error]" in lower
            or "permanently failed" in lower
            or "could not recover" in lower
        ):
            self._fail_count += 1

    def _rewrite_card_row(self, label, value, rows_above_progress):
        if not self._attached_outline or not _stream_supports_cursor_control(self._stream):
            return False
        line = _format_card_row(
            label,
            value,
            stream=self._stream,
            width=self._outline_width,
        )
        self._stream.write(f"\r\033[{rows_above_progress}A{line}\033[{rows_above_progress}B\r")
        self._stream.flush()
        if self._bar is not None:
            self._bar.refresh()
        if self._bottom_bar is not None:
            self._bottom_bar.refresh()
        return True

    def _rewrite_status_row(self, footer):
        # Status is above Warn, Stats, and the progress separator.
        return self._rewrite_card_row(
            "Status",
            _saved_footer_text(footer, self._stream),
            4,
        )

    def _rewrite_warn_row_if_changed(self):
        text = self.warn_text()
        if text == self._last_warn_text:
            return
        if self._rewrite_card_row("Warn", text, 3):
            self._last_warn_text = text

    def _rewrite_stats_row_if_changed(self):
        text = self.stats_text()
        if text == self._last_stats_text:
            return
        if self._rewrite_card_row("Stats", text, 2):
            self._last_stats_text = text

    def _write_outline_bottom(self, footer=None):
        if not self._attached_outline:
            return
        footer = str(footer or "").strip()
        if self._bottom_bar is not None:
            if footer:
                self._bottom_bar.set_description_str(
                    _format_card_row("Status",
                                     _saved_footer_text(footer, self._stream),
                                     stream=self._stream,
                                     width=self._outline_width),
                    refresh=True,
                )
            else:
                self._bottom_bar.refresh()
            self._bottom_bar.close()
            self._bottom_bar = None
            if footer:
                self._stream.write(_format_box_bottom(self._stream, self._outline_width) + "\n")
                self._stream.flush()
            self._attached_outline = False
            return
        # tqdm can leave the cursor on the rendered progress row in some
        # terminals. Start a fresh line so the closing border is never eaten.
        if footer:
            self._stream.write(
                "\n"
                + _format_card_row("Status",
                                   _saved_footer_text(footer, self._stream),
                                   stream=self._stream,
                                   width=self._outline_width)
                + "\n"
                + _format_box_bottom(self._stream, self._outline_width)
                + "\n"
            )
        else:
            self._stream.write("\n" + _format_box_bottom(self._stream, self._outline_width) + "\n")
        self._stream.flush()
        self._attached_outline = False


def _stream_supports_text(stream, text):
    encoding = getattr(stream, "encoding", None) or "utf-8"
    try:
        str(text).encode(encoding)
        return True
    except Exception:
        return False


def _terminal_ui_width(stream=None, fallback=100):
    stream = stream or sys.stdout
    try:
        is_tty = stream.isatty()
    except Exception:
        is_tty = False
    if not is_tty:
        return int(fallback)
    try:
        columns = shutil.get_terminal_size((int(fallback), 24)).columns
    except Exception:
        columns = int(fallback)
    # Leave a tiny guard band so Windows terminals do not wrap the right border
    # when the cursor lands on the final column.
    target = max(48, int(columns) - 2)
    return target


_ANSI_STYLES = {
    "reset": "0",
    "dim": "2",
    "border": "90",
    "bright": "97",
    "title": "1;97",
    "orange": "38;5;215",
    "blue": "38;5;75",
    "cyan": "38;5;80",
    "purple": "38;5;141",
    "green": "38;5;114",
    "yellow": "38;5;221",
    "red": "38;5;203",
}


def _stream_supports_color(stream):
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("CLICOLOR_FORCE") not in (None, "", "0"):
        return True
    try:
        if not stream.isatty():
            return False
    except Exception:
        return False
    term = os.environ.get("TERM", "")
    if term.lower() == "dumb":
        return False
    if os.name != "nt":
        return bool(term)
    return bool(
        os.environ.get("WT_SESSION")
        or os.environ.get("ANSICON")
        or os.environ.get("ConEmuANSI", "").upper() == "ON"
        or os.environ.get("TERM_PROGRAM")
        or "xterm" in term.lower()
    )


def _stream_supports_cursor_control(stream):
    if os.environ.get("NO_COLOR"):
        return False
    try:
        if not stream.isatty():
            return False
    except Exception:
        return False
    term = os.environ.get("TERM", "")
    if term.lower() == "dumb":
        return False
    if os.name != "nt":
        return bool(term)
    return bool(
        os.environ.get("WT_SESSION")
        or os.environ.get("ANSICON")
        or os.environ.get("ConEmuANSI", "").upper() == "ON"
        or os.environ.get("TERM_PROGRAM")
        or "xterm" in term.lower()
    )


def _ansi(text, style, stream=None):
    if stream is not None and not _stream_supports_color(stream):
        return str(text)
    code = _ANSI_STYLES.get(style)
    if not code:
        return str(text)
    return f"\033[{code}m{text}\033[0m"


def _maybe_ansi(text, style, stream):
    return _ansi(text, style) if _stream_supports_color(stream) else str(text)


def _box_chars_for_stream(stream):
    if _stream_supports_text(stream, "\u256d\u2500\u256e\u2502\u251c\u2524\u2570\u256f"):
        return {
            "tl": "\u256d", "tr": "\u256e",
            "bl": "\u2570", "br": "\u256f",
            "h": "\u2500", "v": "\u2502",
            "lt": "\u251c", "rt": "\u2524",
        }
    return {
        "tl": "+", "tr": "+",
        "bl": "+", "br": "+",
        "h": "-", "v": "|",
        "lt": "+", "rt": "+",
    }


def _format_box_bottom(stream=None, width=100):
    stream = stream or sys.stdout
    chars = _box_chars_for_stream(stream or sys.stdout)
    width = max(48, int(width))
    line = chars["bl"] + chars["h"] * (width - 2) + chars["br"]
    return _maybe_ansi(line, "border", stream)


def _saved_footer_text(text, stream=None):
    text = str(text or "").strip()
    if not text:
        return ""
    if text.lower().startswith(("saved ", "saved to ", "no data")):
        return text
    return "Saved to " + text


def _format_box_row(text, stream=None, width=100, value_style=None):
    stream = stream or sys.stdout
    chars = _box_chars_for_stream(stream)
    width = max(48, int(width))
    inner = width - 4
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(text) > inner:
        text = text[:max(0, inner - 3)] + "..."
    padding = " " * max(0, inner - len(text))
    if not _stream_supports_color(stream):
        return f"{chars['v']} {text}{padding} {chars['v']}"
    value = _ansi(text, value_style) if value_style else text
    return (
        _ansi(chars["v"], "border")
        + " "
        + value
        + padding
        + " "
        + _ansi(chars["v"], "border")
    )


def _format_card_row(label, value, route=None, stream=None, width=100):
    stream = stream or sys.stdout
    chars = _box_chars_for_stream(stream)
    width = max(48, int(width))
    inner = width - 4
    label = str(label)
    value = str(value)
    content = f"{label:<7} {value}"
    if len(content) > inner:
        value = value[:max(0, inner - 11)] + "..."
        content = f"{label:<7} {value}"
    padding = " " * max(0, inner - len(content))
    if not _stream_supports_color(stream):
        return f"{chars['v']} {content:<{inner}} {chars['v']}"
    return (
        _ansi(chars["v"], "border")
        + " "
        + _ansi(f"{label:<7}", "dim")
        + " "
        + _color_card_value(label, value, route, stream)
        + padding
        + " "
        + _ansi(chars["v"], "border")
    )


def _format_stats_text(done, total, latest):
    try:
        done = max(0, int(done))
    except Exception:
        done = 0
    try:
        total = max(0, int(total))
    except Exception:
        total = 0
    latest = re.sub(r"\s+", " ", str(latest or "Starting")).strip()
    if total > 0:
        return f"{done}/{total} Filings | {latest}"
    return f"0/0 Filings | {latest}"


def _format_warn_text(warnings, retries, fails):
    try:
        warnings = max(0, int(warnings))
    except Exception:
        warnings = 0
    try:
        retries = max(0, int(retries))
    except Exception:
        retries = 0
    try:
        fails = max(0, int(fails))
    except Exception:
        fails = 0
    return f"{warnings} warnings | {retries} retries | {fails} fails"


def _format_cik_display(cik):
    text = re.sub(r"\s+", "", str(cik or ""))
    return text.zfill(10) if text.isdigit() else (text or "Unknown")


def _clean_log_text(text):
    text = re.sub(r"\s+", " ", str(text or "")).strip()
    return text


def _format_progress_separator(stream=None, width=100):
    stream = stream or sys.stdout
    chars = _box_chars_for_stream(stream)
    width = max(48, int(width))
    title = " Progress "
    fill = chars["h"] * max(0, width - len(title) - 3)
    if not _stream_supports_color(stream):
        return chars["lt"] + chars["h"] + title + fill + chars["rt"]
    return (
        _ansi(chars["lt"] + chars["h"], "border")
        + _ansi(title, "title")
        + _ansi(fill + chars["rt"], "border")
    )


def _route_display_name(route):
    return {
        "US_NATIVE": "Native 10-K / 10-Q",
        "US_NATIVE_ANNUAL": "Native 10-K annual only",
        "FOREIGN_20F": "Foreign 20-F annual only",
        "FOREIGN_40F": "Foreign 40-F annual only",
        "UNSUPPORTED": "Unsupported filing route",
    }.get(str(route or "").strip(), str(route or "Unknown"))


def _mode_display_name(route=None, use_arelle=None, save_xlsx=False, mode=None):
    if mode:
        return str(mode)
    output = "XLSX" if save_xlsx else "CSV"
    route_key = str(route or "").strip()
    if route_key in ("FOREIGN_20F", "FOREIGN_40F"):
        if use_arelle is None:
            return f"annual | foreign FY | {output}"
        arelle_state = "on" if use_arelle else "off"
        return f"annual | foreign XBRL + Arelle {arelle_state} | {output}"
    period_mode = "annual" if route_key == "US_NATIVE_ANNUAL" else "quarterly"
    if use_arelle is None:
        return f"{period_mode} | {output}"
    arelle_state = "on" if use_arelle else "off"
    return f"{period_mode} | Arelle {arelle_state} | {output}"


def _cache_display_name():
    local_on = os.environ.get("SEC_LOCAL_STORAGE", "").strip().lower() in (
        "1", "true", "yes", "on"
    )
    parts = [f"edgar local {'on' if local_on else 'off'}"]
    native_cache = globals().get("_NATIVE_EXTRACTION_CACHE_ENABLED", None)
    if native_cache is not None:
        parts.append(f"native extract {'on' if native_cache else 'off'}")
    final_cache = globals().get("_FINAL_PIVOT_CACHE_ENABLED", None)
    if final_cache is not None:
        parts.append(f"final pivot {'on' if final_cache else 'off'}")
    html_cache = globals().get("_PERSISTENT_HTML_CACHE_ENABLED", None)
    if html_cache is not None:
        parts.append(f"HTML parse {'on' if html_cache else 'off'}")
    fx_cache = globals().get("_FX_PERSISTENT_CACHE_ENABLED", None)
    if fx_cache is not None:
        parts.append(f"20-F {'on' if fx_cache else 'off'}")
    return "; ".join(parts)


def _route_style(route):
    route = str(route or "").strip()
    if route == "US_NATIVE":
        return "blue"
    if route == "US_NATIVE_ANNUAL":
        return "green"
    if route == "FOREIGN_20F":
        return "cyan"
    if route == "FOREIGN_40F":
        return "purple"
    return "yellow"


def _color_card_value(label, value, route, stream):
    text = str(value)
    if not _stream_supports_color(stream):
        return text
    if label == "Ticker":
        return _ansi(text, "title")
    if label == "Route":
        return _ansi(text, _route_style(route))
    if label == "Mode":
        return _ansi(text, "bright")
    if label == "Cache":
        style = "green" if " off" not in text.lower() else "yellow"
        return _ansi(text, style)
    if label == "Workers":
        return _ansi(text, "bright")
    if label == "Status":
        lower = text.lower()
        if "saved" in lower:
            return _ansi(text, "green")
        if "no data" in lower:
            return _ansi(text, "yellow")
        return _ansi(text, "orange")
    if label == "Warn":
        lower = text.lower()
        fail_match = re.search(r"(\d+)\s+fails?", lower)
        warn_match = re.search(r"(\d+)\s+warnings?", lower)
        retry_match = re.search(r"(\d+)\s+retries?", lower)
        fails = int(fail_match.group(1)) if fail_match else 0
        warnings = int(warn_match.group(1)) if warn_match else 0
        retries = int(retry_match.group(1)) if retry_match else 0
        if fails:
            return _ansi(text, "red")
        if warnings or retries:
            return _ansi(text, "yellow")
        return _ansi(text, "dim")
    if label == "Stats":
        return _ansi(text, "bright")
    return text


def _format_run_card(ticker, limit, route, workers, cache, stream=None, width=100,
                     attach_progress=False, status="Running", warn=None, stats=None,
                     company_name=None, cik=None, mode=None):
    stream = stream or sys.stdout
    width = max(48, int(width))
    rows = [
        ("Ticker", str(ticker).upper()),
        ("Company", str(company_name or "Unknown")),
        ("CIK", _format_cik_display(cik)),
        ("Limit", (f"{limit} annual filings" if str(route or "").strip() in ("FOREIGN_20F", "FOREIGN_40F", "US_NATIVE_ANNUAL") else f"{limit} filings")),
        ("Route", _route_display_name(route)),
        ("Mode", _mode_display_name(route=route, mode=mode)),
        ("Workers", str(workers)),
        ("Cache", str(cache)),
        ("Status", str(status)),
        ("Warn", str(warn or _format_warn_text(0, 0, 0))),
        ("Stats", str(stats or _format_stats_text(0, 0, "Starting"))),
    ]

    chars = _box_chars_for_stream(stream)
    title = " SEC Financials "
    top_fill = chars["h"] * max(0, width - len(title) - 3)
    if _stream_supports_color(stream):
        top = (
            _ansi(chars["tl"] + chars["h"], "border")
            + _ansi(title, "title")
            + _ansi(top_fill + chars["tr"], "border")
        )
    else:
        top = chars["tl"] + chars["h"] + title + top_fill + chars["tr"]
    bottom = _format_box_bottom(stream, width)
    left, right = chars["v"], chars["v"]

    inner = width - 4
    lines = [top]
    for label, value in rows:
        lines.append(_format_card_row(label, value, route, stream, width))
    lines.append(_format_progress_separator(stream, width) if attach_progress else bottom)
    return "\n".join(lines)


class _QuietConsoleStream:
    """Sink for third-party console writes while the progress bar owns output."""

    def __init__(self, real_stream):
        self._real_stream = real_stream
        self.encoding = getattr(real_stream, "encoding", "utf-8")
        self.errors = getattr(real_stream, "errors", "replace")

    def write(self, data):
        return len(data or "")

    def writelines(self, lines):
        return None

    def flush(self):
        return None

    def isatty(self):
        return False


class _ExternalConsoleSilencer:
    """Temporarily suppress library stdout/stderr/log warnings in progress mode.

    Some edgartools parsing paths write directly to stdout/stderr or logging,
    bypassing our normal print suppression and tearing through tqdm's one-line
    progress bar. This guard is intentionally UI-only: it does not catch
    exceptions or alter return values from the wrapped SEC calls.
    """

    _lock = threading.RLock()
    _depth = 0
    _saved_stdout = None
    _saved_stderr = None
    _saved_logging_disable = None

    def __init__(self, enabled=True):
        self.enabled = bool(enabled)

    def __enter__(self):
        if not self.enabled:
            return self
        with self._lock:
            if self.__class__._depth == 0:
                self.__class__._saved_stdout = sys.stdout
                self.__class__._saved_stderr = sys.stderr
                self.__class__._saved_logging_disable = logging.root.manager.disable
                sys.stdout = _QuietConsoleStream(sys.stdout)
                sys.stderr = _QuietConsoleStream(sys.stderr)
                logging.disable(logging.WARNING)
            self.__class__._depth += 1
        return self

    def __exit__(self, exc_type, exc, tb):
        if not self.enabled:
            return False
        with self._lock:
            self.__class__._depth = max(0, self.__class__._depth - 1)
            if self.__class__._depth == 0:
                if self.__class__._saved_stdout is not None:
                    sys.stdout = self.__class__._saved_stdout
                if self.__class__._saved_stderr is not None:
                    sys.stderr = self.__class__._saved_stderr
                if self.__class__._saved_logging_disable is not None:
                    logging.disable(self.__class__._saved_logging_disable)
                self.__class__._saved_stdout = None
                self.__class__._saved_stderr = None
                self.__class__._saved_logging_disable = None
        return False


class SECRateLimiter:
    """A thread-safe sliding-window rate limiter.

    Uses a monotonic clock and never sleeps while holding the mutex. That
    preserves the exact request ceiling while allowing other worker threads to
    make progress instead of queueing behind a sleeping thread.
    """
    def __init__(self, max_calls: int, period: float = 1.0):
        self.max_calls = max_calls
        self.period = period
        self.timestamps = deque()
        self.lock = threading.Lock()

    def wait(self):
        while True:
            with self.lock:
                now = time.monotonic()
                while self.timestamps and now - self.timestamps[0] >= self.period:
                    self.timestamps.popleft()

                if len(self.timestamps) < self.max_calls:
                    self.timestamps.append(now)
                    return

                sleep_time = max(0.0, self.period - (now - self.timestamps[0]))

            # Sleep outside the lock. Every waking thread re-checks the
            # window, so the maximum request rate remains unchanged.
            if sleep_time > 0:
                time.sleep(sleep_time)

sec_limiter = SECRateLimiter(max_calls=9, period=1.0)


# Reuse TCP/TLS connections for direct HTTP calls outside edgartools.
_SHARED_HTTP_CLIENT = httpx.Client(follow_redirects=True)
atexit.register(_SHARED_HTTP_CLIENT.close)

# Suppress warnings from pandas read_html
warnings.filterwarnings('ignore', category=FutureWarning)


# Optional lightweight progress mode for profiling/repeated development runs.
# Disabled by default so the normal console UI remains unchanged.
_PROGRESS_LIGHT_ENABLED = os.environ.get("SEC_PROGRESS_LIGHT", "").strip().lower() in (
    "1", "true", "yes", "on"
)

# ---------------------------------------------------------------------------
# Optional profiling instrumentation (disabled by default)
# ---------------------------------------------------------------------------
_PROFILE_ENABLED = os.environ.get("SEC_PROFILE", "").strip().lower() in (
    "1", "true", "yes", "on"
)
_PROFILE_TIMINGS: dict[str, float] = {}
_PROFILE_COUNTS: dict[str, int] = {}
_PROFILE_COUNTERS: dict[str, int] = {}

_DEBUG_OUTPUT_ENABLED = os.environ.get("SEC_DEBUG", "").strip().lower() in (
    "1", "true", "yes", "on"
)


def _debug_print(*args, **kwargs):
    """Debug-only console output. Keeps normal CSV/XLSX outputs unchanged."""
    if _DEBUG_OUTPUT_ENABLED:
        print(*args, **kwargs)


def _profile_count(name: str, amount: int = 1):
    """Increment a profile-only counter.  No-op unless SEC_PROFILE=1."""
    if not _PROFILE_ENABLED:
        return
    try:
        amount = int(amount)
    except Exception:
        amount = 1
    _PROFILE_COUNTERS[name] = _PROFILE_COUNTERS.get(name, 0) + amount


class _ProfileTimer:
    """Tiny no-op-by-default timer for high-level runtime profiling."""

    def __init__(self, name: str):
        self.name = name
        self.start = None

    def __enter__(self):
        if _PROFILE_ENABLED:
            self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        if _PROFILE_ENABLED and self.start is not None:
            elapsed = time.perf_counter() - self.start
            _PROFILE_TIMINGS[self.name] = _PROFILE_TIMINGS.get(self.name, 0.0) + elapsed
            _PROFILE_COUNTS[self.name] = _PROFILE_COUNTS.get(self.name, 0) + 1
        return False




def _profile_call(name, func, *args, **kwargs):
    """Profile a single call when SEC_PROFILE is enabled; otherwise direct."""
    with _ProfileTimer(name):
        return func(*args, **kwargs)

def _print_profile_report():
    if not _PROFILE_ENABLED:
        return
    if _PROFILE_TIMINGS:
        print("\n[Profile] Stage timing summary")
        for name, seconds in sorted(_PROFILE_TIMINGS.items(), key=lambda kv: kv[1], reverse=True):
            count = _PROFILE_COUNTS.get(name, 0)
            avg = seconds / count if count else seconds
            print(f"  {name:<45} {seconds:8.2f}s  calls={count:<5} avg={avg:.4f}s")
    if _PROFILE_COUNTERS:
        print("\n[Profile] Counter summary")
        for name, value in sorted(_PROFILE_COUNTERS.items(), key=lambda kv: kv[0]):
            print(f"  {name:<45} {value}")


atexit.register(_print_profile_report)

# ---------------------------------------------------------------------------
# First-run SEC identity setup
# ---------------------------------------------------------------------------
# The SEC requires automated clients to identify themselves with a real name
# and contact email.  Keep that contact identity local instead of hardcoding a
# maintainer's personal details into an open-source script.
_SEC_IDENTITY_INITIALIZED = False
_SEC_IDENTITY_VALUE = None
_SEC_IDENTITY_FILE_NAME = "sec_identity.json"
_SEC_IDENTITY_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _sec_identity_cache_path():
    """Return the identity file inside the script's shared cache directory."""
    cache_root = os.path.abspath(os.environ.get("SEC_CACHE_DIR", ".cache"))
    return os.path.join(cache_root, _SEC_IDENTITY_FILE_NAME)


def _normalize_sec_identity(name, email):
    """Validate and format the SEC contact identity used by edgartools."""
    name = re.sub(r"\s+", " ", str(name or "")).strip()
    email = re.sub(r"\s+", "", str(email or "")).strip()
    if len(name) < 2:
        raise ValueError("Enter your real name or organization name.")
    if not _SEC_IDENTITY_EMAIL_RE.match(email):
        raise ValueError("Enter a valid contact email address.")
    return name, email, f"{name} ({email})"


def _load_cached_sec_identity():
    path = _sec_identity_cache_path()
    try:
        with open(path, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
        if not isinstance(payload, dict):
            return None
        name, email, identity = _normalize_sec_identity(
            payload.get("name"), payload.get("email")
        )
        return name, email, identity
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return None


def _save_cached_sec_identity(name, email):
    """Atomically save the non-secret SEC contact identity under .cache/."""
    path = _sec_identity_cache_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp_path = f"{path}.{os.getpid()}.tmp"
    payload = {
        "version": 1,
        "name": name,
        "email": email,
    }
    try:
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
            fh.write("\n")
        try:
            os.chmod(tmp_path, 0o600)
        except OSError:
            pass
        os.replace(tmp_path, path)
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except OSError:
            pass
    return path


def _prompt_for_sec_identity():
    if not sys.stdin or not sys.stdin.isatty():
        raise RuntimeError(
            "No SEC identity is configured and this session is non-interactive. "
            "Set SEC_IDENTITY='Your Name (you@example.com)' or run the script "
            "once in an interactive terminal."
        )

    print("\n" + "=" * 64)
    print("SEC identity setup")
    print("=" * 64)
    print("The SEC requires automated downloads to include a real contact")
    print("name and email. This is not an account or password.")
    print("It will be saved locally and requested only once.\n")

    while True:
        try:
            name = input("Name or organization: ").strip()
            email = input("Contact email: ").strip()
            name, email, identity = _normalize_sec_identity(name, email)
        except (EOFError, KeyboardInterrupt):
            raise RuntimeError("SEC identity setup was cancelled.") from None
        except ValueError as exc:
            print(f"Invalid identity: {exc}\n")
            continue

        path = _save_cached_sec_identity(name, email)
        print(f"\nSEC identity saved to {path}\n")
        return name, email, identity


def _initialize_sec_identity():
    """Configure edgartools from env, cache, or a one-time terminal prompt."""
    global _SEC_IDENTITY_INITIALIZED, _SEC_IDENTITY_VALUE
    if _SEC_IDENTITY_INITIALIZED:
        return

    env_identity = os.environ.get("SEC_IDENTITY", "").strip()
    if env_identity:
        # Keep compatibility with edgartools' accepted free-form identity
        # string for CI, containers, and other non-interactive environments.
        set_identity(env_identity)
        _SEC_IDENTITY_VALUE = env_identity
        _SEC_IDENTITY_INITIALIZED = True
        return

    cached = _load_cached_sec_identity()
    if cached is None:
        cached = _prompt_for_sec_identity()

    _name, _email, identity = cached
    set_identity(identity)
    _SEC_IDENTITY_VALUE = identity
    _SEC_IDENTITY_INITIALIZED = True


def _sec_user_agent():
    """Return the configured identity for direct SEC HTTP requests."""
    _initialize_sec_identity()
    return _SEC_IDENTITY_VALUE


def _reset_cached_sec_identity():
    """Delete the saved identity so the next run displays setup again."""
    global _SEC_IDENTITY_INITIALIZED, _SEC_IDENTITY_VALUE
    path = _sec_identity_cache_path()
    try:
        os.remove(path)
        print(f"Removed saved SEC identity: {path}")
    except FileNotFoundError:
        print(f"No saved SEC identity found at: {path}")
    _SEC_IDENTITY_INITIALIZED = False
    _SEC_IDENTITY_VALUE = None


# Optional persistent on-disk cache of downloaded filings. SEC filings are
# immutable, so enabling this makes repeat runs substantially faster without
# changing parsed filing bytes. It remains opt-in to preserve the original
# live-network/index behavior exactly. Enable with SEC_LOCAL_STORAGE=1.
if os.environ.get("SEC_LOCAL_STORAGE", "").strip().lower() in ("1", "true", "yes", "on"):
    try:
        from edgar import use_local_storage
        use_local_storage()
        print("[Cache] edgartools local storage ON -- re-runs read cached filings from disk.")
    except Exception as _cache_err:
        print(f"[Cache] Local storage unavailable ({type(_cache_err).__name__}); using network.")

# ---------------------------------------------------------------------------
# Network Retry Logic for SEC EDGAR
# ---------------------------------------------------------------------------
def retry_sec_request(retries=3, delay=5):
    """
    Decorator to enforce global rate limits and retry on network failures.

    Catches the full httpx timeout family (ReadTimeout, ConnectTimeout,
    WriteTimeout, PoolTimeout) via the base TimeoutException, plus
    low-level connection/OS errors.  Uses exponential backoff so a
    struggling SEC server gets progressively more breathing room.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, retries + 1):
                sec_limiter.wait()
                try:
                    return func(*args, **kwargs)
                except httpx.TimeoutException as e:
                    # Covers ReadTimeout, ConnectTimeout, WriteTimeout, PoolTimeout
                    wait = delay * attempt   # exponential-ish backoff: 5s, 10s, 15s...
                    print(f"  [Timeout] {func.__name__} timed out (attempt {attempt}/{retries}). "
                          f"Retrying in {wait}s... ({type(e).__name__})")
                    if attempt == retries:
                        raise
                    time.sleep(wait)
                except httpx.HTTPStatusError as e:
                    if e.response.status_code == 429:
                        wait = delay * (2 ** attempt)   # aggressive backoff on 429
                        print(f"  [429 Throttled] {func.__name__} rate-limited. "
                              f"Backing off {wait}s (attempt {attempt}/{retries})...")
                        time.sleep(wait)
                        if attempt == retries:
                            raise
                    else:
                        raise
                except (ConnectionError, OSError) as e:
                    wait = delay * atte