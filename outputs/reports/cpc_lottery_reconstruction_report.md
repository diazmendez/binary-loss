# CPC Lottery Reconstruction Report

Generated: 2026-05-05

## Executive Summary

CPC18 encodes 270 choice problems parametrically. 148 (54.8%) have both options as simple 2-outcome gambles and can be normalized exactly from CSV columns. The remaining 122 (45.2%) have multi-outcome lotteries whose exact structure is recoverable empirically from the Apay/Bpay columns. CPC15 is fully subsumed by CPC18 Sets 1–5. Normalization is NOT blocked.

## Lottery Model

```
Option X:
  prob pHx     → draw from lottery (LotNumX outcomes, EV = Hx, shape = LotShapeX)
  prob (1-pHx) → get Lx (fixed)
```

When LotNumX=1 and LotShapeX="-": lottery is degenerate → standard 2-outcome gamble.

## Problem-Level Complexity (270 GameIDs)

| Category | Problems | % |
|----------|----------|---|
| Both options simple (exact normalization) | 148 | 54.8% |
| Only Option A complex | 13 | 4.8% |
| Only Option B complex | 87 | 32.2% |
| Both options complex | 22 | 8.1% |

## Row-Level Coverage (694,500 rows)

| Category | Rows | % |
|----------|------|---|
| Both simple | 377,850 | 54.4% |
| At least one complex | 316,650 | 45.6% |

## LotNum Distribution (Problem Level)

### Option A
| LotNumA | Problems |
|---------|----------|
| 1 | 235 (87.0%) |
| 2 | 3 |
| 3 | 8 |
| 4 | 3 |
| 5 | 10 |
| 6 | 3 |
| 7 | 5 |
| 9 | 3 |

### Option B
| LotNumB | Problems |
|---------|----------|
| 1 | 161 (59.6%) |
| 2 | 6 |
| 3 | 29 |
| 4 | 7 |
| 5 | 20 |
| 6 | 6 |
| 7 | 22 |
| 8 | 2 |
| 9 | 17 |

## LotShape Distribution (Row Level)

### Option A
| LotShapeA | Rows |
|-----------|------|
| - | 589,500 (84.9%) |
| Symm | 48,000 |
| R-skew | 33,000 |
| L-skew | 24,000 |

### Option B
| LotShapeB | Rows |
|-----------|------|
| - | 416,850 (60.0%) |
| Symm | 167,200 |
| L-skew | 58,175 |
| R-skew | 52,275 |

## Both-Simple Problems by Set

| Set | Simple/Total | Notes |
|-----|-------------|-------|
| 1 | 27/30 | CPC15 Exp1 |
| 2 | 19/30 | CPC15 Exp2a |
| 3 | 21/30 | CPC15 Exp2b |
| 4 | 14/30 | CPC15 Exp3a |
| 5 | 16/30 | CPC15 Exp3b |
| 6 | 10/30 | CPC18 Exp1a |
| 7 | 15/30 | CPC18 Exp1b |
| 8 | 11/30 | CPC18 (UNCERTAIN) |
| 9 | 15/30 | CPC18 (UNCERTAIN) |

## Apay/Bpay Availability

- Apay: 694,500 / 694,500 (100% non-null)
- Bpay: 694,500 / 694,500 (100% non-null)
- Sufficient for empirical reconstruction of all 122 complex problems.

## Empirical Reconstruction Validation

| GameID | LotNum | Shape | Ha (EV) | Empirical EV | Unique Outcomes | Match |
|--------|--------|-------|---------|-------------|-----------------|-------|
| 173 | 7 (A) | Symm | 83 | 82.93 | 7 | ✓ |
| 161 | 5 (A) | R-skew | 0 | 0.07 | 5 | ✓ |
| 27 | 3 (B) | L-skew | 48 | ~47.4 | 3 | ✓ |

## CPC15 vs CPC18 Compatibility

- CPC18 Sets 1–5 = CPC15 data (verified: 30/30 GameIDs match with identical problem definitions).
- CPC15 has `RiskPay` column (analogous to Bpay for empirical reconstruction).
- CPC15 lacks `Apay`/`Bpay` but has `Payoff`, `Forgone`, `RiskPay`.
- **Recommendation**: Use CPC18 as sole source. It subsumes CPC15 with better columns.

## Recommendation

| Action | Status |
|--------|--------|
| Normalize 148 simple CPC18 problems (exact) | **TODO** |
| Reconstruct 122 complex CPC18 problems (empirical via Apay/Bpay) | **TODO** |
| Normalize CPC15 separately | **NOT NEEDED** (use CPC18 Sets 1–5) |
| Find Erev et al. generation algorithm | **OPTIONAL** (empirical method sufficient) |
| Include CPC in first paper | **YES** (with documented approximation for complex problems) |
