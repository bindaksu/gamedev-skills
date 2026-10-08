# Forecast Model, Conversion-Value Schema and Incrementality

Read when building a forecast model from scratch, designing an iOS conversion-value schema, or planning an incrementality test.

## 1. Retention fit and LTV in Python

Fit on all observed days in log-log space (least squares), not on two points. Weight by cohort size if days have different sample sizes.

```python
import numpy as np

def fit_power_law(days, rates):
    """days: [1,3,7,14,30], rates: retention fractions. Returns (R1, b)."""
    x, y = np.log(days), np.log(rates)
    slope, intercept = np.polyfit(x, y, 1)
    return float(np.exp(intercept)), float(-slope)

def retention(d, r1, b):
    return 1.0 if d == 0 else r1 * d ** (-b)

def ltv(horizon, r1, b, arpdau_net, growth=0.0):
    """growth > 0 models ARPDAU rising with cohort age: arpdau * (1 + growth*ln(1+d))."""
    return sum(retention(d, r1, b) * arpdau_net * (1 + growth * np.log1p(d))
               for d in range(horizon + 1))

def payback_day(cpi, r1, b, arpdau_net, growth=0.0, max_day=1095):
    cum = 0.0
    for d in range(max_day + 1):
        cum += retention(d, r1, b) * arpdau_net * (1 + growth * np.log1p(d))
        if cum >= cpi:
            return d
    return None  # no payback inside max_day

def dau_forecast(installs_by_day, r1, b):
    """Convolution: DAU(t) = sum_s installs(s) * R(t - s)."""
    n = len(installs_by_day)
    return [sum(installs_by_day[s] * retention(t - s, r1, b) for s in range(t + 1))
            for t in range(n)]
```

Late-tail guard: after D90, switch to an exponential tail `R(d) = R(90) · e^(−λ(d−90))` fitted on D60–D180 data once you have it. Power laws over-predict the tail of content-limited games.

## 2. Forecast model structure

```
Inputs (per channel × geo × platform):
  spend curve: spend/day → installs/day (from measured spend steps)
  organic installs/day (baseline + uplift from paid, counted once)
  R1, b (and tail λ when available)
  ARPDAU_net(d) by cohort age
Calculations:
  cohorts[t] = paid installs[t] + organic installs[t]
  DAU[t] = Σ_s cohorts[s] · R(t − s)
  revenue_net[t] = Σ_s cohorts[s] · R(t − s) · ARPDAU_net(t − s)
  UA[t] = spend[t]
  contribution[t] = revenue_net[t] − UA[t] − variable costs[t]
  cash[t] = cash[t−1] + contribution[t] − fixed costs[t]
Outputs: DAU, revenue, contribution, cumulative cash, months of runway, by low/base/high case
```

Sanity checks: DAU/MAU between roughly 0.15 and 0.35 for most F2P genres (heuristic); forecast month-1 revenue within ±20% of the last soft-launch cohorts scaled by installs; organics never more than paid unless the game has featuring or virality evidence.

## 3. iOS conversion-value schema (SKAN / AdAttributionKit)

Goal: a coarse and fine value received within the first postback window that predicts D7 (or D30) value. As of 2026-10, configure both SKAN and AAK postbacks; Apple Ads postbacks use AAK from iOS 26.2 (verify current Apple documentation: https://developer.apple.com/app-store/ad-attribution).

Design steps:
1. From consented/Android users, build a model that predicts D7 net revenue from first-24–48 h signals (tutorial complete, levels reached, session count, first purchase, ad views).
2. Bucket predicted D7 value into the fine-value range (64 values) and into low/medium/high coarse values.
3. Reserve top buckets for any real purchase; most revenue concentrates in few users.
4. Validate: correlation between bucket mean and actual D7 value on a holdout; re-fit when monetization changes.
5. Version the schema; never change it mid-campaign test without annotating the date in reporting.

```
Fine value  │ Meaning                                  │ Predicted D7 net $
0           │ install only                             │ 0.00
1–15        │ engagement tiers (levels, sessions)      │ 0.01–0.30
16–40       │ ad-value tiers                           │ 0.30–1.50
41–63       │ purchase tiers (by revenue band)         │ 1.50+
Coarse      │ low = 0–15, medium = 16–40, high = 41–63
```

## 4. Incrementality test plan

| Method | When | Read |
| --- | --- | --- |
| Geo holdout (matched markets) | Channel-level truth, any platform | Difference-in-differences on installs and revenue vs matched control geos |
| Conversion lift (platform-run) | Meta, Google, TikTok studies | Platform randomizes exposure; check sample size and window |
| Ghost bids / PSA control | DSP and network tests | Requires partner support |
| Spend on/off pulses | Small channels | Weak; use only for direction |

Template:

```
QUESTION:     Is channel X incremental at spend $__/day?
DESIGN:       geo holdout, test geos __, control geos __ (matched on pre-period installs/revenue)
DURATION:     pre-period __ wk, test __ wk (≥ 2 × payback signal window)
METRIC:       incremental installs, incremental D7 net revenue
POWER:        minimum detectable lift __% given pre-period variance
DECISION:     iROAS = incremental revenue / spend; compare with attributed ROAS → calibration factor
```

Use the calibration factor (incremental ÷ attributed) per channel to adjust MMP/SKAN-attributed ROAS in the bidding sheet, and feed results into MMM as priors.

## 5. Soft-launch stage notes

- **Technical stage:** cheap, stable geos; goal is crash-free sessions, load time, server stability, funnel instrumentation. Do not read monetization here.
- **Retention stage:** add a tier-1 proxy (Canada, Australia, New Zealand are common English-language proxies; Nordics or Benelux for Europe). Hold UA mix constant across builds so retention changes are attributable to the build.
- **Monetization stage:** same proxies; enough payers to read conversion and ARPPU (hundreds of payers per variant, not dozens).
- **Scale stage:** small US/UK/DE spend steps to measure the spend curve and marginal CPI before global launch. Scopely used soft launch to pre-train network ML bidding (https://moloco.com/case-studies/scopely-monopoly-go).
- **Kill memo:** what was tested, which gate failed, what iterations were tried, what is reusable (systems, art, tech), and the team's next assignment. Supercell redeployed Squad Busters staff rather than laying them off (https://mobilegamer.biz/supercell-is-killing-squad-busters/).
