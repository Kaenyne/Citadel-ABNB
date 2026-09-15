"""Parse a 13F information-table XML into a normalized holdings table.

Normalization handled here:
  * Namespace-agnostic XML parsing (the namespace URL varies by the
    SEC schema version used in a given filing).
  * Value units. Before the SEC's amended Form 13F took effect (filings
    on/after 2023-01-03), the <value> field is in THOUSANDS of dollars;
    after, it is in WHOLE dollars. We convert everything to whole
    dollars so quarters are comparable. See `THOUSANDS_CUTOFF`.
  * Aggregation by CUSIP. A single issuer/CUSIP can appear on multiple
    rows (one per otherManager); we sum shares and value so each CUSIP
    is one position.
"""
import re
from dataclasses import dataclass, field
from datetime import date
from xml.etree import ElementTree as ET

# Filings submitted on or after this date report value in whole dollars.
# Earlier filings report value in thousands. (SEC Form 13F amendments.)
THOUSANDS_CUTOFF = date(2023, 1, 3)


@dataclass
class Holding:
    cusip: str
    issuer: str
    title_of_class: str
    shares: float
    value_usd: float          # normalized to whole dollars
    is_share: bool            # True if sshPrnamtType == SH (vs PRN principal)


def _localname(tag: str) -> str:
    return tag.split("}")[-1]


def parse_information_table(xml_text: str, filing_date: str) -> list[Holding]:
    """Parse info-table XML -> list of Holding, aggregated by CUSIP.

    `filing_date` is 'YYYY-MM-DD' and decides value units.
    """
    fdate = date.fromisoformat(filing_date)
    in_thousands = fdate < THOUSANDS_CUTOFF

    root = ET.fromstring(xml_text.encode("utf-8"))
    agg: dict[str, Holding] = {}

    for it in root.iter():
        if _localname(it.tag) != "infoTable":
            continue
        fields: dict[str, str] = {}
        shares = 0.0
        sh_type = "SH"
        for child in it.iter():
            name = _localname(child.tag)
            text = (child.text or "").strip()
            if name in ("nameOfIssuer", "titleOfClass", "cusip"):
                fields[name] = text
            elif name == "sshPrnamt" and text:
                shares = float(text.replace(",", ""))
            elif name == "sshPrnamtType" and text:
                sh_type = text
            elif name == "value" and text:
                fields["value"] = text

        cusip = fields.get("cusip", "").strip().upper()
        if not cusip:
            continue
        raw_value = float(fields.get("value", "0").replace(",", ""))
        value_usd = raw_value * 1000.0 if in_thousands else raw_value

        if cusip in agg:
            h = agg[cusip]
            h.shares += shares
            h.value_usd += value_usd
        else:
            agg[cusip] = Holding(
                cusip=cusip,
                issuer=fields.get("nameOfIssuer", ""),
                title_of_class=fields.get("titleOfClass", ""),
                shares=shares,
                value_usd=value_usd,
                is_share=(sh_type == "SH"),
            )
    return sorted(agg.values(), key=lambda h: h.value_usd, reverse=True)


def portfolio_weights(holdings: list[Holding]) -> dict[str, float]:
    """CUSIP -> fraction of total reported 13F value (0..1)."""
    total = sum(h.value_usd for h in holdings)
    if total <= 0:
        return {}
    return {h.cusip: h.value_usd / total for h in holdings}
