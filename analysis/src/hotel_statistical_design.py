"""Transparent planning calculations; no empirical hotel significance claim.

Normal-approximation, equal-size, independent two-group mean comparison.
Recalculate using observed hotel-level residual variance and actual design.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import NormalDist

ROOT = Path(__file__).resolve().parents[2]


def hotels_per_group(relative_effect: float, residual_cv: float,
                     alpha: float = 0.05, power: float = 0.80) -> int:
    values = (relative_effect, residual_cv, alpha, power)
    if not all(math.isfinite(v) for v in values):
        raise ValueError('Inputs must be finite.')
    if relative_effect <= 0 or residual_cv <= 0:
        raise ValueError('Effect and residual coefficient of variation must be positive.')
    if not 0 < alpha < 1 or not 0.5 < power < 1:
        raise ValueError('Require 0<alpha<1 and 0.5<power<1.')
    normal = NormalDist()
    z = normal.inv_cdf(1-alpha/2) + normal.inv_cdf(power)
    return math.ceil(2 * z*z * (residual_cv/relative_effect)**2)


def minimum_detectable_effect(n_each: int, residual_cv: float,
                              alpha: float = 0.05, power: float = 0.80) -> float:
    if not isinstance(n_each, int) or isinstance(n_each, bool) or n_each < 2:
        raise ValueError('At least two hotels per group are required.')
    # Reuse validation without using the rounded result.
    hotels_per_group(0.1, residual_cv, alpha, power)
    normal = NormalDist()
    return (normal.inv_cdf(1-alpha/2) + normal.inv_cdf(power)) * math.sqrt(2/n_each) * residual_cv


def main() -> None:
    rows = []
    for cv in [0.5, 1.0, 1.5]:
        for effect in [0.05, 0.10, 0.20]:
            n = hotels_per_group(effect, cv)
            rows.append({'assumed_residual_cv': cv, 'target_relative_effect': effect,
                         'alpha_two_sided': 0.05, 'target_power': 0.80,
                         'independent_hotels_per_group': n, 'total_independent_hotels': 2*n})
    output = {
        'status': 'illustrative_design_not_observed_data_or_achieved_power',
        'method': 'Normal approximation for two equal independent groups; hotel-level residual outcome is the analysis unit.',
        'design_assumptions': ['equal residual variances', 'independent hotels after common shocks are addressed',
                               'one pre-specified primary test', 'no nonresponse or measurement error inflation',
                               'no causal identification supplied by the power calculation'],
        'requirements': ['Reestimate variance on valid production data.',
                         'Cluster repeated observations by hotel and account for shared operator/city/date shocks.',
                         'Use matching/weights and retain exits; more observations cannot remove selection bias.',
                         'Specify a financially meaningful minimum effect before inspecting outcomes.',
                         'For staggered adoption, use a cohort-aware design; simulate power for that design.',
                         'Population registry counts do not require a significance test; classification and coverage are the uncertainties.',
                         'Daily forecasts and many broker estimates do not create more independent company earnings events.'],
        'planning_grid': rows,
        'sources': ['https://www.itl.nist.gov/div898/handbook/eda/section3/eda353.htm',
                    'https://www.itl.nist.gov/div898/handbook/prc/section2/prc222.htm']}
    out = ROOT / 'data/processed/hotel_expanded_research/statistical_design.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(output, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'output': str(out), 'examples': [row for row in rows if row['assumed_residual_cv']==1]}, indent=2))


if __name__ == '__main__':
    main()
