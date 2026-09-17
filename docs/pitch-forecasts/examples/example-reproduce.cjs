// Read-only reproduction of the September 11 research audit. Node.js, no packages.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

const rows = fs.readFileSync(path.join(__dirname, '../datasets/tgju_usd_irr_history.csv'), 'utf8')
  .trim().split(/\r?\n/).slice(1).map(line => {
    const fields = line.split(',');
    return { date: fields[0], day: Date.parse(fields[0]) / 86400000, close: Number(fields[4]) };
  });
assert(rows.every((r, i) => Number.isFinite(r.day) && r.close > 0 && (!i || r.day > rows[i - 1].day)));

function previous(day) {
  let low = 0, high = rows.length;
  while (low < high) {
    const mid = (low + high) >> 1;
    if (rows[mid].day <= day) low = mid + 1;
    else high = mid;
  }
  return low - 1;
}
function quantile(sorted, p) {
  const j = (sorted.length - 1) * p, i = Math.floor(j);
  return sorted[i] + (sorted[Math.ceil(j)] - sorted[i]) * (j - i);
}
function summary(values) {
  const sorted = [...values].sort((a, b) => a - b);
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  return {
    n: values.length, mean,
    sample_sd: Math.sqrt(values.reduce((s, v) => s + (v - mean) ** 2, 0) / (values.length - 1)),
    quantiles: Object.fromEntries([.05, .1, .25, .5, .75, .9, .95].map(p => [p, quantile(sorted, p)])),
    p_negative: values.filter(v => v < 0).length / values.length,
    p_above_250k_from_235k: values.filter(v => v > Math.log(250 / 235)).length / values.length,
  };
}
const all = [], crisisLog = [], crisisSimple = [];
for (const row of rows) {
  if (row.day + 111 > rows.at(-1).day) continue;
  const end = rows[previous(row.day + 111)];
  const ret = Math.log(end.close / row.close);
  all.push(ret);
  const j = previous(row.day - 90);
  if (j < 0) continue;
  const trailing = row.close / rows[j].close;
  const entry = { start: row.date, end: end.date, log_return: ret };
  if (Math.log(trailing) > .25) crisisLog.push(entry);
  if (trailing > 1.25) crisisSimple.push(entry);
}

// Abramowitz-Stegun erf approximation; sufficient for reported audit precision.
function phi(z) {
  const x = Math.abs(z) / Math.SQRT2, t = 1 / (1 + .3275911 * x);
  const erf = 1 - (((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t
    - .284496736) * t + .254829592) * t) * Math.exp(-x * x);
  return (1 + Math.sign(z) * erf) / 2;
}
const components = [[.48, .20, .20], [.17, .03, .09], [.20, -.10, .13], [.11, .55, .25], [.04, -.35, .25]];
function cdf(x, spot = 235000) {
  return components.reduce((s, [w, mu, sd]) => s + w * phi((Math.log(x / spot) - mu) / sd), 0);
}
function inverse(p) {
  let low = 10000, high = 1000000;
  for (let i = 0; i < 70; i++) {
    const mid = (low + high) / 2;
    if (cdf(mid) < p) low = mid;
    else high = mid;
  }
  return (low + high) / 2;
}
function density(x) {
  return components.reduce((s, [w, mu, sd]) => s + w * Math.exp(-.5 * ((Math.log(x / 235000) - mu) / sd) ** 2)
    / (x * sd * Math.sqrt(2 * Math.PI)), 0);
}
let mode = 150000;
for (let x = 150000; x <= 250000; x += 100) if (density(x) > density(mode)) mode = x;
const worst = [...crisisLog].sort((a, b) => a.log_return - b.log_return)[0];
const events = ['2026-04-08', '2026-06-17', '2026-02-27', '2018-08-01', '2023-02-20'].map(date => {
  const day = Date.parse(date) / 86400000, base = rows[previous(day)];
  const min = rows.filter(r => r.day > day && r.day <= day + 20).reduce((a, b) => a.close < b.close ? a : b);
  return { event: date, baseline: base.date, minimum_date: min.date, quote_change: min.close / base.close - 1, days_after_event: min.day - day };
});
const market = [.155, .215, .095, .305, .130, .040];
const marketTotal = market.reduce((a, b) => a + b);
const marketUpper = market.slice(2).reduce((a, b) => a + b);
console.log(JSON.stringify({
  inputs: { rows: rows.length, first: rows[0].date, last: rows.at(-1).date, spot_toman: 235000 },
  unconditional: summary(all),
  crisis_log_gt_025: summary(crisisLog.map(r => r.log_return)),
  crisis_simple_gt_25_percent: summary(crisisSimple.map(r => r.log_return)),
  period_sensitivity: Object.fromEntries([2018, 2020, 2023].map(y => [y, summary(crisisLog.filter(r => Number(r.start.slice(0, 4)) >= y).map(r => r.log_return))])),
  worst_crisis_window: { ...worst, quote_change: Math.expm1(worst.log_return) },
  event_minima_20_calendar_days: events,
  mixture: {
    percentiles_toman: Object.fromEntries([.05, .1, .25, .5, .75, .9, .95].map(p => [p, Math.round(inverse(p))])),
    p_below_150k: cdf(150000), p_above_250k: 1 - cdf(250000),
    p_150k_to_200k: cdf(200000) - cdf(150000), p_200k_to_250k: cdf(250000) - cdf(200000),
    p_above_400k: 1 - cdf(400000), in_range_density_mode_100_toman_grid: mode,
  },
  market: { sum: marketTotal, raw_upper_sum: marketUpper, lower_complement: 1 - market[0] - market[1],
    normalized_upper: marketUpper / marketTotal, lower_bracket_spread_complement: [1 - .16 - .22, 1 - .15 - .21] },
  sensitivities: {
    p_above_250k_spot_plus_5_percent: 1 - cdf(250000, 235000 * 1.05),
    six_percent_weekly_16_weeks: 235000 * 1.06 ** 16,
    september_30_spot_250k_weekly_rule: { median: 250000 * Math.exp(.10 * 92 / 111), p_above_250k: phi((.10 * 92 / 111) / (.26 * Math.sqrt(92 / 111))) },
    illustrative_separate_resolution_risk: .015 + .985 * cdf(150000),
  },
}, null, 2));
