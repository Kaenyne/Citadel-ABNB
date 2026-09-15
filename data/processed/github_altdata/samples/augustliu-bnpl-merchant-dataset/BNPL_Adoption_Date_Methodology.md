# BNPL Adoption Date Methodology

Generated at: 2026-08-09T21:28:28+00:00

## Operational Definition

BNPL adoption is defined as the earliest date on which a BNPL payment option was operationally available to consumers purchasing from the merchant.

The dataset does not treat partnership announcements, merchant-directory listings, contract dates, or the 2026 scraped directory date as adoption dates unless the evidence explicitly supports operational payment availability.

## Input

The script reads public merchants from `data/merchant_ownership/merchant_ownership_rows.json`, derived from `BNPL_Merchant_Ownership_List.xlsx`.

## Automated First-Pass Search Procedure

For each public merchant and each currently listed BNPL provider, the scraper checks:

1. Provider-specific URLs already captured in the merchant directory dataset.
2. Current merchant webpages inferred from available merchant URLs.
3. Generic payment/help/FAQ/financing paths on merchant domains.
4. Wayback CDX metadata for provider-specific URLs.

The automated process records evidence, errors, and inconclusive results. It does not interpret HTTP failures, JavaScript failures, or missing text on arbitrary pages as evidence of non-adoption.

## Evidence Hierarchy

Tier 1 evidence includes official merchant/provider operational launch pages and informative Wayback payment-page evidence.

Tier 2 evidence includes SEC filings, investor materials, and official social media.

Tier 3 evidence includes major business press.

Tier 4 evidence includes provider directories and other current-listing evidence. Tier 4 evidence can support current provider membership but is not sufficient by itself for adoption timing.

## Date Precision Rules

Allowed precision values are `exact_day`, `month`, `quarter`, `year`, `interval`, and `unknown`.

The automated first pass leaves timing as `unknown` unless source text or Wayback bounds support a narrower period. It never converts year-only or month-only information into artificial exact dates.

## Wayback Rules

Wayback absence is coded only when an archived payment/help page appears informative and enumerates payment methods without the provider. Arbitrary missing keywords on a homepage are not coded as confirmed absence.

## Multi-Platform Rule

The master dataset is merchant x provider. Merchant-level first BNPL adoption is calculated only from credible provider-level timing evidence. Rows with unknown timing remain preserved.

## Subsidiary-Parent Rule

Merchant-level BNPL adoption is kept distinct from public-parent treatment. `parent_treatment_eligible` is set conservatively and often requires manual review when brand-parent scope is ambiguous.

## Missing-Date Policy

If no reliable evidence is found, the treatment date remains blank with `date_precision = unknown` and `confidence = UNKNOWN`.

## Validation

The script validates duplicate merchant-provider rows, unsupported exact dates under unknown/year precision, invalid Wayback interval ordering, and missing evidence summaries for known timing.

## Summary

```json
{
  "retrieved_at": "2026-08-09T21:28:28+00:00",
  "total_public_merchants": 144,
  "merchant_provider_rows": 278,
  "evidence_log_rows": 1007,
  "manual_review_rows": 676,
  "confidence_distribution_provider_level": {
    "UNKNOWN": 278
  },
  "date_precision_distribution_provider_level": {
    "unknown": 278
  },
  "provider_distribution": {
    "Affirm": 38,
    "Afterpay": 39,
    "Klarna": 93,
    "Sezzle": 41,
    "Zip": 67
  },
  "merchant_first_confidence_distribution": {
    "UNKNOWN": 144
  },
  "merchant_first_precision_distribution": {
    "unknown": 144
  },
  "multi_platform_merchants": 81,
  "earlier_external_bnpl_rows": 69,
  "main_regression_eligible_merchants": 0
}
```

## Manual Review Procedure

Manual review should prioritize:

- high-value public parents;
- merchants with multiple current BNPL platforms;
- possible subsidiary-parent ambiguity;
- possible earlier external BNPL providers;
- unknown timing with current provider membership;
- any interval timing spanning multiple quarters.
